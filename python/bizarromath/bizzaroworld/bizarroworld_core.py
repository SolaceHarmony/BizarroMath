from typing import List
from dataclasses import dataclass
from ..meganumber.mega_number import MegaNumber

@dataclass
class DutyCycleWave:
    """Binary duty-cycle wave generator for high-frequency carrier signals"""
    sample_rate: int = 44100
    duty_cycle: float = 0.5
    period: int = 8

    def __post_init__(self):
        self.num_samples = int(self.sample_rate / self.period)  # Number of samples per period

    def generate(self, num_steps: int) -> MegaNumber:
        """Generate a duty cycle wave"""
        wave = [0] * num_steps
        high_samples = int(num_steps * self.duty_cycle)

        for i in range(num_steps):
            if i < high_samples:
                wave[i] = 1  # High value for the duty cycle
            else:
                wave[i] = 0  # Low value for the remaining time

        # Convert wave to MegaNumber
        wave_mantissa = wave[::-1]  # Reverse to match MegaNumber's chunk order
        return MegaNumber(mantissa=wave_mantissa, exponent=[0])

    def to_decimal(self, wave: MegaNumber) -> str:
        """Convert the generated wave to a decimal string"""
        return wave.to_decimal_string()

    def to_int_array(self, wave: MegaNumber) -> List[int]:
        """Convert the generated wave to an array of integers"""
        return wave.mantissa

    def to_bytearray(self, wave: MegaNumber) -> bytearray:
        """Convert the generated wave to a bytearray"""
        return bytearray(wave.mantissa)

class BizarroWorld(MegaNumber):
    def __init__(
        self,
        mantissa: List[int] = None,
        exponent: List[int] = None,
        negative: bool = False,
        is_float: bool = False,
        exponent_negative: bool = False
    ):
        super().__init__(
            mantissa=mantissa,
            exponent=exponent,
            negative=negative,
            is_float=is_float,
            exponent_negative=exponent_negative
        )

    @classmethod
    def from_duty_cycle(cls, period: "BizarroWorld", duty: "BizarroWorld") -> "BizarroWorld":
        """Create a binary wave state from period and duty cycle"""
        if not period.mantissa or not duty.mantissa:
            return cls([0])
        
        # Generate binary pattern based on period and duty cycle using DutyCycleWave
        wave_generator = DutyCycleWave(
            sample_rate=44100,  # Default sample rate
            duty_cycle=float(duty.to_decimal_string()),  # Convert duty cycle to float
            period=int(period.to_decimal_string())  # Convert period to int
        )
        generated_wave = wave_generator.generate(len(period.mantissa))
        return cls(mantissa=generated_wave.mantissa, exponent=[0])

    def xor_wave(self, other: "BizarroWorld") -> "BizarroWorld":
        """Binary wave interference through XOR"""
        # Use MegaNumber's chunk operations for XOR
        result_mantissa = self._xor_chunks(self.mantissa, other.mantissa)
        return BizarroWorld(mantissa=result_mantissa, exponent=[0])

    def _xor_chunks(self, a: List[int], b: List[int]) -> List[int]:
        """XOR operation on chunk-limbs"""
        # Implement proper chunk-by-chunk XOR
        max_len = max(len(a), len(b))
        result = [0] * max_len
        for i in range(max_len):
            av = a[i] if i < len(a) else 0
            bv = b[i] if i < len(b) else 0
            result[i] = av ^ bv
        return result
