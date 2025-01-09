import unittest
from bizarromath.meganumber.mega_number import MegaNumber
from bizarromath.mega_fractions.mega_fractions_core import MegaFraction

class TestMegaFraction(unittest.TestCase):
    def test_add(self):
        num1 = MegaNumber.from_int(1)
        denom1 = MegaNumber.from_int(2)
        frac1 = MegaFraction(num1, denom1)

        num2 = MegaNumber.from_int(1)
        denom2 = MegaNumber.from_int(3)
        frac2 = MegaFraction(num2, denom2)

        result = frac1.add(frac2)
        expected_numerator = MegaNumber.from_int(5)
        expected_denominator = MegaNumber.from_int(6)
        self.assertEqual(result.numerator, expected_numerator)
        self.assertEqual(result.denominator, expected_denominator)

    def test_sub(self):
        num1 = MegaNumber.from_int(1)
        denom1 = MegaNumber.from_int(2)
        frac1 = MegaFraction(num1, denom1)

        num2 = MegaNumber.from_int(1)
        denom2 = MegaNumber.from_int(3)
        frac2 = MegaFraction(num2, denom2)

        result = frac1.sub(frac2)
        expected_numerator = MegaNumber.from_int(1)
        expected_denominator = MegaNumber.from_int(6)
        self.assertEqual(result.numerator, expected_numerator)
        self.assertEqual(result.denominator, expected_denominator)

    def test_mul(self):
        num1 = MegaNumber.from_int(1)
        denom1 = MegaNumber.from_int(2)
        frac1 = MegaFraction(num1, denom1)

        num2 = MegaNumber.from_int(1)
        denom2 = MegaNumber.from_int(3)
        frac2 = MegaFraction(num2, denom2)

        result = frac1.mul(frac2)
        expected_numerator = MegaNumber.from_int(1)
        expected_denominator = MegaNumber.from_int(6)
        self.assertEqual(result.numerator, expected_numerator)
        self.assertEqual(result.denominator, expected_denominator)

    def test_div(self):
        num1 = MegaNumber.from_int(1)
        denom1 = MegaNumber.from_int(2)
        frac1 = MegaFraction(num1, denom1)

        num2 = MegaNumber.from_int(1)
        denom2 = MegaNumber.from_int(3)
        frac2 = MegaFraction(num2, denom2)

        result = frac1.div(frac2)
        expected_numerator = MegaNumber.from_int(3)
        expected_denominator = MegaNumber.from_int(2)
        self.assertEqual(result.numerator, expected_numerator)
        self.assertEqual(result.denominator, expected_denominator)

    def test_to_meganumber(self):
        num = MegaNumber.from_int(1)
        denom = MegaNumber.from_int(2)
        frac = MegaFraction(num, denom)

        result = frac.to_meganumber()
        expected = MegaNumber.from_float(0.5)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
