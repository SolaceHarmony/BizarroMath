"""
Fraction logic built atop HPC MegaNumber for integer fraction arithmetic.
"""

from .fraction_core import MegaFraction
from .fraction_wrappers import (
    hpc_is_zero,
    hpc_add,
    hpc_sub,
    hpc_mul,
    hpc_divmod,
    hpc_gcd,
    parse_decimal_string_to_hpc,
    hpc_abs,
    hpc_to_decimal_string,
    hpc_inc,
    hpc_shr1,
)

__all__ = [
    "MegaFraction",
    "hpc_is_zero",
    "hpc_add",
    "hpc_sub",
    "hpc_mul",
    "hpc_divmod",
    "hpc_gcd",
    "parse_decimal_string_to_hpc",
    "hpc_abs",
    "hpc_to_decimal_string",
    "hpc_inc",
    "hpc_shr1",
]