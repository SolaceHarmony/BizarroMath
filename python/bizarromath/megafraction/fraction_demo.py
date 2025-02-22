# bizarromath/megafraction/fraction_demo.py
"""
Sample usage or fraction stress tests for demonstration.

To run:
    from bizarromath.megafraction.fraction_demo import fraction_stress_test
    fraction_stress_test()
"""

from .fraction_core import MegaFraction
from bizarromath.bizarroworld.bizarroworld_core import DutyCycleWave, FrequencyBandAnalyzer
from ..meganumber.mega_number import MegaNumber, MegaInteger, MegaFloat, MegaArray, MegaBinary

def fraction_stress_test():
    """
    Demonstrate HPC fraction usage with a variety of decimal inputs,
    performing add, sub, mul, div, plus showing the unbounded decimal expansions.
    """
    examples = [
        "0.5",
        "123.456",
        "9999.99999999",
        "0.0000000001234",
        "-0.5",
        "1.2345",
        "12345.6789",
        "2.718281828459",
        "3.1415926535",
        "100000.00001",
        "9999999999.9999999999"
    ]

    print("\n=== BizarroMath Fraction Stress Test ===")
    for s in examples:
        print(f"\n--- Testing decimal: {s} ---")
        try:
            frac = MegaFraction.from_decimal_string(s)
            print(f"Fraction object => num={frac.num.to_decimal_string()}, den={frac.den.to_decimal_string()}")
            
            # Show unbounded decimal expansion
            # (will loop forever if fraction has prime factors other than 2/5)
            print("Unbounded decimal =>", frac.to_decimal_string_unbounded())

            # Let's do an operation with e.g. 2.0
            f2 = MegaFraction.from_decimal_string("2.0")

            # add
            added = frac.add(f2)
            print(f"  {s} + 2.0 => {added.to_decimal_string_unbounded()}")

            # sub
            subd = frac.sub(f2)
            print(f"  {s} - 2.0 => {subd.to_decimal_string_unbounded()}")

            # mul
            product = frac.mul(f2)
            print(f"  {s} * 2.0 => {product.to_decimal_string_unbounded()}")

            # div
            try:
                quotient = frac.div(f2)
                print(f"  {s} / 2.0 => {quotient.to_decimal_string_unbounded()}")
            except ZeroDivisionError:
                print(f"  {s} / 2.0 => ZeroDivisionError (division by zero?)")

        except Exception as e:
            print(f"Error creating or operating on fraction {s}: {e}")

    print("\n=== End of fraction_stress_test ===")

def duty_cycle_wave_demo():
    """
    Demonstrate DutyCycleWave class usage.
    """
    sample_rate = MegaNumber.from_int(44100)
    duty_cycle = MegaNumber.from_int(50).div(MegaNumber.from_int(100))
    period = MegaNumber.from_int(8)
    wave_gen = DutyCycleWave(sample_rate, duty_cycle, period)
    wave = wave_gen.generate(MegaNumber.from_int(16))
    print("Generated wave:", wave)

def frequency_band_analyzer_demo():
    """
    Demonstrate FrequencyBandAnalyzer class usage.
    """
    bit_depth = MegaNumber.from_int(16)
    sample_rate = MegaNumber.from_int(44100)
    num_bands = MegaNumber.from_int(8)
    analyzer = FrequencyBandAnalyzer(bit_depth, sample_rate, num_bands)
    bits = [1, 0, 1, 1, 0, 1, 0, 1]
    band_waves = analyzer.analyze_pattern(bits)
    print("Band waves:", band_waves)

def mega_number_demo():
    """
    Demonstrate the usage of different MegaNumber types.
    """
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

if __name__ == "__main__":
    # If run directly, just call fraction_stress_test.
    fraction_stress_test()
    duty_cycle_wave_demo()
    frequency_band_analyzer_demo()
    mega_number_demo()
