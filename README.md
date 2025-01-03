Below is a polished README.md for your BizarroMath repository. It’s designed to dazzle new visitors, provide clear installation and usage instructions, and highlight the library’s core features—chunk-based HPC big-int and fraction logic.

BizarroMath

BizarroMath is a high-performance, chunk-based big-integer library (and fraction system) built for insane precision and flexibility. Whether you’re doing monstrous integer exponentiations or exact decimal arithmetic without compromise, BizarroMath’s unique HPC approach keeps you in control.

Table of Contents
	•	Features
	•	Installation
	•	Quick Start
	•	Package Structure
	•	Usage Examples
	•	MegaNumber (Chunk-Based Big-Int)
	•	MegaFraction (Exact Rational Arithmetic)
	•	Memory Pool and Optimized Multiplication
	•	Contributing
	•	License

Features
	1.	Chunk-Based Big-Int
	•	Stores large numbers in base ￼ (8, 16, 32, or 64 bits per limb).
	•	No internal usage of Python int mid-calculation—only for final chunk manipulations.
	2.	Optional Float Exponents
	•	MegaNumber can store a binary float exponent, letting you parse decimals ("123.456") exactly and represent them as ￼.
	3.	Exact Fraction System
	•	MegaFraction merges HPC big-int numerator & denominator, so you can do exact decimal operations with gcd-reduction.
	•	Supports unbounded decimal expansions (with no forced rounding) and HPC wrappers for integer-only fraction ops.
	4.	HPC Multiplication
	•	Memory Pool (CPUMemoryPool) to reuse array-limb buffers and reduce allocations.
	•	OptimizedToom3 includes placeholders for Karatsuba and Toom-3 multiplication.
	5.	High Precision, Infinitely
	•	No rounding or truncation mid-calculation.
	•	Perfect for cryptography, advanced numeric analysis, or any scenario where Python’s default int or decimal might not suffice.

Installation

git clone https://github.com/YourName/BizarroMath.git
cd BizarroMath
pip install -e .

	•	Requires Python 3.7+
	•	For advanced usage, optionally install pytest for testing, mpmath for cross-checking HPC results, etc.

Quick Start

from bizarromath import MegaNumber, MegaFraction

# HPC big-int usage
a = MegaNumber.from_decimal_string("9999999999999999999999")
b = MegaNumber.from_decimal_string("1234567890123456789")
result = a.mul(b)
print("a*b =", result.to_decimal_string())

# HPC fraction usage
f1 = MegaFraction.from_decimal_string("123.456")
f2 = MegaFraction.from_decimal_string("0.0001")
sum_ = f1.add(f2)
print("123.456 + 0.0001 =>", sum_.to_decimal_string_unbounded())

That’s it! You’re doing HPC chunk-based arithmetic with no hidden rounding.

Package Structure

bizarromath/
├── __init__.py           # Exports top-level classes (MegaNumber, MegaFraction, etc.)
├── meganumber/           # Chunk-based big-int code
│   ├── __init__.py
│   ├── mega_number.py    # MegaNumber class
│   ├── memory_pool.py    # CPUMemoryPool & BlockMetrics
│   └── optimized_toom3.py# HPC multiply: Karatsuba, Toom-3
├── megafraction/         # HPC fraction logic
│   ├── __init__.py
│   ├── fraction_core.py  # MegaFraction class + HPC fraction ops
│   └── fraction_wrappers.py # HPC wrappers (hpc_add, hpc_sub, etc.)
└── tests/
    ├── __init__.py
    ├── test_meganumber.py   # Tests for MegaNumber
    ├── test_megafraction.py # Tests for MegaFraction
    └── test_hpc_integration.py # HPC memory pool & advanced multiply tests

Key Modules
	•	meganumber: core HPC big-int (MegaNumber), plus memory pool & advanced multipliers.
	•	megafraction: fraction logic (MegaFraction) + HPC wrappers.

Usage Examples

MegaNumber (Chunk-Based Big-Int)

from bizarromath.meganumber import MegaNumber

# Parse a large decimal string
big_num = MegaNumber.from_decimal_string("123456789012345678901234567890")
print("Big num =>", big_num)

# Integer operations
x = MegaNumber.from_int(999999)
y = MegaNumber.from_int(1001)
product = x.mul(y)   # => HPC integer multiply
print("999999 * 1001 =>", product.to_decimal_string())

# Float exponent usage
float_num = MegaNumber.from_decimal_string("0.0000000001234")
print("Float HPC =>", float_num.to_decimal_string())

MegaFraction (Exact Rational Arithmetic)

from bizarromath.megafraction import MegaFraction

f1 = MegaFraction.from_decimal_string("9999.99999999")
f2 = MegaFraction.from_decimal_string("2.0")

# HPC fraction addition
sum_f = f1.add(f2)
print("9999.99999999 + 2.0 =>", sum_f.to_decimal_string_unbounded())

# HPC fraction multiply
f3 = MegaFraction.from_decimal_string("123.456")
f4 = MegaFraction.from_decimal_string("0.0001")
product_f = f3.mul(f4)
print("123.456 * 0.0001 =>", product_f.to_decimal_string_unbounded())

Memory Pool and Optimized Multiplication

from bizarromath.meganumber import CPUMemoryPool, OptimizedToom3
import array

pool = CPUMemoryPool()
hpc_mul = OptimizedToom3(pool)

# Convert Python int => HPC chunk-limb array
def int_to_limbs(value: int) -> array.array:
    csize = MegaNumber._global_chunk_size or 64
    base = (1 << csize)
    out = array.array('Q', [])
    while value>0:
        out.append(value & (base-1))
        value >>= csize
    if not out:
        out.append(0)
    return out

# HPC multiply
a_val, b_val = 123456, 999999
a_arr = int_to_limbs(a_val)
b_arr = int_to_limbs(b_val)
prod_arr = hpc_mul.multiply(a_arr, b_arr)

# Convert HPC limbs => Python int
def limbs_to_int(limbs: array.array) -> int:
    csize = MegaNumber._global_chunk_size or 64
    val = 0
    shift = 0
    for limb in limbs:
        val += (limb << shift)
        shift += csize
    return val

print("123456 * 999999 =>", limbs_to_int(prod_arr))

Contributing
	1.	Fork the project.
	2.	Create a branch (e.g., feature/awesome-improvement).
	3.	Commit your changes and push.
	4.	Open a Pull Request describing your changes.

We love new HPC routines, advanced polynomial multiplication, or creative fraction expansions (e.g. cycle detection for repeating decimals).

License

This project is licensed under the MIT License. See LICENSE for details.

Happy HPC computing—and enjoy your bizarrely large (or small) numeric explorations!

## References & Credits

BizarroMath is indebted to a wide range of mathematical and computational references:

- **Karatsuba Multiplication** (A. Karatsuba & Yu. Ofman, 1962)
- **Toom-3 / Toom–Cook multiplication** (A. Toom, 1963; S. Cook, 1966)
- **Knuth’s Algorithmic Fundamentals** for big-integer arithmetic (Donald E. Knuth, _The Art of Computer Programming_, Vol. 2)
- HPC big-int wave transformations by Sydney Renee @sydneyrenee.
- Additional code or formula snippets adapted from academic references or other open-source HPC libraries.

In all cases, we remain grateful for the groundwork laid by these pioneering works.