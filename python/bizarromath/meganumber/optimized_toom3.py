# bizarromath/meganumber/optimized_toom3.py

import time
import array
from typing import List
from .memory_pool import CPUMemoryPool
from .mega_number import MegaNumber

class OptimizedToom3:
    """
    HPC exponent and multiply with chunk-limb arrays,
    using schoolbook, karatsuba, or toom3 placeholders.

    This class can handle arbitrary array('Q') limb arrays—each 'Q' 
    slot is a chunk-limb of size MegaNumber._global_chunk_size bits.
    The memory pool reuses arrays to reduce allocations.

    Usage:
        pool = CPUMemoryPool()
        big_int = OptimizedToom3(pool)

        # Convert a Python int => HPC array-limbs
        a_arr = int_to_limbs(a_val)
        b_arr = int_to_limbs(b_val)

        # HPC multiply
        product = big_int.multiply(a_arr, b_arr)

        # HPC exponent
        power_arr = big_int.power(a_arr, exponent)
    """

    def __init__(self, pool: CPUMemoryPool):
        self.pool = pool

    def power(self, base: array.array, exponent: int) -> array.array:
        """
        Repeated-squaring. 'base' is an array of chunk-limbs from MegaNumber,
        'exponent' is a standard Python int for now.

        If exponent=0 => returns HPC array-limbs for '1'.
        """
        csize = MegaNumber._global_chunk_size
        if exponent == 0:
            return array.array('Q', [1])

        temp_base = array.array('Q', base)
        result = array.array('Q', [1])
        e = exponent

        while e > 0:
            # if odd => multiply result by temp_base
            if e & 1:
                result = self.multiply(result, temp_base)
            temp_base = self.multiply(temp_base, temp_base)
            e >>= 1

        return result

    def multiply(self, a: array.array, b: array.array) -> array.array:
        """
        Chooses schoolbook, karatsuba, or toom3 based on array-limb size.

        Args:
          a, b: HPC arrays of chunk-limbs (array('Q')), each slot is a csize-bit chunk.

        Returns:
          HPC array-limbs representing a*b in chunk-limb form.
        """
        csize = MegaNumber._global_chunk_size
        base = 1 << csize
        n = max(len(a), len(b))

        if n < 32:
            # small => schoolbook is fine
            t0 = time.perf_counter()
            out = self._schoolbook(a, b, csize, base)
            elapsed = time.perf_counter() - t0
            self.pool.stats.time_spent['schoolbook'] += elapsed
            return out
        elif n < 128:
            # moderate => karatsuba
            t0 = time.perf_counter()
            out = self._karatsuba(a, b, csize, base)
            elapsed = time.perf_counter() - t0
            self.pool.stats.time_spent['karatsuba'] += elapsed
            return out
        else:
            # large => fallback to _toom3
            t0 = time.perf_counter()
            out = self._toom3(a, b, csize, base)
            elapsed = time.perf_counter() - t0
            self.pool.stats.time_spent['toom3'] += elapsed
            return out

    def _schoolbook(self, A: array.array, B: array.array, csize: int, base: int) -> array.array:
        """
        Naive O(n^2) multiply for HPC chunk-limb arrays.
        Each array slot is csize bits, physically stored in a 64-bit element.
        """
        la, lb = len(A), len(B)
        out = array.array('Q', [0]*(la+lb))

        for i in range(la):
            carry = 0
            av = A[i]
            for j in range(lb):
                mul_val = av * B[j] + out[i+j] + carry
                out[i+j] = mul_val & (base - 1)
                carry = mul_val >> csize
            if carry:
                out[i+lb] = (out[i+lb] + carry) & ((1 << 64) - 1)

        # remove trailing zero limbs
        while len(out) > 1 and out[-1] == 0:
            out.pop()
        return out

    def _karatsuba(self, A: array.array, B: array.array, csize: int, base: int) -> array.array:
        """
        Karatsuba multiply for HPC chunk-limb arrays, O(n^1.585).

        Splits arrays into halves: 
            A0, A1 and B0, B1
        then uses:
            z0 = A0*B0
            z2 = A1*B1
            z1 = (A0+A1)*(B0+B1) - z0 - z2
        combined with shifts => final product.
        """
        n = max(len(A), len(B))
        if n < 32:
            return self._schoolbook(A, B, csize, base)

        half = n // 2
        A0, A1 = A[:half], A[half:]
        B0, B1 = B[:half], B[half:]

        z0 = self._karatsuba(A0, B0, csize, base)
        z2 = self._karatsuba(A1, B1, csize, base)
        sumA = self._add_arrays(A0, A1, csize, base)
        sumB = self._add_arrays(B0, B1, csize, base)

        z1 = self._karatsuba(sumA, sumB, csize, base)
        self._sub_in_place(z1, z0, csize, base)
        self._sub_in_place(z1, z2, csize, base)

        result = array.array('Q', [0]*(n*2))
        self._add_shifted(result, z0, 0, csize, base)
        self._add_shifted(result, z1, half, csize, base)
        self._add_shifted(result, z2, half*2, csize, base)

        while len(result) > 1 and result[-1] == 0:
            result.pop()
        return result

    def _toom3(self, A: array.array, B: array.array, csize: int, base: int) -> array.array:
        """
        Simplified placeholder for Toom-3 multiply, 
        often O(n^log3(2))~O(n^1.465).
        
        For brevity, we can just fallback to schoolbook or re-implement 
        partial toom-3 if you like. We'll just do:
        """
        # fallback:
        return self._schoolbook(A, B, csize, base)

    #
    # Helper HPC routines for array-limb manipulation:
    #

    def _add_arrays(self, A: array.array, B: array.array, csize: int, base: int) -> array.array:
        """
        Add two HPC arrays (same csize), return new HPC array result.
        """
        length = max(len(A), len(B))
        out = array.array('Q', [0]*length)
        carry = 0
        for i in range(length):
            av = A[i] if i < len(A) else 0
            bv = B[i] if i < len(B) else 0
            s_val = av + bv + carry
            out[i] = s_val & (base - 1)
            carry = s_val >> csize
        if carry:
            out.append(carry & (base - 1))
        return out

    def _sub_in_place(self, target: array.array, source: array.array, csize: int, base: int) -> None:
        """
        In-place subtract => target -= source, ignoring sign.
        target >= source assumed.
        """
        carry = 0
        for i in range(len(target)):
            sv = source[i] if i < len(source) else 0
            diff = target[i] - sv - carry
            if diff < 0:
                diff += base
                carry = 1
            else:
                carry = 0
            target[i] = diff & (base - 1)
        # trailing zeros remain as is.

    def _add_shifted(self, target: array.array, source: array.array, shift: int, csize: int, base: int) -> None:
        """
        Add 'source' into 'target' with an offset (shift).
        e.g. target[shift + i] += source[i].
        """
        carry = 0
        length = len(target)
        for i in range(len(source)):
            idx = i + shift
            if idx >= length:
                break
            s_val = target[idx] + source[i] + carry
            target[idx] = s_val & (base - 1)
            carry = s_val >> csize

        idx = shift + len(source)
        while carry and idx < length:
            s_val = target[idx] + carry
            target[idx] = s_val & (base - 1)
            carry = s_val >> csize
            idx += 1
        # if carry still remains beyond length, we typically 
        # rely on 'result' having enough space pre-allocated.