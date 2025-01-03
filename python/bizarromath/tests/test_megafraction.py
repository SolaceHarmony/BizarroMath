# bizarromath/tests/test_megafraction.py
import pytest

from bizarromath.megafraction.fraction_core import MegaFraction

def test_fraction_basic():
    f1 = MegaFraction.from_decimal_string("123.456")
    f2 = MegaFraction.from_decimal_string("0.0001")
    sum_ = f1.add(f2)
    # 123.456 + 0.0001 => 123.4561
    assert sum_.to_decimal_string_unbounded() == "123.4561"

    product_ = f1.mul(f2)
    # 123.456 * 0.0001 => 0.0123456
    assert product_.to_decimal_string_unbounded() == "0.0123456"

def test_fraction_int():
    f1 = MegaFraction.from_decimal_string("999")
    f2 = MegaFraction.from_decimal_string("1")
    assert f1.sub(f2).to_decimal_string_unbounded() == "998"

def test_fraction_signs():
    fneg = MegaFraction.from_decimal_string("-5")
    fpos = MegaFraction.from_decimal_string("3")
    # -5 + 3 => -2
    added = fneg.add(fpos)
    assert added.to_decimal_string_unbounded() == "-2"
    # -5 * 3 => -15
    product = fneg.mul(fpos)
    assert product.to_decimal_string_unbounded() == "-15"

def test_fraction_div():
    f1 = MegaFraction.from_decimal_string("100.0")
    f2 = MegaFraction.from_decimal_string("4.0")
    result = f1.div(f2)
    # 100.0 / 4.0 => 25.0
    assert result.to_decimal_string_unbounded() == "25"

def test_fraction_gcdreduction():
    # e.g. 200/100 => 2/1
    big_frac = MegaFraction.from_decimal_string("200.0")
    small_frac = MegaFraction.from_decimal_string("100.0")
    ratio = big_frac.div(small_frac)
    # => 2
    assert ratio.to_decimal_string_unbounded() == "2"

def test_fraction_zero_den_error():
    with pytest.raises(ZeroDivisionError):
        MegaFraction.from_decimal_string("123/0")  # or force something

def test_fraction_negative_denom():
    # e.g. fraction => 123 / -456 => internally => -123 / 456
    f = MegaFraction.from_decimal_string("123/-456")  # if you parse slash yourself or something
    # you'd confirm sign is on numerator
    assert str(f).startswith("-")  # i.e. negative fraction