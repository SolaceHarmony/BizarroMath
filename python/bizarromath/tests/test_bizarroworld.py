import pytest
from bizarromath.bizzaroworld.bizarroworld_core import DutyCycleWave, BizarroWorld, FrequencyBandAnalyzer
from bizarromath.meganumber.mega_number import MegaNumber

def test_duty_cycle_wave():
    sample_rate = MegaNumber.from_int(44100)
    duty_cycle = MegaNumber.from_int(50).div(MegaNumber.from_int(100))
    period = MegaNumber.from_int(8)
    wave_gen = DutyCycleWave(sample_rate, duty_cycle, period)
    wave = wave_gen.generate(MegaNumber.from_int(16))
    assert wave == [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]

def test_bizarro_world_from_duty_cycle():
    period = BizarroWorld(mantissa=[8])
    duty = BizarroWorld(mantissa=[4])
    result = BizarroWorld.from_duty_cycle(period, duty)
    assert result.mantissa == [1, 1, 1, 1, 0, 0, 0, 0]

def test_bizarro_world_xor_wave():
    wave1 = BizarroWorld(mantissa=[1, 0, 1, 0])
    wave2 = BizarroWorld(mantissa=[0, 1, 0, 1])
    result = wave1.xor_wave(wave2)
    assert result.mantissa == [1, 1, 1, 1]

def test_frequency_band_analyzer():
    bit_depth = MegaNumber.from_int(16)
    sample_rate = MegaNumber.from_int(44100)
    num_bands = MegaNumber.from_int(8)
    analyzer = FrequencyBandAnalyzer(bit_depth, sample_rate, num_bands)
    bits = [1, 0, 1, 1, 0, 1, 0, 1]
    band_waves = analyzer.analyze_pattern(bits)
    assert len(band_waves) == 8
    assert all(isinstance(band, list) for band in band_waves)
