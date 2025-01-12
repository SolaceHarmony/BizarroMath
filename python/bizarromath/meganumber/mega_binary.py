import array
from enum import Enum
from typing import Union, List, Tuple

import numpy as np

from .mega_number import MegaNumber
from .mega_float import MegaFloat


def choose_array_type():
    """
    Try to use 64-bit unsigned limbs ('Q').
    If not supported (e.g., 32-bit ARM), fall back to 32-bit unsigned ('L').
    """
    try:
        _ = array.array('Q', [0])
        return 'Q', 64
    except (ValueError, OverflowError):
        return 'L', 32


class InterferenceMode(Enum):
    XOR = "xor"
    AND = "and"
    OR  = "or"


class MegaBinary(MegaNumber):
    """
    HPC-based binary data class, storing bits in chunk-limb arrays ('Q' or 'L').
    Includes wave generation, duty-cycle patterns, interference, HPC-limb 
    arithmetic, and optional leading-zero preservation.
    """

    def __init__(self, value: Union[str, bytes, bytearray] = "0",
                 keep_leading_zeros: bool = True,
                 **kwargs):
        """
        By default, keep_leading_zeros=True so wave usage won't lose top zero-limbs.
        Pass keep_leading_zeros=False if you want normal HPC big-int trimming.
        'value' can be:
          - str of binary digits (e.g. "1010" or "0b1010")
          - bytes/bytearray (will parse each byte => 8 bits => HPC-limb)
          - default "0" => HPC-limb of just [0].
        """
        super().__init__(
            mantissa=None,
            exponent=None,
            negative=False,
            is_float=False,
            exponent_negative=False,
            keep_leading_zeros=keep_leading_zeros,
            **kwargs
        )


        # Step 1) Auto-detect and convert input
        if isinstance(value, (bytes, bytearray)):
            # We want to store original bytes if needed
            self.byte_data = bytearray(value)
            # Convert them to a binary string => HPC-limbs
            bin_str = "".join(format(b, "08b") for b in self.byte_data)
        else:
            # Assume it's a string of bits (e.g. "1010" or "0b1010")
            # or possibly an empty string => "0"
            bin_str = value
            if bin_str.startswith("0b"):
                bin_str = bin_str[2:]
            if not bin_str:
                bin_str = "0"

            # Also build self.byte_data from this binary string
            # so we have a consistent stored representation if needed.
            # We'll chunk every 8 bits => int => byte
            def bits_to_byte(bits):
                return int(bits, 2)

            self.byte_data = bytearray()
            for i in range(0, len(bin_str), 8):
                chunk = bin_str[i : i + 8]
                self.byte_data.append(bits_to_byte(chunk.zfill(8)))  # ensure it's 8 bits

        # Step 2) Now parse bin_str into HPC-limbs
        self._parse_binary_string(bin_str)

        # Step 3) _normalize() with respect to keep_leading_zeros
        self._normalize()

    # ----------------------------------------------------------------
    #   PARSING HELPERS
    # ----------------------------------------------------------------
    def _parse_binary_string(self, bin_str: str) -> None:
        """Convert binary string => HPC-limb in little-endian chunk form."""
        if bin_str.startswith("0b"):
            bin_str = bin_str[2:]
        if not bin_str:
            bin_str = "0"

        val = int(bin_str, 2)

        csize = self._global_chunk_size
        limbs = []
        while val > 0:
            limbs.append(val & self._mask)
            val >>= csize
        if not limbs:
            limbs = [0]
        self.mantissa = limbs

    def _parse_bytes(self, val: bytes) -> None:
        """Parse each byte => 8 bits => HPC-limb array in little-endian form."""
        bin_str = "".join(format(b, "08b") for b in val)
        self._bit_length = len(bin_str)  # e.g. 8*len(val)
        self._parse_binary_string(bin_str)
    def _parse_binary_string(self, bin_str: str) -> None:
        if bin_str.startswith("0b"):
            bin_str = bin_str[2:]
        if not bin_str:
            bin_str = "0"

        self._bit_length = len(bin_str)  # capture the actual number of bits

        val = int(bin_str, 2)
        # build HPC-limbs in little-endian
        csize = self._global_chunk_size
        limbs = []
        while val > 0:
            limbs.append(val & self._mask)
            val >>= csize
        if not limbs:
            limbs = [0]
        self.mantissa = limbs
    # ----------------------------------------------------------------
    #   ARITHMETIC OVERRIDES (Returning MegaBinary)
    # ----------------------------------------------------------------
    def add(self, other: "MegaBinary") -> "MegaBinary":
        result = super().add(other)
        # build new MegaBinary from 'result.mantissa'
        out_str = bin(self._chunklist_to_int(result.mantissa))[2:]
        out_bin = self.__class__(out_str)
        # Copy bit_length
        out_bin._bit_length = len(out_str)
        return out_bin

    def sub(self, other: "MegaBinary") -> "MegaBinary":
        result = super().sub(other)
        # build new MegaBinary from 'result.mantissa'
        out_str = bin(self._chunklist_to_int(result.mantissa))[2:]
        out_bin = self.__class__(out_str)
        # Copy bit_length
        out_bin._bit_length = len(out_str)
        return out_bin

    def mul(self, other: "MegaBinary") -> "MegaBinary":
        result = super().mul(other)
        # build new MegaBinary from 'result.mantissa'
        out_str = bin(self._chunklist_to_int(result.mantissa))[2:]
        out_bin = self.__class__(out_str)
        # Copy bit_length
        out_bin._bit_length = len(out_str)
        return out_bin

    def div(self, other: "MegaBinary") -> Union["MegaBinary", MegaFloat]:
        """
        Integer division. If result is float-based => returns MegaFloat.
        """
        if not other.mantissa or (len(other.mantissa) == 1 and other.mantissa[0] == 0):
            raise ZeroDivisionError("Divide by zero")

        result = super().div(other)
        
        if result.is_float:
            # build new MegaBinary from 'result.mantissa'
            out_str = bin(self._chunklist_to_int(result.mantissa))[2:]
            out_bin = self.__class__(out_str)
            # Copy bit_length
            out_bin._bit_length = len(out_str)
            return out_bin
        else:
            bit_str = bin(self._chunklist_to_int(result.mantissa))[2:]
            return self.__class__(bit_str)

    # ----------------------------------------------------------------
    #   SHIFT
    # ----------------------------------------------------------------
    def shift_left(self, bits: "MegaBinary") -> "MegaBinary":
        """
        Shift HPC-limb left by 'bits' (a MegaBinary).
        chunk_shifts = bits // csize
        bit_shifts   = bits %  csize
        Insert chunk_shifts zero-limbs at the front, then partial shift.
        """
        csize = self._global_chunk_size
        chunk_shifts = bits.div(self.__class__(bin(csize)[2:]))
        bit_shifts   = bits.sub(chunk_shifts.mul(self.__class__(bin(csize)[2:])))

        shift_count = int(chunk_shifts.to_decimal_string())
        new_arr = array.array(self._chunk_code, [0]*shift_count)
        new_arr.extend(self.mantissa)

        if not bit_shifts.is_zero():
            shift_val = int(bit_shifts.to_decimal_string())
            carry = 0
            for i in range(len(new_arr)):
                val = (new_arr[i] << shift_val) | carry
                new_arr[i] = val & self._mask
                carry = val >> self._global_chunk_size
            if carry:
                new_arr.append(carry)

        result = self.__class__("0")
        result.mantissa = new_arr
        result._normalize()
        return result

    def shift_right(self, bits: "MegaBinary") -> "MegaBinary":
        csize = self._global_chunk_size
        chunk_shifts = bits.div(self.__class__(bin(csize)[2:]))
        bit_shifts   = bits.sub(chunk_shifts.mul(self.__class__(bin(csize)[2:])))

        shift_count = int(chunk_shifts.to_decimal_string())
        if shift_count >= len(self.mantissa):
            return self.__class__("0")

        new_arr = array.array(self._chunk_code, self.mantissa[shift_count:])

        if not bit_shifts.is_zero():
            shift_val = int(bit_shifts.to_decimal_string())
            carry = 0
            for i in range(len(new_arr)-1, -1, -1):
                val = new_arr[i]
                new_arr[i] = ((val >> shift_val) | carry) & self._mask
                carry = (val << (self._global_chunk_size - shift_val)) & self._mask

        result = self.__class__("0")
        result.mantissa = new_arr
        result._normalize()
        return result

    # ----------------------------------------------------------------
    #   WAVES + DUTY CYCLE
    # ----------------------------------------------------------------
        # ----------------------------------------------------------------
    #   EXAMPLE BLOCKY-SIN & DUTY-WAVE CREATION (No Python float/int)
    # ----------------------------------------------------------------

    @classmethod
    def generate_blocky_sin(cls, length: "MegaBinary", half_period: "MegaBinary") -> "MegaBinary":
        """
        Creates a rudimentary square wave (blocky sine) of total 'length' bits.
        half_period is half the wave’s period in HPC-limb form.
        
        Logic:
          - We track an accumulator 'acc' from 0 up to 2*half_period (the full period).
          - If acc < half_period => wave bit=1, else 0.
          - Then acc += 1 each step (HPC-limb).
          - If acc >= 2*half_period => acc -= 2*half_period.
          
        The result: bits set from 0..(half_period-1) in each cycle. 
        """

        # wave: HPC-limb to store resulting bits
        wave = cls("0")
        wave._keep_leading_zeros = True  # preserve leading zeros if needed

        # We’ll define two_half_period = half_period << 1
        two = cls("10")  # binary "10" => decimal 2
        two_half_period = half_period.mul(two)

        # Start accumulators
        i = cls("0")     # HPC-limb index
        acc = cls("0")   # HPC-limb accumulator

        while True:
            # 1) Compare i vs length: if i >= length => break
            cmp_i_len = i._compare_abs(length.mantissa)
            if cmp_i_len >= 0:
                break

            # 2) Compare acc vs half_period => if acc < half_period => bit=1, else 0
            cmp_acc_half = acc._compare_abs(half_period.mantissa)
            wave_bit = (cmp_acc_half < 0)  # True=>1, False=>0

            # 3) Set wave bit at index i
            wave.set_bit(i, wave_bit)

            # 4) acc++ => HPC-limb increment
            acc = acc.add(cls("1"))

            # 5) if acc >= 2*half_period => acc -= 2*half_period
            cmp_acc_twoperiod = acc._compare_abs(two_half_period.mantissa)
            if cmp_acc_twoperiod >= 0:
                acc = acc.sub(two_half_period)

            # 6) i++ => HPC-limb increment to next bit
            i = i.add(cls("1"))

        wave._normalize()
        return wave
    @classmethod
    def create_duty_cycle(cls, length: "MegaBinary", duty_cycle: "MegaBinary") -> "MegaBinary":
        """
        Create a pattern of 'duty_cycle' fraction of 'length' bits set to 1.
        pattern = (1 << (length*duty_cycle)) - 1, then shift left the remainder.
        """
        high_samples = length.mul(duty_cycle)   # number of '1' bits
        one = cls("1")

        pattern = one.shift_left(high_samples).sub(one)
        remaining = length.sub(high_samples)
        if not remaining.is_zero():
            pattern = pattern.shift_left(remaining)
        return pattern

    def propagate(self, shift: "MegaBinary") -> "MegaBinary":
        """Shift left by 'shift' => wave moves 'shift' bits to the left."""
        return self.shift_left(shift)

    @classmethod
    def interfere(cls, waves: List["MegaBinary"], mode: InterferenceMode) -> "MegaBinary":
        """Combine multiple waves bitwise (XOR, AND, OR)."""
        if not waves:
            raise ValueError("Need at least one wave for interference")

        result = waves[0]
        for wave in waves[1:]:
            max_len = max(len(result.mantissa), len(wave.mantissa))
            result_arr = array.array(result._chunk_code, result.mantissa)
            wave_arr   = array.array(wave._chunk_code, wave.mantissa)
            result_arr.extend([0] * (max_len - len(result_arr)))
            wave_arr.extend([0] * (max_len - len(wave_arr)))

            new_arr = array.array(result._chunk_code, [0]*max_len)
            for i in range(max_len):
                if mode == InterferenceMode.XOR:
                    new_arr[i] = result_arr[i] ^ wave_arr[i]
                elif mode == InterferenceMode.AND:
                    new_arr[i] = result_arr[i] & wave_arr[i]
                elif mode == InterferenceMode.OR:
                    new_arr[i] = result_arr[i] | wave_arr[i]

            new_wave = cls("0")
            new_wave.mantissa = new_arr
            new_wave._normalize()
            result = new_wave
        return result

    # ----------------------------------------------------------------
    #   BIT ACCESS
    # ----------------------------------------------------------------
    def get_bit(self, position: "MegaBinary") -> bool:
        """
        Return bit at 'position' (0-based, LSB=bit0).
        If position >= total bits, returns False.
        """
        csize = self._global_chunk_size
        chunk_index = int(position.div(self.__class__(bin(csize)[2:])).to_decimal_string())
        bit_offset  = int(position.sub(self.__class__(bin(csize)[2:]).mul(
                          self.__class__(bin(chunk_index)[2:]))).to_decimal_string())

        if chunk_index >= len(self.mantissa):
            return False
        return bool(self.mantissa[chunk_index] & (1 << bit_offset))

    def set_bit(self, position: "MegaBinary", value: bool) -> None:
        """
        Set bit at 'position' (0-based). HPC-limb extends if needed.
        """
        csize = self._global_chunk_size
        chunk_index = int(position.div(self.__class__(bin(csize)[2:])).to_decimal_string())
        bit_offset  = int(position.sub(self.__class__(bin(csize)[2:]).mul(
                          self.__class__(bin(chunk_index)[2:]))).to_decimal_string())

        while chunk_index >= len(self.mantissa):
            self.mantissa.append(0)

        if value:
            self.mantissa[chunk_index] |= (1 << bit_offset)
        else:
            self.mantissa[chunk_index] &= ~(1 << bit_offset)
        self._normalize()

    # ----------------------------------------------------------------
    #   BIT/BYTES/STRING OUTPUT
    # ----------------------------------------------------------------
    def to_bits(self) -> list[int]:
        """
        Return the HPC-limb bits in LSB-first, but only up to _bit_length.
        If _bit_length is None (like a normal big-int?), we return all bits.
        """
        bits = []
        csize = self._global_chunk_size
        for limb in self.mantissa:
            for i in range(csize):
                bits.append((limb >> i) & 1)

        if hasattr(self, '_bit_length') and self._bit_length is not None:
            return bits[:self._bit_length]
        else:
            # fallback: normal HPC approach
            # Trim trailing zeros only if you want, or just return all
            while len(bits) > 1 and bits[-1] == 0:
                bits.pop()
            return bits

    def to_bits_bigendian(self) -> list[int]:
        """
        Reverse chunk and bit order => big-endian: highest bit first.
        """
        bits = []
        csize = self._global_chunk_size
        for limb in reversed(self.mantissa):
            for i in reversed(range(csize)):
                bits.append((limb >> i) & 1)
        return bits

    def to_string(self) -> str:
        """
        HPC-limb => integer => binary string (leading zeros stripped by bin()).
        For wave usage, see to_full_bitstring().
        """
        if len(self.mantissa) == 1 and self.mantissa[0] == 0:
            return "0"

        val = 0
        shift = 0
        for i, limb in enumerate(self.mantissa):
            val += limb << shift
            shift += self._global_chunk_size
        return bin(val)[2:]

    def to_full_bitstring(self) -> str:
        """
        Zero-padded bitstring: length = (len(mantissa)*_global_chunk_size).
        """
        total_bits = len(self.mantissa) * self._global_chunk_size
        val = 0
        shift = 0
        for i, limb in enumerate(self.mantissa):
            val += (limb << shift)
            shift += self._global_chunk_size
        raw_str = bin(val)[2:]
        return raw_str.zfill(total_bits)

    def to_string_bigendian(self) -> str:
        """Join big-endian bits => '101010...' format."""
        return "".join(str(b) for b in self.to_bits_bigendian())

    def is_zero(self) -> bool:
        return (len(self.mantissa) == 1 and self.mantissa[0] == 0)
    def to_bytes(self) -> bytearray:
        """Return internal byte representation"""
        return self.byte_data
    def __repr__(self):
        return f"<MegaBinary {self.to_string()}>"


    # ----------------------------------------------------------------
    #   WAVE UTILS
    # ----------------------------------------------------------------
    def generate_wave_bit(self, t: float, freq: float, duty: float) -> int:
        """
        Simple wave logic => 1 if phase < duty, else 0.
        """
        phase = (t * freq) % 1.0
        return 1 if phase < duty else 0

    def shift_in_bit(self, bit_val: int) -> None:
        """
        SHIFT HPC-limb left by 1, set bit0 if bit_val=1.
        Leading zeros are retained if keep_leading_zeros=True.
        """
        carry = 0
        for i in range(len(self.mantissa)):
            val = (self.mantissa[i] << 1) | carry
            self.mantissa[i] = val & self._mask
            carry = val >> self._global_chunk_size

        if carry:
            self.mantissa.append(carry)
        if bit_val:
            self.mantissa[0] |= 1

        self._normalize()

    def wave_step(self, wave_bit: int) -> None:
        """Convenience: shift HPC-limb by 1 bit, set wave_bit."""
        self.shift_in_bit(wave_bit)

    def wave_update(self, input_val: int, t: float, freq: float, duty: float) -> None:
        """
        1) generate wave_bit => 0/1
        2) combine with input => XOR
        3) shift HPC-limb by that combined bit
        """
        wbit = self.generate_wave_bit(t, freq, duty)
        combined = wbit ^ input_val
        self.shift_in_bit(combined)
    # ----------------------------------------------------------------
    #   ENCODER (from earlier)
    # ----------------------------------------------------------------
    @classmethod
    def create_duty_wave(cls, length: "MegaBinary", duty_ratio_num: "MegaBinary", duty_ratio_den: "MegaBinary") -> "MegaBinary":
        """
        HPC-limb “duty wave”:
          - length = total bits
          - duty_ratio_num / duty_ratio_den = fraction of bits set = 'on'
        """
        wave = cls("0")
        wave._keep_leading_zeros = True

        # duty_length = (length * num) // den
        length_times_num = length.mul(duty_ratio_num)
        duty_length = length_times_num.div(duty_ratio_den)  # HPC-limb integer divide

        # set bits [0..(duty_length - 1)] to 1
        i = cls("0")
        one = cls("1")
        while True:
            # if i >= duty_length => break
            if i._compare_abs(duty_length.mantissa) >= 0:
                break
            wave.set_bit(i, True)
            i = i.add(one)

        wave._normalize()
        return wave
    @classmethod
    def decode_duty_wave(cls, wave: "MegaBinary", length: "MegaBinary") -> Tuple["MegaBinary", "MegaBinary"]:
        """
        HPC-limb “decoder” for a simple duty-wave:
        - `wave` is a MegaBinary with some bits = 1
        - `length` is how many bits we consider
        Returns (sum_bits, length) to represent the fraction sum_bits/length.
        Example usage:
        fraction_num, fraction_den = decode_duty_wave(...)
         The fraction is fraction_num / fraction_den in HPC-limb form.
        """
        sum_bits = cls("0")
        one = cls("1")
        i = cls("0")

        while True:
            # if i >= length => stop
            if i._compare_abs(length.mantissa) >= 0:
                break

            # Check if wave’s bit at position i is set
            if wave.get_bit(i):
                sum_bits = sum_bits.add(one)

            # i++
            i = i.add(one)

        # sum_bits / length is your recovered duty fraction.
        return (sum_bits, length)
    @classmethod
    def create_blocky_complex_wave(cls, length: "MegaBinary") -> "MegaBinary":
        """
        A toy “complex” HPC-limb wave: we combine multiple patterned segments,
        purely in HPC-limb. For instance:
          - Segment A: repeating pattern 1010...
          - Segment B: repeating pattern 11110000...
          - Segment C: etc.
        We do all logic with HPC-limb indexes.
        """
        wave = cls("0")
        wave._keep_leading_zeros = True

        i = cls("0")
        one = cls("1")

        while True:
            if i.compare_abs(length) >= 0:
                break

            # HPC-limb "mod 16" approach => we cheat with python int again,
            # but in your real code, do chunk-based mod.
            i_val = wave._mantissa_to_int(i.mantissa)
            mod16 = i_val & 15  # i % 16
            # Some silly pattern:
            #  - bits 0..3 => set
            #  - bits 8..10 => set
            #  - else 0
            bit_val = False
            if (mod16 < 4) or (8 <= mod16 <= 10):
                bit_val = True

            wave.set_bit(i, bit_val)

            i = i.add(one)

        return wave

    @classmethod
    def encode_simple_duty_wave(cls, wave: "MegaBinary", length: "MegaBinary") -> "MegaBinary":
        """
        A toy "encoder": interpret wave as amplitude (0 or 1) and produce
        HPC-limb duty wave with that fraction. We do:
          sum_of_bits = count how many bits are set
          fraction = sum_of_bits / length
          Then create a single chunk of 'length' bits, fraction of them set.
        """
        # 1) sum_of_bits = decode how many bits in 'wave'
        sum_of_bits = cls("0")
        one = cls("1")
        i = cls("0")

        while True:
            if i._compare_abs(length.mantissa) >= 0:
                break
            if wave.get_bit(i):
                sum_of_bits = sum_of_bits.add(one)
            i = i.add(one)

        # 2) build a new HPC-limb with sum_of_bits bits set, out of total length
        encoded = cls("0")
        encoded._keep_leading_zeros = True
        i = cls("0")
        while True:
            if i._compare_abs(sum_of_bits.mantissa) >= 0:
                break
            encoded.set_bit(i, True)
            i = i.add(one)

        return encoded

    @classmethod
    def decode_simple_duty_wave(cls, encoded: "MegaBinary", length: "MegaBinary") -> "MegaBinary":
        """
        Reverse of encode_simple_duty_wave:
          - count how many bits are set in 'encoded' => sum_encoded
          - interpret fraction = sum_encoded / length
          - Then produce a wave that has 'sum_encoded' bits set at the start,
            rest off, same as the original. 
        """
        # 1) sum_of_bits in 'encoded'
        sum_encoded = cls("0")
        one = cls("1")
        i = cls("0")

        while True:
            if i._compare_abs(length.mantissa) >= 0:
                break
            if encoded.get_bit(i):
                sum_encoded = sum_encoded.add(one)
            i = i.add(one)

        # 2) Create HPC-limb wave with sum_encoded bits set
        out_wave = cls("0")
        out_wave._keep_leading_zeros = True
        i = cls("0")

        while True:
            if i._compare_abs(sum_encoded.mantissa) >= 0:
                break
            out_wave.set_bit(i, True)
            i = i.add(one)

        return out_wave
    def to_waveform(self, total_bits: int, sample_rate=1.0, amplitude=1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert HPC-limb bits => float waveform of length 'total_bits'.
        If bit i=1 => amplitude, else 0.
        """
        wave = np.zeros(total_bits, dtype=float)
        for i in range(total_bits):
            # Build a MegaBinary 'i' => check HPC-limb
            if self.get_bit(MegaBinary(bin(i)[2:])):
                wave[i] = amplitude
        t = np.linspace(0, total_bits/sample_rate, total_bits, endpoint=False)
        return t, wave