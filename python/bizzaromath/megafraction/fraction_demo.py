# bizarromath/megafraction/fraction_demo.py
"""
Sample usage or fraction stress tests for demonstration.

To run:
    from bizarromath.megafraction.fraction_demo import fraction_stress_test
    fraction_stress_test()
"""

from .fraction_core import MegaFraction

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

if __name__ == "__main__":
    # If run directly, just call fraction_stress_test.
    fraction_stress_test()