# bizarromath/tests/test_hpc_integration.py
import pytest
import random
from array import array
from bizarromath.meganumber.memory_pool import CPUMemoryPool
from bizarromath.meganumber.optimized_toom3 import OptimizedToom3
from bizarromath.meganumber.mega_number import MegaNumber

def test_pool_basic():
    pool = CPUMemoryPool()
    buf1 = pool.get_buffer(16)
    buf1[0] = 123
    pool.return_buffer(buf1)
    assert pool.stats.block_hits == 0
    assert pool.stats.cache_misses == 1

    buf2 = pool.get_buffer(16)
    # This time we should reuse the same size buffer => block_hits increments
    assert pool.stats.block_hits == 1
    pool.return_buffer(buf2)

def test_optimized_toom3_small():
    """
    Tests small HPC multiply & exponent via schoolbook logic.
    """
    pool = CPUMemoryPool()
    big_op = OptimizedToom3(pool)

    a_val = 12345
    b_val = 6789

    # convert to HPC limbs
    a_arr = int_to_limbs(a_val)
    b_arr = int_to_limbs(b_val)

    product_arr = big_op.multiply(a_arr, b_arr)
    # convert back to Python int
    from_bizarro = limbs_to_int(product_arr)
    assert from_bizarro == (a_val * b_val)

    # exponent test
    exponent = 10
    power_arr = big_op.power(a_arr, exponent)
    from_power = limbs_to_int(power_arr)
    assert from_power == (a_val ** exponent)

def test_optimized_toom3_medium():
    """
    Tests HPC multiply with moderate bit length => might trigger karatsuba.
    """
    pool = CPUMemoryPool()
    big_op = OptimizedToom3(pool)

    bits = 64  # borderline for karatsuba
    a_val = random.getrandbits(bits)
    b_val = random.getrandbits(bits)
    a_arr = int_to_limbs(a_val)
    b_arr = int_to_limbs(b_val)

    product_arr = big_op.multiply(a_arr, b_arr)
    from_bizarro = limbs_to_int(product_arr)
    assert from_bizarro == (a_val * b_val)

def test_optimized_toom3_large():
    """
    HPC multiply with bigger bits => might fallback to toom3 if implemented,
    or just schoolbook if _toom3 is a placeholder.
    """
    pool = CPUMemoryPool()
    big_op = OptimizedToom3(pool)

    bits = 256
    a_val = random.getrandbits(bits)
    b_val = random.getrandbits(bits)
    a_arr = int_to_limbs(a_val)
    b_arr = int_to_limbs(b_val)

    product_arr = big_op.multiply(a_arr, b_arr)
    from_bizarro = limbs_to_int(product_arr)
    assert from_bizarro == (a_val * b_val)

#
# Helpers from meganumber code to do HPC <-> Python int
#
def int_to_limbs(value: int) -> array.array:
    csize = MegaNumber._global_chunk_size or 64
    base = (1 << csize)
    out = array.array('Q', [])
    while value > 0:
        out.append(value & (base - 1))
        value >>= csize
    if not out:
        out.append(0)
    return out

def limbs_to_int(limbs: array.array) -> int:
    csize = MegaNumber._global_chunk_size or 64
    val = 0
    shift = 0
    for limb in limbs:
        val += (limb << shift)
        shift += csize
    return val