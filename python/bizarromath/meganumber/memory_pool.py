# bizarromath/meganumber/memory_pool.py

"""
Memory Pool for HPC chunk-limb arrays.

This module provides a CPUMemoryPool class that allocates and reuses
fixed-size arrays of chunk limbs (array('Q')) to minimize overhead
during HPC big-int operations (Karatsuba, Toom-3, etc.).
"""

import threading
import array
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class BlockMetrics:
    """
    Statistics about memory block usage.

    Attributes:
      block_hits:     how many times we've successfully reused an existing buffer
      cache_misses:   how many times we had to allocate a new buffer
      total_ops:      optional field for tracking total HPC ops (unused here)
      peak_memory:    tracks the max memory usage in 'chunks allocated'
      time_spent:     dictionary storing timings of various HPC phases
    """
    block_hits: int = 0
    cache_misses: int = 0
    total_ops: int = 0
    peak_memory: int = 0
    time_spent: Dict[str, float] = None

    def __post_init__(self):
        # Initialize time_spent dictionary if not provided
        if self.time_spent is None:
            self.time_spent = {
                'schoolbook': 0.0,
                'karatsuba': 0.0,
                'toom3': 0.0,
                'evaluation': 0.0,
                'interpolation': 0.0
            }

class CPUMemoryPool:
    """
    HPC memory pool for chunk-limb arrays, reusing buffers to reduce allocations.
    
    Typically, HPC big-int multiplication or exponent routines may need multiple
    temporary arrays('Q') to store partial results. Instead of constantly allocating
    new arrays, we keep a pool of them keyed by size for potential reuse.

    Attributes:
      _lock:         a threading.Lock() to ensure safe multi-thread usage
      pools:         dictionary mapping aligned sizes to a list of array('Q') objects
      stats:         collects usage metrics (block_hits, cache_misses, etc.)
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.pools: Dict[int, List[array.array]] = {}
        self.stats = BlockMetrics()

    def get_buffer(self, size: int) -> array.array:
        """
        Obtain an array('Q') buffer of at least 'size' length. If possible,
        reuse one from the pool to avoid new allocations.
        
        Args:
          size: the minimum number of 64-bit elements needed.

        Returns:
          An array('Q') object with 'aligned_size' elements, all zero-initialized.
        """
        aligned_size = (size + 7) & ~7
        with self._lock:
            # Check if we already have a buffer of this aligned size
            if aligned_size in self.pools and self.pools[aligned_size]:
                self.stats.block_hits += 1
                return self.pools[aligned_size].pop()

            self.stats.cache_misses += 1
            buf = array.array('Q', [0]*aligned_size)

            # Update peak memory usage stats
            cur_mem = sum(len(lst)*aligned_size for lst in self.pools.values())
            self.stats.peak_memory = max(self.stats.peak_memory, cur_mem)
            return buf

    def return_buffer(self, buf: array.array) -> None:
        """
        Return a previously obtained buffer to the pool for future reuse.
        
        Args:
          buf: the array('Q') object being returned.
        """
        size = (len(buf) + 7) & ~7
        with self._lock:
            if size not in self.pools:
                self.pools[size] = []
            self.pools[size].append(buf)