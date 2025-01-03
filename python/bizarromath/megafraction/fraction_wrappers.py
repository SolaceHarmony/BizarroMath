from typing import Tuple
from ..meganumber.mega_number import MegaNumber

def hpc_is_zero(x: MegaNumber) -> bool:
    return (len(x.mantissa) == 1 and x.mantissa[0] == 0)

def hpc_compare(a: MegaNumber, b: MegaNumber) -> int:
    # Compare sign first
    if hpc_is_zero(a) and hpc_is_zero(b):
        return 0
    if a.negative and not b.negative:
        return -1
    if b.negative and not a.negative:
        return 1
    # same sign => compare absolute
    c = MegaNumber._compare_abs(a.mantissa, b.mantissa)
    if c == 0:
        return 0
    # if both negative => reversed
    if a.negative and b.negative:
        return -c
    return c

def hpc_inc(x: MegaNumber) -> MegaNumber:
    one = MegaNumber.from_int(1)
    return x.add(one)

def hpc_shr1(x: MegaNumber) -> MegaNumber:
    if x.negative:
        raise NotImplementedError("hpc_shr1 for negative not implemented.")
    new_mant = MegaNumber._div2(x.mantissa)
    out = MegaNumber(new_mant, [0], False)
    out._normalize()
    return out

def hpc_add(a: MegaNumber, b: MegaNumber) -> MegaNumber:
    if a.is_float or b.is_float:
        raise NotImplementedError("Integer HPC fraction mode only.")
    return a.add(b)

def hpc_sub(a: MegaNumber, b: MegaNumber) -> MegaNumber:
    if a.is_float or b.is_float:
        raise NotImplementedError("Integer HPC fraction mode only.")
    return a.sub(b)

def hpc_mul(a: MegaNumber, b: MegaNumber) -> MegaNumber:
    if a.is_float or b.is_float:
        raise NotImplementedError("Integer HPC fraction mode only.")
    return a.mul(b)

def hpc_divmod(a: MegaNumber, b: MegaNumber) -> Tuple[MegaNumber, MegaNumber]:
    if a.is_float or b.is_float:
        raise NotImplementedError("Integer HPC fraction mode only.")
    if hpc_is_zero(b):
        raise ZeroDivisionError("hpc_divmod by zero.")
    quotient = a.div(b)
    remainder = a.sub(quotient.mul(b))
    return (quotient, remainder)

def hpc_abs(x: MegaNumber) -> MegaNumber:
    y = x.copy()
    y.negative = False
    return y

def hpc_gcd(a: MegaNumber, b: MegaNumber) -> MegaNumber:
    A = hpc_abs(a)
    B = hpc_abs(b)
    while not hpc_is_zero(B):
        q, r = hpc_divmod(A, B)
        A, B = B, r
    return A

def hpc_to_decimal_string(x: MegaNumber) -> str:
    if x.is_float:
        raise NotImplementedError("hpc_to_decimal_string only for integer HPC fraction mode.")
    return x.to_decimal_string()

def parse_decimal_string_to_hpc(s: str) -> MegaNumber:
    if not s:
        return MegaNumber.from_int(0)
    return MegaNumber.from_decimal_string(s)