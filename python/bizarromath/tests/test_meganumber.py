# bizarromath/tests/test_meganumber.py
import pytest
import random

from bizarromath.meganumber.mega_number import MegaNumber
from bizarromath.meganumber.mega_array import MegaArray
from bizarromath.meganumber.mega_binary import MegaBinary

def test_meganumber_add():
    a = MegaNumber.from_decimal_string("123")
    b = MegaNumber.from_decimal_string("456")
    c = a.add(b)
    assert c.to_decimal_string() == "579"

def test_meganumber_sub():
    a = MegaNumber.from_decimal_string("500")
    b = MegaNumber.from_decimal_string("123")
    c = a.sub(b)
    assert c.to_decimal_string() == "377"

def test_meganumber_mul():
    a = MegaNumber.from_decimal_string("999999")
    b = MegaNumber.from_decimal_string("1001")
    product = a.mul(b)
    # 999999 * 1001 = 1000998999
    assert product.to_decimal_string() == "1000998999"

def test_meganumber_div():
    a = MegaNumber.from_decimal_string("999999")
    b = MegaNumber.from_decimal_string("1000")
    quotient = a.div(b)
    # 999999 // 1000 = 999
    assert quotient.to_decimal_string() == "999"

def test_meganumber_pow():
    base = MegaNumber.from_decimal_string("5")
    exponent = MegaNumber.from_decimal_string("3")
    result = base.pow(exponent)
    # 5^3 = 125
    assert result.to_decimal_string() == "125"

def test_meganumber_sqrt():
    x = MegaNumber.from_decimal_string("1000000")
    root = x.sqrt()
    assert root.to_decimal_string() == "1000"

def test_meganumber_floatmode():
    # small float parse
    x = MegaNumber.from_decimal_string("0.5")
    assert x.is_float is True
    assert x.to_decimal_string().endswith("* 2^-")  # e.g. "5 * 2^-4"

def test_random_add():
    # optional random test
    for _ in range(5):
        val1 = random.randint(1, 999999)
        val2 = random.randint(1, 999999)
        m1 = MegaNumber.from_int(val1)
        m2 = MegaNumber.from_int(val2)
        sum_ = m1.add(m2)
        assert sum_.to_decimal_string() == str(val1 + val2)

def test_megaarray_add():
    a = MegaArray("1,2,3")
    b = MegaArray("4,5,6")
    c = a.add(b)
    assert c.to_string() == "5,7,9"

def test_megaarray_sub():
    a = MegaArray("10,20,30")
    b = MegaArray("1,2,3")
    c = a.sub(b)
    assert c.to_string() == "9,18,27"

def test_megabinary_add():
    a = MegaBinary("1010")
    b = MegaBinary("1100")
    c = a.add(b)
    assert c.to_string() == "10110"

def test_megabinary_sub():
    a = MegaBinary("1100")
    b = MegaBinary("1010")
    c = a.sub(b)
    assert c.to_string() == "10"
