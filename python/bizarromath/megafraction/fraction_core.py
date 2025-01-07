# bizarromath/megafraction/fraction_core.py

import math
from typing import Tuple
from bizarromath.meganumber.mega_number import MegaNumber

#
#  1) HPC Wrappers for integer-only usage of MegaNumber
#

def hpc_is_zero(x: MegaNumber) -> bool:
    """
    Return True if x==0 (mantissa=[0], exponent=0).
    """
    return (len(x.mantissa) == 1 and x.mantissa[0] == 0)

def hpc_compare(a: MegaNumber, b: MegaNumber) -> int:
    """
    HPC compare => -1 if a<b, 0 if a==b, +1 if a>b.
    Compares sign first, then absolute magnitude.
    """
    # if both zero
    if hpc_is_zero(a) and hpc_is_zero(b):
        return 0
    # sign check
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

def hpc_add(a: MegaNumber, b: MegaNumber) -> MegaNumber:
    """
    HPC integer add => a + b. 
    (No float logic.)
    """
    if a.is_float or b.is_float:
        raise NotImplementedError("hpc_add is for integer mode only.")
    return a.add(b)

def hpc_sub(a: MegaNumber, b: MegaNumber) -> MegaNumber:
    """
    HPC integer subtract => a - b.
    """
    if a.is_float or b.is_float:
        raise NotImplementedError("hpc_sub is for integer mode only.")
    return a.sub(b)

def hpc_mul(a: MegaNumber, b: MegaNumber) -> MegaNumber:
    """
    HPC integer multiply => a*b.
    """
    if a.is_float or b.is_float:
        raise NotImplementedError("hpc_mul is for integer mode only.")
    return a.mul(b)

def hpc_abs(x: MegaNumber) -> MegaNumber:
    """
    HPC absolute value => returns a copy with negative=False.
    """
    y = x.copy()
    y.negative = False
    return y

def hpc_divmod(a: MegaNumber, b: MegaNumber) -> Tuple[MegaNumber, MegaNumber]:
    """
    HPC integer divmod => returns (quotient, remainder).
    remainder = a - quotient*b.
    """
    if a.is_float or b.is_float:
        raise NotImplementedError("hpc_divmod is for integer mode only.")
    if hpc_is_zero(b):
        raise ZeroDivisionError("hpc_divmod by zero.")
    quotient = a.div(b)  # HPC integer division
    # remainder = a - quotient*b
    remainder = a.sub(quotient.mul(b))
    return (quotient, remainder)

def hpc_gcd(a: MegaNumber, b: MegaNumber) -> MegaNumber:
    """
    HPC gcd => Euclidean algorithm with integer divmod.
    """
    A = hpc_abs(a)
    B = hpc_abs(b)
    while not hpc_is_zero(B):
        q, r = hpc_divmod(A, B)
        A, B = B, r
    return A

def hpc_to_decimal_string(x: MegaNumber) -> str:
    """
    HPC integer => decimal. (No float exponent.)
    """
    if x.is_float:
        raise NotImplementedError("hpc_to_decimal_string only for integer HPC mode.")
    return x.to_decimal_string()

def parse_decimal_string_to_hpc(s: str) -> MegaNumber:
    """
    HPC parse decimal => HPC integer. 
    If empty => 0
    """
    if not s:
        return MegaNumber.from_int(0)
    return MegaNumber.from_decimal_string(s)

#
#  2) MegaFraction: fraction logic built on HPC integer MegaNumber
#

class MegaFraction:
    """
    Fraction type storing numerator & denominator as HPC MegaNumbers in integer mode.
    - on creation, gcd-reduces => simplest fraction
    - unbounded decimal expansions (no cycle detection).
    """
    __slots__ = ('num', 'den')

    def __init__(self, numerator: MegaNumber, denominator: MegaNumber):
        # check denominator != 0
        if hpc_is_zero(denominator):
            raise ZeroDivisionError("Fraction denominator cannot be zero.")
        # gcd-reduce
        g = hpc_gcd(numerator, denominator)

        # ensure denominator > 0
        if denominator.negative:
            denominator.negative = False
            numerator.negative = not numerator.negative

        # do integer div => num//g, den//g
        self.num, _ = hpc_divmod(numerator, g)
        self.den, _ = hpc_divmod(denominator, g)

    @classmethod
    def from_decimal_string(cls, dec_str: str) -> "MegaFraction":
        """
        Parse a decimal string => HPC fraction with denominator=10^frac_len.
        e.g. "123.456" => 123456/1000
        """
        s = dec_str.strip()
        if not s:
            # fraction=0
            return cls(MegaNumber.from_int(0), MegaNumber.from_int(1))

        negative = s.startswith('-')
        if negative:
            s = s[1:].strip()

        point_pos = s.find('.')
        frac_len = 0
        if point_pos >= 0:
            frac_len = len(s) - (point_pos + 1)
            s = s.replace('.', '')

        # parse HPC integer numerator
        numerator = parse_decimal_string_to_hpc(s)
        if negative:
            numerator.negative = True

        if frac_len == 0:
            # purely integer
            return cls(numerator, MegaNumber.from_int(1))
        else:
            # denominator = 10^frac_len
            ten = MegaNumber.from_int(10)
            denom = MegaNumber.from_int(1)
            for _ in range(frac_len):
                denom = denom.mul(ten)
            return cls(numerator, denom)

    def copy(self) -> "MegaFraction":
        """
        Return a fraction copy (numerator & denominator HPC copies).
        """
        return MegaFraction(self.num.copy(), self.den.copy())

    def add(self, other: "MegaFraction") -> "MegaFraction":
        """
        (a/b) + (c/d) => (ad + bc)/ bd
        """
        ad = hpc_mul(self.num, other.den)
        bc = hpc_mul(other.num, self.den)
        new_num = hpc_add(ad, bc)
        new_den = hpc_mul(self.den, other.den)
        return MegaFraction(new_num, new_den)

    def sub(self, other: "MegaFraction") -> "MegaFraction":
        """
        (a/b) - (c/d) => (ad - bc)/bd
        """
        ad = hpc_mul(self.num, other.den)
        bc = hpc_mul(other.num, self.den)
        new_num = hpc_sub(ad, bc)
        new_den = hpc_mul(self.den, other.den)
        return MegaFraction(new_num, new_den)

    def mul(self, other: "MegaFraction") -> "MegaFraction":
        """
        (a/b)*(c/d) => (ac)/(bd)
        """
        new_num = hpc_mul(self.num, other.num)
        new_den = hpc_mul(self.den, other.den)
        return MegaFraction(new_num, new_den)

    def div(self, other: "MegaFraction") -> "MegaFraction":
        """
        (a/b)/(c/d) => (a/b)*(d/c) => ad/bc
        check c!=0
        """
        if hpc_is_zero(other.num):
            raise ZeroDivisionError("Fraction divide by zero.")
        new_num = hpc_mul(self.num, other.den)
        new_den = hpc_mul(self.den, other.num)
        return MegaFraction(new_num, new_den)

    def __str__(self):
        """
        Quick text => "num/den".
        """
        return f"{self.num.to_decimal_string()} / {self.den.to_decimal_string()}"

    def to_decimal_string_unbounded(self) -> str:
        """
        Convert fraction => decimal string, continuing until remainder=0.
        If fraction has prime factors !=2,5 => infinite repeating decimal => loop forever.
        """
        # integer part => q,r = num//den
        q, r = hpc_divmod(self.num, self.den)
        sign_str = "-" if q.negative else ""
        q.negative = False
        int_str = hpc_to_decimal_string(q)  # HPC integer => decimal

        if hpc_is_zero(r):
            return sign_str + int_str

        # fractional digits
        frac_digits = []
        r_abs = r.copy()
        r_abs.negative = False
        ten = MegaNumber.from_int(10)

        # loop until remainder=0 => might never terminate if repeating
        while True:
            # remainder *=10
            r_abs = hpc_mul(r_abs, ten)
            digit_q, r_abs = hpc_divmod(r_abs, self.den)
            digit_val = digit_q.mantissa[0]  # in [0..9]
            frac_digits.append(str(digit_val))

            if hpc_is_zero(r_abs):
                # done
                break

        frac_str = "".join(frac_digits)
        return f"{sign_str}{int_str}.{frac_str}"
