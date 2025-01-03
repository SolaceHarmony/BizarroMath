import pytest
from bizarromath.bizzaroworld.bizarroworld_core import DutyCycleWave, BizarroWorld
from bizarromath.meganumber.mega_number import MegaNumber

def test_duty_cycle_wave_generate():
    wave_gen = DutyCycleWave(sample_rate=44100, duty_cycle=0.5, period=8)
    wave = wave_gen.generate(16)
    assert wave.to_decimal_string() == "32768"  # 16 bits with 8 high and 8 low

def test_duty_cycle_wave_to_decimal():
    wave_gen = DutyCycleWave(sample_rate=44100, duty_cycle=0.5, period=8)
    wave = wave_gen.generate(16)
    decimal_str = wave_gen.to_decimal(wave)
    assert decimal_str == "32768"

def test_duty_cycle_wave_to_int_array():
    wave_gen = DutyCycleWave(sample_rate=44100, duty_cycle=0.5, period=8)
    wave = wave_gen.generate(16)
    int_array = wave_gen.to_int_array(wave)
    assert int_array == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0]

def test_duty_cycle_wave_to_bytearray():
    wave_gen = DutyCycleWave(sample_rate=44100, duty_cycle=0.5, period=8)
    wave = wave_gen.generate(16)
    byte_array = wave_gen.to_bytearray(wave)
    assert byte_array == bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0])

def test_bizarroworld_from_duty_cycle():
    period = BizarroWorld.from_decimal_string("8")
    duty = BizarroWorld.from_decimal_string("0.5")
    wave = BizarroWorld.from_duty_cycle(period, duty)
    assert wave.to_decimal_string() == "32768"
