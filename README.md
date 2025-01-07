# BizarroMath

BizarroMath is a **high-performance**, chunk-based big-integer library (and fraction system) built for **insane precision** and **flexibility**. Whether you’re doing monstrous integer exponentiations or exact decimal arithmetic without compromise, BizarroMath’s unique HPC approach keeps you in control.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Package Structure](#package-structure)
- [Usage Examples](#usage-examples)
  - [MegaNumber (Chunk-Based Big-Int)](#meganumber-chunk-based-big-int)
  - [MegaFraction (Exact Rational Arithmetic)](#megafraction-exact-rational-arithmetic)
  - [Memory Pool and Optimized Multiplication](#memory-pool-and-optimized-multiplication)
  - [DutyCycleWave (Binary Wave Generator)](#dutycyclewave-binary-wave-generator)
  - [FrequencyBandAnalyzer (Frequency Analysis)](#frequencybandanalyzer-frequency-analysis)
- [Contributing](#contributing)
- [License](#license)
- [References & Credits](#references--credits)

---

## Features

1. **Chunk-Based Big-Int**
   - Stores large numbers in base \(2^{	ext{chunk\_size}}\) (8, 16, 32, or 64 bits per limb).
   - **No** internal usage of Python `int` mid-calculation—only for final chunk manipulations.

2. **Optional Float Exponents**
   - `MegaNumber` can store a binary float exponent, letting you parse decimals (e.g., `"123.456"`) exactly and represent them as \(	ext{mantissa} 	imes 2^{	ext{exponent}}\).

3. **Exact Fraction System**
   - `MegaFraction` merges HPC big-int numerator & denominator, so you can do **exact** decimal operations with gcd-reduction.
   - Supports **unbounded decimal expansions** (no forced rounding) and HPC wrappers for integer-only fraction ops.

4. **HPC Multiplication**
   - **Memory Pool** (`CPUMemoryPool`) to reuse array-limb buffers and reduce allocations.
   - `OptimizedToom3` includes placeholders for Karatsuba and Toom-3 multiplication.

5. **High Precision, Infinitely**
   - No rounding or truncation mid-calculation.
   - Perfect for cryptography, advanced numeric analysis, or any scenario where Python’s default `int` or `decimal` might not suffice.

6. **Binary Wave Generation**
   - `DutyCycleWave` class to generate binary waves using `MegaNumber` for handling large bit waveforms.

7. **Frequency Analysis**
   - `FrequencyBandAnalyzer` class to analyze bit patterns across frequency bands using `MegaNumber`.

---

## Installation

```bash
git clone https://github.com/SolaceHarmony/BizarroMath.git
cd BizarroMath
pip install -e .
```

- Requires **Python 3.7+**  
- For advanced usage, optionally install **pytest** (for testing) and **mpmath** (for cross-checking HPC results).

---

## Quick Start

```python
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
```

That’s it! You’re doing **HPC chunk-based arithmetic** with no hidden rounding.

---

## Package Structure

```
bizarromath/
├── __init__.py           # Exports top-level classes (MegaNumber, MegaFraction, etc.)
├── meganumber/           # Chunk-based big-int code
│   ├── __init__.py
│   ├── mega_number.py    # MegaNumber class
│   ├── mega_array.py     # MegaArray class
│   ├── mega_binary.py    # MegaBinary class
│   ├── memory_pool.py    # CPUMemoryPool & BlockMetrics
│   └── optimized_toom3.py# HPC multiply: Karatsuba, Toom-3
├── megafraction/         # HPC fraction logic
│   ├── __init__.py
│   ├── fraction_core.py  # MegaFraction class + HPC fraction ops
│   └── fraction_wrappers.py # HPC wrappers (hpc_add, hpc_sub, etc.)
└── bizzaroworld/         # Binary wave generation and frequency analysis
    ├── __init__.py
    ├── bizarroworld_core.py # DutyCycleWave and FrequencyBandAnalyzer classes
└── tests/
    ├── __init__.py
    ├── test_meganumber.py      # Tests for MegaNumber
    ├── test_megafraction.py    # Tests for MegaFraction
    └── test_hpc_integration.py # HPC memory pool & advanced multiply tests
    └── test_bizarroworld.py    # Tests for DutyCycleWave and FrequencyBandAnalyzer
```

**Key Modules**  
- **`meganumber`**: core HPC big-int (`MegaNumber`), plus memory pool & advanced multipliers.  
- **`megafraction`**: fraction logic (`MegaFraction`) + HPC wrappers.  
- **`bizzaroworld`**: binary wave generation (`DutyCycleWave`) and frequency analysis (`FrequencyBandAnalyzer`).

---

## Usage Examples

### MegaNumber (Chunk-Based Big-Int)

```python
from bizarromath.meganumber import MegaNumber

# Parse a large decimal string
big_num = MegaNumber.from_decimal_string("123456789012345678901234567890")
print("Big num =>", big_num)

# Integer operations
x = MegaNumber.from_int(999999)
y = MegaNumber.from_int(1001)
product = x.mul(y)   # HPC integer multiply
print("999999 * 1001 =>", product.to_decimal_string())

# Float exponent usage
float_num = MegaNumber.from_decimal_string("0.0000000001234")
print("Float HPC =>", float_num.to_decimal_string())
```

### MegaFraction (Exact Rational Arithmetic)

```python
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
```

### Memory Pool and Optimized Multiplication

```python
from bizarromath.meganumber import CPUMemoryPool, OptimizedToom3
import array

pool = CPUMemoryPool()
hpc_mul = OptimizedToom3(pool)

# Convert Python int => HPC chunk-limb array
def int_to_limbs(value: int) -> array.array:
    csize = MegaNumber._global_chunk_size or 64
    base = (1 << csize)
    out = array.array('Q', [])
    while value > 0:
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
```

### DutyCycleWave (Binary Wave Generator)

```python
from bizarromath.bizzaroworld.bizarroworld_core import DutyCycleWave
from bizarromath.meganumber.mega_number import MegaNumber

sample_rate = MegaNumber.from_int(44100)
duty_cycle = MegaNumber.from_int(50).div(MegaNumber.from_int(100))
period = MegaNumber.from_int(8)
wave_gen = DutyCycleWave(sample_rate, duty_cycle, period)
wave = wave_gen.generate(MegaNumber.from_int(16))
print("Generated wave:", wave)
```

### FrequencyBandAnalyzer (Frequency Analysis)

```python
from bizarromath.bizzaroworld.bizarroworld_core import FrequencyBandAnalyzer
from bizarromath.meganumber.mega_number import MegaNumber

bit_depth = MegaNumber.from_int(16)
sample_rate = MegaNumber.from_int(44100)
num_bands = MegaNumber.from_int(8)
analyzer = FrequencyBandAnalyzer(bit_depth, sample_rate, num_bands)
bits = [1, 0, 1, 1, 0, 1, 0, 1]
band_waves = analyzer.analyze_pattern(bits)
print("Band waves:", band_waves)
```

### MegaInteger, MegaFloat, MegaArray, and MegaBinary

```python
from bizarromath.meganumber import MegaInteger, MegaFloat, MegaArray, MegaBinary

# MegaInteger
int_value = MegaInteger.from_decimal_string("1234567890")
print("MegaInteger value:", int_value.to_decimal_string())

# MegaFloat
float_value = MegaFloat.from_decimal_string("12345.67890")
print("MegaFloat value:", float_value.to_decimal_string())

# MegaArray
array_value = MegaArray.from_decimal_string("1,2,3,4,5")
print("MegaArray value:", array_value.to_decimal_string())

# MegaBinary
binary_value = MegaBinary.from_decimal_string("1101")
print("MegaBinary value:", binary_value.to_decimal_string())
```

---

## Contributing

1. **Fork** the project.  
2. **Create a branch** (e.g., `feature/awesome-improvement`).  
3. **Commit your changes** and **push**.  
4. **Open a Pull Request** describing your changes.

We love new HPC routines, advanced polynomial multiplication, or creative fraction expansions (e.g. cycle detection for repeating decimals).

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.  
Happy HPC computing—and enjoy your bizarrely large (or small) numeric explorations!

---

## References & Credits

BizarroMath is indebted to a wide range of mathematical and computational references:

- **Karatsuba Multiplication** (A. Karatsuba & Yu. Ofman, 1962)  
- **Toom-3 / Toom–Cook multiplication** (A. Toom, 1963; S. Cook, 1966)  
- **Knuth’s Algorithmic Fundamentals** for big-integer arithmetic (Donald E. Knuth, *The Art of Computer Programming*, Vol. 2)  
- HPC big-int wave transformations by Sydney Renee @sydneyrenee  
- Additional code or formula snippets adapted from academic references or other open-source HPC libraries.

In all cases, we remain grateful for the groundwork laid by these pioneering works.
