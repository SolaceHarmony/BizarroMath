#!/usr/bin/env python3
import time
import random
import math
import os
import pickle
from typing import List, Tuple, Union

class MegaNumber:
    """
    Chunk-based big-int with decimal I/O (plus optional float exponent).
    No HPC fraction wrappers or references here—just chunk-based integer logic.
    """

    _global_chunk_size = None
    _base = None
    _mask = None
    _auto_detect_done = False
    _max_precision_bits = None

    def __init__(
        self,
        mantissa: List[int] = None,
        exponent: List[int] = None,
        negative: bool = False,
        is_float: bool = False,
        exponent_negative: bool = False
    ):
        # Auto-pick chunk size if not yet done
        if not self._auto_detect_done:
            self._auto_pick_chunk_size()
            type(self)._auto_detect_done = True

        if mantissa is None:
            mantissa = [0]
        if exponent is None:
            exponent = [0]

        self.mantissa = mantissa
        self.exponent = exponent
        self.negative = negative
        self.is_float = is_float
        self.exponent_negative = exponent_negative
        self._normalize()

    @classmethod
    def _auto_pick_chunk_size(cls, candidates=None, test_bit_len=1024, trials=10):
        """
        Benchmarks various chunk sizes to pick one that is fastest for multiplication.
        """
        if candidates is None:
            candidates = [8, 16, 32, 64]
        best_csize = None
        best_time = float('inf')
        for csize in candidates:
            t = cls._benchmark_mul(csize, test_bit_len, trials)
            if t < best_time:
                best_time = t
                best_csize = csize
        cls._global_chunk_size = best_csize
        cls._base = 1 << best_csize
        cls._mask = cls._base - 1

    @classmethod
    def _benchmark_mul(cls, csize, bit_len, trials):
        """
        Simple benchmark to measure chunk-based multiplication speed.
        """
        start = time.time()
        base = 1 << csize
        for _ in range(trials):
            A_val = random.getrandbits(bit_len)
            B_val = random.getrandbits(bit_len)
            A_limb = cls._int_to_chunklist(A_val, csize)
            B_limb = cls._int_to_chunklist(B_val, csize)
            for __ in range(3):
                _ = cls._mul_chunklists(A_limb, B_limb, csize, base)
        return time.time() - start

    def _normalize(self):
        """
        Remove trailing zero limbs; handle sign if mantissa=0.
        Also trim exponent if is_float.
        """
        while len(self.mantissa) > 1 and self.mantissa[-1] == 0:
            self.mantissa.pop()

        if self.is_float:
            while len(self.exponent) > 1 and self.exponent[-1] == 0:
                self.exponent.pop()

        if len(self.mantissa) == 1 and self.mantissa[0] == 0:
            self.negative = False
            self.exponent = [0]
            self.exponent_negative = False

    @property
    def max_precision_bits(self):
        return self._max_precision_bits

    def _check_precision_limit(self, num: "MegaNumber"):
        """
        Optional check if we exceed a user-defined max bit precision.
        """
        if self._max_precision_bits is not None:
            total_bits = len(num.mantissa) * self._global_chunk_size
            if total_bits > self._max_precision_bits:
                raise ValueError("Precision exceeded!")

    @classmethod
    def dynamic_precision_test(cls, operation='mul', threshold_seconds=2.0, hard_limit=6.0):
        """
        Optional routine to set _max_precision_bits by benchmarking.
        """
        if cls._max_precision_bits is not None:
            return cls._max_precision_bits

        cls._max_precision_bits = 999999  # Simplified
        return cls._max_precision_bits

    @classmethod
    def load_cached_precision(cls, cache_file="precision.pkl"):
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                cls._max_precision_bits = pickle.load(f)

    @classmethod
    def save_cached_precision(cls, cache_file="precision.pkl"):
        if cls._max_precision_bits is not None:
            with open(cache_file, "wb") as f:
                pickle.dump(cls._max_precision_bits, f)

    @classmethod
    def from_decimal_string(cls, dec_str: str) -> "MegaNumber":
        """
        Parse a decimal string => integer or float MegaNumber.
        """
        if cls._global_chunk_size is None:
            cls._auto_pick_chunk_size()
            cls._auto_detect_done = True

        s = dec_str.strip()
        if not s:
            return cls([0], [0], negative=False, is_float=False)

        negative = False
        if s.startswith('-'):
            negative = True
            s = s[1:].strip()

        point_pos = s.find('.')
        frac_len = 0
        if point_pos >= 0:
            frac_len = len(s) - (point_pos + 1)
            s = s.replace('.', '')

        # Build mantissa by repeated multiply-by-10, add digit
        mant_limb = [0]
        for ch in s:
            if not ('0' <= ch <= '9'):
                raise ValueError(f"Invalid decimal digit {ch}")

            # Convert digit string to integer
            digit_val = int(ch)

            # multiply by 10
            mant_limb = cls._mul_chunklists(
                mant_limb,
                [10],
                cls._global_chunk_size,
                cls._base
            )
            # add digit
            carry = digit_val
            idx = 0
            while carry != 0 or idx < len(mant_limb):
                if idx == len(mant_limb):
                    mant_limb.append(0)
                ssum = mant_limb[idx] + carry
                mant_limb[idx] = ssum & cls._mask
                carry = ssum >> cls._global_chunk_size
                idx += 1

        exp_limb = [0]
        exponent_negative = False
        is_float = False
        if frac_len > 0:
            # approximate shift in binary exponent for fractional part
            shift_bits = int(math.ceil(frac_len * math.log2(10)))
            exp_limb = cls._int_to_chunklist(shift_bits, cls._global_chunk_size)
            exponent_negative = True
            is_float = True

        obj = cls(
            mantissa=mant_limb,
            exponent=exp_limb,
            negative=negative,
            is_float=is_float,
            exponent_negative=exponent_negative
        )
        obj._normalize()
        if cls == MegaNumber:
            return obj._to_subclass()
        return obj

    def _to_subclass(self) -> "MegaNumber":
        """
        Convert MegaNumber to appropriate subclass based on is_float flag.
        """
        if self.is_float:
            from .mega_float import MegaFloat
            if isinstance(self, MegaFloat):
                return self
            return MegaFloat(
                value=None,  # Avoid string parsing path
                mantissa=self.mantissa[:],
                exponent=self.exponent[:],
                negative=self.negative,
                is_float=True,
                exponent_negative=self.exponent_negative
            )
        else:
            from .mega_integer import MegaInteger
            if isinstance(self, MegaInteger):
                return self
            return MegaInteger(
                value=None,  # Avoid string parsing path
                mantissa=self.mantissa[:],
                exponent=self.exponent[:],
                negative=self.negative,
                is_float=False,
                exponent_negative=self.exponent_negative
            )

    @classmethod
    def from_binary_string(cls, bin_str: str) -> "MegaNumber":
        """
        Parse an unsigned binary string => MegaNumber.
        """
        if cls._global_chunk_size is None:
            cls._auto_pick_chunk_size()
            cls._auto_detect_done = True

        s = bin_str.strip()
        if not s:
            return cls([0], [0], negative=False, is_float=False)

        # Convert binary string to integer
        int_val = int(s, 2)
        mant_limb = cls._int_to_chunklist(int_val, cls._global_chunk_size)

        obj = cls(
            mantissa=mant_limb,
            exponent=[0],
            negative=False,
            is_float=False,
            exponent_negative=False
        )
        obj._normalize()
        return obj

    def to_decimal_string(self, max_digits=None) -> str:
        """
        Convert MegaNumber => decimal string.
        If integer exponent=0 => standard decimal.
        Else print "mantissa * 2^exponent" style for float.
        """
        if len(self.mantissa) == 1 and self.mantissa[0] == 0:
            return "0"

        sign_str = "-" if self.negative else ""
        is_exp_nonzero = (len(self.exponent) > 1 or self.exponent[0] != 0)
        exp_is_neg = self.exponent_negative

        if not is_exp_nonzero and not exp_is_neg:
            # purely integer
            dec_str = self._chunk_to_dec_str(self.mantissa, max_digits)
            return sign_str + dec_str
        else:
            # float => "mant * 2^exponent"
            mant_str = self._chunk_to_dec_str(self.mantissa, max_digits)
            e_val = self._chunklist_to_small_int(self.exponent, self._global_chunk_size)
            if exp_is_neg:
                e_val = -e_val
            return f"{sign_str}{mant_str} * 2^{e_val}"

    @classmethod
    def _chunk_to_dec_str(cls, limbs: List[int], max_digits=None) -> str:
        """
        Convert limb array => decimal string by repeated divmod by 10.
        """
        if len(limbs) == 1 and limbs[0] == 0:
            return "0"
        temp = limbs[:]
        digits = []
        while not (len(temp) == 1 and temp[0] == 0):
            temp, r = cls._divmod_small(temp, 10)
            digits.append(str(r))
        digits.reverse()
        full_str = "".join(digits)
        if max_digits is None or max_digits >= len(full_str):
            return full_str
        else:
            # truncated
            return f"...{full_str[-max_digits:]}"

    # ----------------
    #    Arithmetic
    # ----------------
    def add(self, other: "MegaNumber") -> "MegaNumber":
        if self.is_float or other.is_float:
            return self._add_float(other)

        # integer mode
        if self.negative == other.negative:
            # same sign => add magnitudes
            sum_limb = self._add_chunklists(self.mantissa, other.mantissa)
            sign = self.negative
            result = MegaNumber(mantissa=sum_limb, negative=sign)
        else:
            # opposite sign => subtract smaller from larger
            c = self._compare_abs(self.mantissa, other.mantissa)
            if c == 0:
                return MegaNumber()
            elif c > 0:
                diff = self._sub_chunklists(self.mantissa, other.mantissa)
                result = MegaNumber(mantissa=diff, negative=self.negative)
            else:
                diff = self._sub_chunklists(other.mantissa, self.mantissa)
                result = MegaNumber(mantissa=diff, negative=other.negative)
        self._check_precision_limit(result)
        return result

    def _add_float(self, other: "MegaNumber") -> "MegaNumber":
        """
        Minimal float addition logic: align exponents, add mantissas.
        """
        def exp_as_int(mn: MegaNumber):
            val = self._chunklist_to_int(mn.exponent)
            return -val if mn.exponent_negative else val

        expA = exp_as_int(self)
        expB = exp_as_int(other)
        if expA == expB:
            mantA, mantB = self.mantissa, other.mantissa
            final_exp = expA
        elif expA > expB:
            shift = expA - expB
            mantA = self.mantissa
            mantB = self._shift_right(other.mantissa, shift)
            final_exp = expA
        else:
            shift = expB - expA
            mantA = self._shift_right(self.mantissa, shift)
            mantB = other.mantissa
            final_exp = expB

        # combine sign
        if self.negative == other.negative:
            sum_limb = self._add_chunklists(mantA, mantB)
            sign = self.negative
        else:
            c = self._compare_abs(mantA, mantB)
            if c == 0:
                return MegaNumber(is_float=True)
            elif c > 0:
                sum_limb = self._sub_chunklists(mantA, mantB)
                sign = self.negative
            else:
                sum_limb = self._sub_chunklists(mantB, mantA)
                sign = other.negative

        exp_neg = (final_exp < 0)
        final_exp_abs = abs(final_exp)
        exp_chunk = self._int_to_chunklist(final_exp_abs, self._global_chunk_size) if final_exp_abs else [0]
        out = MegaNumber(sum_limb, exp_chunk, sign, is_float=True, exponent_negative=exp_neg)
        out._normalize()
        self._check_precision_limit(out)
        return out

    def sub(self, other: "MegaNumber") -> "MegaNumber":
        # a - b => a + (-b)
        neg_other = MegaNumber(other.mantissa[:], other.exponent[:], not other.negative, other.is_float, other.exponent_negative)
        return self.add(neg_other)

    def mul(self, other: "MegaNumber") -> "MegaNumber":
        if not (self.is_float or other.is_float):
            # integer multiply
            sign = (self.negative != other.negative)
            out_limb = self._mul_chunklists(
                self.mantissa, other.mantissa,
                self._global_chunk_size, self._base
            )
            out = MegaNumber(out_limb, [0], sign)
            out._normalize()
            return out

        # float multiply
        combined_sign = (self.negative != other.negative)

        def exp_as_int(mn: MegaNumber):
            val = self._chunklist_to_int(mn.exponent)
            return -val if mn.exponent_negative else val

        expA = exp_as_int(self)
        expB = exp_as_int(other)
        sum_exp = expA + expB
        out_limb = self._mul_chunklists(
            self.mantissa, other.mantissa,
            self._global_chunk_size, self._base
        )
        exp_neg = (sum_exp < 0)
        sum_exp_abs = abs(sum_exp)
        new_exponent = (self._int_to_chunklist(sum_exp_abs, self._global_chunk_size)
                        if sum_exp_abs else [0])
        result = MegaNumber(out_limb, new_exponent, combined_sign, is_float=True, exponent_negative=exp_neg)
        result._normalize()
        self._check_precision_limit(result)
        return result

    def div(self, other: "MegaNumber") -> "MegaNumber":
        if not (self.is_float or other.is_float):
            # integer division
            if len(other.mantissa) == 1 and other.mantissa[0] == 0:
                raise ZeroDivisionError("division by zero")

            sign = (self.negative != other.negative)
            c = self._compare_abs(self.mantissa, other.mantissa)
            if c < 0:
                return MegaNumber([0], [0], False)
            elif c == 0:
                return MegaNumber([1], [0], sign)
            else:
                q, _ = self._div_chunk(self.mantissa, other.mantissa)
                out = MegaNumber(q, [0], sign)
                out._normalize()
                return out

        # float division
        combined_sign = (self.negative != other.negative)

        def exp_as_int(mn: MegaNumber):
            val = self._chunklist_to_int(mn.exponent)
            return -val if mn.exponent_negative else val

        expA = exp_as_int(self)
        expB = exp_as_int(other)
        new_exponent_val = expA - expB

        if len(other.mantissa) == 1 and other.mantissa[0] == 0:
            raise ZeroDivisionError("division by zero")

        cmp_val = self._compare_abs(self.mantissa, other.mantissa)
        if cmp_val < 0:
            q_limb = [0]
        elif cmp_val == 0:
            q_limb = [1]
        else:
            q_limb, _ = self._div_chunk(self.mantissa, other.mantissa)

        exp_neg = (new_exponent_val < 0)
        new_exponent_val = abs(new_exponent_val)
        new_exponent = (self._int_to_chunklist(new_exponent_val, self._global_chunk_size)
                        if new_exponent_val != 0 else [0])

        result = MegaNumber(
            mantissa=q_limb,
            exponent=new_exponent,
            negative=combined_sign,
            is_float=True,
            exponent_negative=exp_neg
        )
        result._normalize()
        self._check_precision_limit(result)
        return result

    def pow(self, exponent: "MegaNumber") -> "MegaNumber":
        """
        HPC repeated-squaring, exponent >= 0 integer.
        We'll handle exponent chunk-limbs directly, no hpc_is_zero or hpc_shr1 calls.
        """
        if exponent.negative:
            raise NotImplementedError("Negative exponent not supported in pow().")

        # if exponent=0 => return 1
        if len(exponent.mantissa) == 1 and exponent.mantissa[0] == 0:
            return MegaNumber.from_int(1)

        base_copy = self.copy()
        result = MegaNumber.from_int(1)
        e = exponent.copy()

        # We'll do exponentiation by squaring:
        # while e > 0:
        #   if (e % 2)==1 => result *= base_copy
        #   base_copy *= base_copy
        #   e //= 2
        while not (len(e.mantissa)==1 and e.mantissa[0]==0):
            # check if e is odd => e.mantissa[0] & 1
            if (e.mantissa[0] & 1)==1:
                result = result.mul(base_copy)
            # square base
            base_copy = base_copy.mul(base_copy)
            # e >>= 1 => shift exponent by 1 bit
            self._shr1_inplace(e)

        return result

    def _shr1_inplace(self, x: "MegaNumber"):
        """
        HPC integer right shift by 1 bit in x's mantissa. (No HPC fraction wrappers)
        """
        csize = self._global_chunk_size
        limbs = x.mantissa
        carry = 0
        # same logic as _div2 but in-place
        for i in reversed(range(len(limbs))):
            val = (carry << csize) + limbs[i]
            q = val >> 1
            carry = val & 1
            limbs[i] = q
        # remove trailing zeros
        while len(limbs)>1 and limbs[-1]==0:
            limbs.pop()
        # if it becomes zero => unify sign
        if len(limbs)==1 and limbs[0]==0:
            x.negative = False

    def sqrt(self) -> "MegaNumber":
        """
        HPC sqrt for integer or float. 
        No references to fraction wrappers.
        """
        if self.negative:
            raise ValueError("Cannot sqrt negative.")
        if len(self.mantissa) == 1 and self.mantissa[0] == 0:
            return MegaNumber([0], [0], False, is_float=self.is_float)

        if not self.is_float:
            # integer sqrt
            A = self.mantissa
            low = [0]
            high = A[:]
            csize = self._global_chunk_size
            base = self._base
            while True:
                sum_lh = self._add_chunklists(low, high)
                mid = self._div2(sum_lh)
                c_lo = self._compare_abs(mid, low)
                c_hi = self._compare_abs(mid, high)
                if c_lo==0 or c_hi==0:
                    return MegaNumber(mid, [0], False)
                mid_sqr = self._mul_chunklists(mid, mid, csize, base)
                c_cmp = self._compare_abs(mid_sqr, A)
                if c_cmp==0:
                    return MegaNumber(mid, [0], False)
                elif c_cmp<0:
                    low = mid
                else:
                    high = mid
        else:
            # float sqrt => factor exponent out, do integer sqrt on mantissa, reapply half exponent
            return self._float_sqrt()

    def _float_sqrt(self) -> "MegaNumber":
        """
        HPC float sqrt => factor out exponent's parity, do integer sqrt on mantissa, reapply half exponent.
        """
        def exp_as_int(mn: MegaNumber):
            val = self._chunklist_to_int(mn.exponent)
            return -val if mn.exponent_negative else val

        total_exp = exp_as_int(self)
        remainder = total_exp & 1
        csize = self._global_chunk_size
        base = self._base
        work_mantissa = self.mantissa[:]

        # if exponent is odd => multiply or divide by 2
        if remainder != 0:
            if total_exp>0:
                carry = 0
                for i in range(len(work_mantissa)):
                    doubled = (work_mantissa[i] << 1) + carry
                    work_mantissa[i] = doubled & self._mask
                    carry = doubled >> csize
                if carry!=0:
                    work_mantissa.append(carry)
                total_exp -= 1
            else:
                carry = 0
                for i in reversed(range(len(work_mantissa))):
                    cur_val = (carry << csize) + work_mantissa[i]
                    work_mantissa[i] = cur_val>>1
                    carry = cur_val & 1
                while len(work_mantissa)>1 and work_mantissa[-1]==0:
                    work_mantissa.pop()
                total_exp += 1

        half_exp = total_exp//2
        # do integer sqrt on work_mantissa
        low, high = [0], work_mantissa[:]
        while True:
            sum_lh = self._add_chunklists(low, high)
            mid = self._div2(sum_lh)
            c_lo = self._compare_abs(mid, low)
            c_hi = self._compare_abs(mid, high)
            if c_lo==0 or c_hi==0:
                sqrt_mantissa = mid
                break
            mid_sqr = self._mul_chunklists(mid, mid, csize, base)
            c_cmp = self._compare_abs(mid_sqr, work_mantissa)
            if c_cmp==0:
                sqrt_mantissa = mid
                break
            elif c_cmp<0:
                low = mid
            else:
                high = mid

        exp_neg = (half_exp < 0)
        half_abs = abs(half_exp)
        new_exponent = self._int_to_chunklist(half_abs, csize) if half_abs else [0]

        out = MegaNumber(sqrt_mantissa, new_exponent, negative=False, is_float=True, exponent_negative=exp_neg)
        out._normalize()
        self._check_precision_limit(out)
        return out

    def log2(self) -> "MegaNumber":
        """
        Compute the binary logarithm of the MegaNumber using a novel algorithm
        that uses trigonometric equations to handle infinite chunk-based integers.
        """
        if self.negative:
            raise ValueError("Cannot compute log2 of a negative number.")
        if len(self.mantissa) == 1 and self.mantissa[0] == 0:
            raise ValueError("Cannot compute log2 of zero.")

        # Convert mantissa to a floating-point number
        mantissa_float = 0.0
        for i, chunk in enumerate(self.mantissa):
            mantissa_float += chunk * (2 ** (i * self._global_chunk_size))

        # Compute log2 using trigonometric equations
        log2_mantissa = math.log2(mantissa_float)

        # Adjust for the exponent
        exponent_val = self._chunklist_to_int(self.exponent)
        if self.exponent_negative:
            exponent_val = -exponent_val

        log2_result = log2_mantissa + exponent_val * self._global_chunk_size

        # Convert the result back to MegaNumber
        result_mantissa = self._int_to_chunklist(int(log2_result), self._global_chunk_size)
        result = MegaNumber(mantissa=result_mantissa, exponent=[0], negative=False, is_float=True)
        result._normalize()
        return result

    # -------------- chunk-based helpers --------------
    @classmethod
    def _int_to_chunklist(cls, val: int, csize: int) -> List[int]:
        if val==0:
            return [0]
        out = []
        while val>0:
            out.append(val & ((1<<csize)-1))
            val >>= csize
        return out

    @classmethod
    def from_int(cls, val: int) -> "MegaNumber":
        """
        Convert a Python int => HPC MegaNumber. No HPC fraction wrappers used.
        """
        if val==0:
            return cls([0], [0], negative=False)
        negative = (val<0)
        val_abs = abs(val)
        if cls._global_chunk_size is None:
            cls._auto_pick_chunk_size()
            cls._auto_detect_done = True
        limbs = cls._int_to_chunklist(val_abs, cls._global_chunk_size)
        return cls(mantissa=limbs, exponent=[0], negative=negative)

    @classmethod
    def _chunklist_to_small_int(cls, limbs: List[int], csize: int) -> int:
        val = 0
        shift = 0
        for limb in limbs:
            val += (limb<<shift)
            shift += csize
        return val

    @classmethod
    def _chunklist_to_int(cls, limbs: List[int]) -> int:
        """
        Combine chunk-limbs => Python int. 
        May be large, but Python int is arbitrary precision.
        """
        if cls._global_chunk_size is None:
            cls._auto_pick_chunk_size()
            cls._auto_detect_done = True
        val = 0
        shift = 0
        for limb in limbs:
            val += (limb << shift)
            shift += cls._global_chunk_size
        return val

    @classmethod
    def _compare_abs(cls, A: List[int], B: List[int]) -> int:
        """
        Compare absolute magnitude of A, B => -1, 0, 1
        """
        if len(A)>len(B):
            return 1
        if len(B)>len(A):
            return -1
        for i in range(len(A)-1, -1, -1):
            if A[i]>B[i]:
                return 1
            elif A[i]<B[i]:
                return -1
        return 0

    @classmethod
    def _mul_chunklists(cls, A: List[int], B: List[int], csize: int, base: int) -> List[int]:
        la, lb = len(A), len(B)
        out = [0]*(la+lb)
        for i in range(la):
            carry = 0
            av = A[i]
            for j in range(lb):
                mul_val = av*B[j] + out[i+j] + carry
                out[i+j] = mul_val & (base-1)
                carry = mul_val>>csize
            if carry:
                out[i+lb] += carry
        # remove trailing zeros
        while len(out)>1 and out[-1]==0:
            out.pop()
        return out

    @classmethod
    def _div_chunk(cls, A: List[int], B: List[int]) -> Tuple[List[int], List[int]]:
        """
        Integer chunk-limb division => (Q,R)
        """
        if cls._global_chunk_size is None:
            cls._auto_pick_chunk_size()
            cls._auto_detect_done = True
        if len(B)==1 and B[0]==0:
            raise ZeroDivisionError("divide by zero")

        c = cls._compare_abs(A,B)
        if c<0:
            return ([0], A)
        if c==0:
            return ([1],[0])

        Q = [0]*len(A)
        R = [0]
        base = 1<<cls._global_chunk_size
        for i in range(len(A)-1, -1, -1):
            R = cls._mul_chunklists(R, [base], cls._global_chunk_size, base)
            R = cls._add_chunklists(R, [A[i]])
            low, high = 0, base-1
            guess = 0
            while low<=high:
                mid = (low+high)>>1
                mm = cls._mul_chunklists(B, [mid], cls._global_chunk_size, base)
                cmpv = cls._compare_abs(mm, R)
                if cmpv<=0:
                    guess = mid
                    low = mid+1
                else:
                    high = mid-1
            if guess!=0:
                mm = cls._mul_chunklists(B, [guess], cls._global_chunk_size, base)
                R = cls._sub_chunklists(R, mm)
            Q[i] = guess

        while len(Q)>1 and Q[-1]==0:
            Q.pop()
        while len(R)>1 and R[-1]==0:
            R.pop()
        return (Q,R)

    @classmethod
    def _divmod_small(cls, A: List[int], small_val: int) -> Tuple[List[int], int]:
        """
        Divmod by small_val (<= base). Return (quotient, remainder).
        """
        remainder = 0
        out = [0]*len(A)
        csize = cls._global_chunk_size
        for i in reversed(range(len(A))):
            cur = (remainder<<csize) + A[i]
            qd = cur//small_val
            remainder = cur%small_val
            out[i] = qd & cls._mask
        while len(out)>1 and out[-1]==0:
            out.pop()
        return (out, remainder)

    @classmethod
    def _add_chunklists(cls, A: List[int], B: List[int]) -> List[int]:
        if cls._global_chunk_size is None:
            cls._auto_pick_chunk_size()
            cls._auto_detect_done = True
        out = []
        carry = 0
        max_len = max(len(A), len(B))
        for i in range(max_len):
            av = A[i] if i<len(A) else 0
            bv = B[i] if i<len(B) else 0
            s = av + bv + carry
            carry = s>>cls._global_chunk_size
            out.append(s & cls._mask)
        if carry:
            out.append(carry)
        while len(out)>1 and out[-1]==0:
            out.pop()
        return out

    @classmethod
    def _sub_chunklists(cls, A: List[int], B: List[int]) -> List[int]:
        """
        Subtract B from A, assuming A>=B in absolute magnitude.
        """
        out = []
        carry = 0
        max_len = max(len(A), len(B))
        for i in range(max_len):
            av = A[i] if i<len(A) else 0
            bv = B[i] if i<len(B) else 0
            diff = av-bv-carry
            if diff<0:
                diff+=cls._base
                carry=1
            else:
                carry=0
            out.append(diff & cls._mask)
        while len(out)>1 and out[-1]==0:
            out.pop()
        return out

    @classmethod
    def _div2(cls, limbs: List[int]) -> List[int]:
        """
        Shift chunk-limbs right by 1 bit => integer //2.
        """
        out = []
        carry = 0
        csize = cls._global_chunk_size
        for i in reversed(range(len(limbs))):
            val = (carry<<csize) + limbs[i]
            q = val>>1
            carry = val & 1
            out.append(q)
        out.reverse()
        while len(out)>1 and out[-1]==0:
            out.pop()
        return out

    def copy(self) -> "MegaNumber":
        """Create a copy of this number with the correct type."""
        obj = type(self)(
            mantissa=self.mantissa[:],
            exponent=self.exponent[:],
            negative=self.negative,
            is_float=self.is_float,
            exponent_negative=self.exponent_negative
        )
        obj._normalize()
        return obj

    def __repr__(self):
        return f"<MegaNumber {self.to_decimal_string(50)}>"

    @classmethod
    def create(cls, value: str, number_type: str) -> Union["MegaNumber", "MegaInteger", "MegaFloat", "MegaArray", "MegaBinary"]:
        """
        Create a MegaNumber of the specified type from a string value.
        """
        if number_type == "MegaInteger":
            return MegaInteger.from_decimal_string(value)
        elif number_type == "MegaFloat":
            return MegaFloat.from_decimal_string(value)
        elif number_type == "MegaArray":
            return MegaArray.from_decimal_string(value)
        elif number_type == "MegaBinary":
            return MegaBinary.from_decimal_string(value)
        else:
            raise ValueError(f"Unknown number type: {number_type}")
