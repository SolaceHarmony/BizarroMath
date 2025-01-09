from typing import Union, List
from enum import Enum
from .mega_number import MegaNumber
from .mega_float import MegaFloat

class InterferenceMode(Enum):
    XOR = "xor"
    AND = "and" 
    OR = "or"

class MegaBinary(MegaNumber):
    def __init__(self, value: Union[str, bytes, bytearray]):
        super().__init__()  # Initialize MegaNumber first to set chunk size
        
        # Ensure chunk size is initialized
        if self._global_chunk_size is None:
            self._auto_pick_chunk_size()
            type(self)._auto_detect_done = True

        # Auto-detect and convert input type
        if isinstance(value, (bytes, bytearray)):
            self.byte_data = value if isinstance(value, bytearray) else bytearray(value)
            binary_str = self._parse_bytes(self.byte_data)
        else:
            binary_str = self._parse_binary_string(value)
            # Convert binary string to bytearray
            self.byte_data = bytearray(int(binary_str[i:i+8], 2) 
                                     for i in range(0, len(binary_str), 8))

        # Initialize with chunked values
        chunks = []
        for i in range(0, len(binary_str), self._global_chunk_size):
            end = min(i + self._global_chunk_size, len(binary_str))
            chunk = binary_str[i:end]
            chunks.append(int(chunk, 2))
        
        self.mantissa = chunks
        self.binary_string = binary_str
        self._normalize()

    def _parse_bytes(self, value: Union[bytes, bytearray]) -> str:
        """Convert bytes/bytearray to binary string"""
        return ''.join(format(b, '08b') for b in value)

    def _parse_binary_string(self, value: str) -> str:
        """Parse string value, stripping '0b' prefix if present"""
        return value[2:] if value.startswith('0b') else value

    def add(self, other: "MegaBinary") -> "MegaBinary":
        """Add using superclass chunked arithmetic"""
        result = super().add(other)
        return self.__class__(bin(self._chunklist_to_int(result.mantissa))[2:])

    def sub(self, other: "MegaBinary") -> "MegaBinary":
        """Subtract using superclass chunked arithmetic"""
        result = super().sub(other)
        return self.__class__(bin(self._chunklist_to_int(result.mantissa))[2:])

    def mul(self, other: "MegaBinary") -> "MegaBinary":
        """Multiply using superclass chunked arithmetic"""
        result = super().mul(other)
        return self.__class__(bin(self._chunklist_to_int(result.mantissa))[2:])

    def div(self, other: "MegaBinary") -> Union["MegaBinary", MegaFloat]:
        """Divide using superclass chunked arithmetic"""
        if not other.mantissa or (len(other.mantissa) == 1 and other.mantissa[0] == 0):
            raise ZeroDivisionError("Division by zero")

        result = super().div(other)
        
        if result.is_float:
            return result  # Already a MegaFloat
        else:
            return self.__class__(bin(self._chunklist_to_int(result.mantissa))[2:])

    def to_bytes(self) -> bytearray:
        """Return internal byte representation"""
        return self.byte_data

    @classmethod
    def from_bytes(cls, value: Union[bytes, bytearray]) -> "MegaBinary":
        """Create MegaBinary from bytes/bytearray"""
        return cls(value)

    def to_float(self) -> MegaFloat:
        """Convert binary number to MegaFloat"""
        value = int(self.binary_string, 2)
        return MegaFloat.from_decimal_string(str(value))

    def from_float(self, float_num: MegaFloat) -> "MegaBinary":
        """Create MegaBinary from MegaFloat (truncates decimal part)"""
        int_value = int(float(float_num.to_decimal_string()))
        return self.__class__(bin(int_value)[2:])
        
    def to_string(self) -> str:
        """Convert to binary string"""
        return self.binary_string

    def shift_left(self, bits: "MegaBinary") -> "MegaBinary":
        """Shift bits left using pure chunk operations"""
        chunk_shifts = bits.div(self.__class__(bin(self._global_chunk_size)[2:]))
        bit_shifts = bits.sub(chunk_shifts.mul(self.__class__(bin(self._global_chunk_size)[2:])))
        
        new_chunks = [0] * (int(chunk_shifts.to_decimal_string())) + self.mantissa[:]
        
        if not bit_shifts.is_zero():
            carry = 0
            shift_val = int(bit_shifts.to_decimal_string())
            for i in range(len(new_chunks)):
                val = (new_chunks[i] << shift_val) | carry
                new_chunks[i] = val & self._mask
                carry = val >> self._global_chunk_size
            if carry:
                new_chunks.append(carry)
                
        result = self.__class__('0')
        result.mantissa = new_chunks
        result._normalize()
        return result

    def shift_right(self, bits: "MegaBinary") -> "MegaBinary":
        """Shift bits right using pure chunk operations"""
        chunk_shifts = bits.div(self.__class__(bin(self._global_chunk_size)[2:]))
        bit_shifts = bits.sub(chunk_shifts.mul(self.__class__(bin(self._global_chunk_size)[2:])))
        
        chunk_shift_val = int(chunk_shifts.to_decimal_string())
        if chunk_shift_val >= len(self.mantissa):
            return self.__class__('0')
            
        new_chunks = self.mantissa[chunk_shift_val:]
        
        if not bit_shifts.is_zero():
            carry = 0
            shift_val = int(bit_shifts.to_decimal_string())
            for i in range(len(new_chunks)-1, -1, -1):
                val = new_chunks[i]
                new_chunks[i] = ((val >> shift_val) | carry) & self._mask
                carry = (val << (self._global_chunk_size - shift_val)) & self._mask
        
        result = self.__class__('0')
        result.mantissa = new_chunks
        result._normalize()
        return result

    def get_slice(self, start: "MegaBinary", length: "MegaBinary") -> "MegaBinary":
        """Get a slice of bits using pure chunk operations"""
        # Calculate start position in chunks
        chunk_pos = start.div(self.__class__(bin(self._global_chunk_size)[2:]))
        bit_offset = start.sub(chunk_pos.mul(self.__class__(bin(self._global_chunk_size)[2:])))
        
        result_chunks = []
        remaining_bits = length
        
        # Work with chunk_pos directly as MegaBinary
        while not remaining_bits.is_zero() and chunk_pos.compare(self.__class__(bin(len(self.mantissa))[2:])) < 0:
            chunk = self.mantissa[chunk_pos.mantissa[0]]  # Safe as this is a small index
            available = self.__class__(bin(self._global_chunk_size)[2:]).sub(bit_offset)
            bits_to_take = min(available, remaining_bits)
            
            # Create mask using shift operations
            mask = self.__class__('1').shift_left(bits_to_take).sub(self.__class__('1'))
            value = (chunk >> bit_offset.mantissa[0]) & mask.mantissa[0]  # Safe for small offsets
            result_chunks.append(value)
            
            remaining_bits = remaining_bits.sub(bits_to_take)
            chunk_pos = chunk_pos.add(self.__class__('1'))
            bit_offset = self.__class__('0')
            
        result = self.__class__('0')
        result.mantissa = result_chunks
        result._normalize()
        return result

    def to_bits(self) -> List[int]:
        """Convert to list of bits"""
        bits = []
        raw_bytes = self.to_bytes()
        for b in raw_bytes:
            for bit_idx in reversed(range(8)):
                bits.append((b >> bit_idx) & 1)
        return bits

    @classmethod
    def from_bits(cls, bits: List[int]) -> "MegaBinary":
        """Create from list of bits"""
        byte_array = bytearray()
        for i in range(0, len(bits), 8):
            chunk = bits[i:i+8]
            val = 0
            for bit_idx, bit in enumerate(reversed(chunk)):
                val |= (bit & 1) << bit_idx
            byte_array.append(val)
        return cls(byte_array)

    def is_zero(self) -> bool:
        """Check if number is zero"""
        return len(self.mantissa) == 1 and self.mantissa[0] == 0

    def __repr__(self):
        """String representation"""
        return f"<MegaBinary {self.to_string()}>"

    # Wave Operations
    @classmethod
    def create_duty_cycle(cls, length: "MegaBinary", duty_cycle: "MegaBinary") -> "MegaBinary":
        """Create a duty cycle pattern"""
        high_samples = length.mul(duty_cycle)
        one = cls(bytearray([1]))
        
        pattern = one.shift_left(high_samples).sub(one)
        remaining = length.sub(high_samples)
        
        if not remaining.is_zero():
            pattern = pattern.shift_left(remaining)
            
        return pattern

    def propagate(self, shift: "MegaBinary") -> "MegaBinary":
        """Propagate wave by shifting"""
        return self.shift_left(shift)

    @classmethod
    def interfere(cls, waves: List["MegaBinary"], mode: InterferenceMode) -> "MegaBinary":
        """Apply interference between waves"""
        if not waves:
            raise ValueError("Need at least one wave for interference")
            
        result = waves[0]
        for wave in waves[1:]:
            max_chunks = max(len(result.mantissa), len(wave.mantissa))
            result_chunks = result.mantissa + [0] * (max_chunks - len(result.mantissa))
            wave_chunks = wave.mantissa + [0] * (max_chunks - len(wave.mantissa))
            
            new_chunks = []
            for i in range(max_chunks):
                if mode == InterferenceMode.XOR:
                    new_chunks.append(result_chunks[i] ^ wave_chunks[i])
                elif mode == InterferenceMode.AND:
                    new_chunks.append(result_chunks[i] & wave_chunks[i])
                elif mode == InterferenceMode.OR:
                    new_chunks.append(result_chunks[i] | wave_chunks[i])
                    
            result = cls(bytearray([0]))
            result.mantissa = new_chunks
            result._normalize()
            
        return result
    
    def get_bit(self, position: "MegaBinary") -> bool:
        """Get bit at specified position"""
        chunk_size = self._global_chunk_size
        chunk_index = int(position.div(self.__class__(bin(chunk_size)[2:])).to_decimal_string())
        bit_offset = int(position.sub(self.__class__(bin(chunk_size)[2:]).mul(
            self.__class__(bin(chunk_index)[2:]))).to_decimal_string())
        
        if chunk_index >= len(self.mantissa):
            return False
            
        return bool(self.mantissa[chunk_index] & (1 << bit_offset))

    def set_bit(self, position: "MegaBinary", value: bool) -> None:
        """Set bit at specified position"""
        chunk_size = self._global_chunk_size
        chunk_index = int(position.div(self.__class__(bin(chunk_size)[2:])).to_decimal_string())
        bit_offset = int(position.sub(self.__class__(bin(chunk_size)[2:]).mul(
            self.__class__(bin(chunk_index)[2:]))).to_decimal_string())
        
        while chunk_index >= len(self.mantissa):
            self.mantissa.append(0)
            
        if value:
            self.mantissa[chunk_index] |= (1 << bit_offset)
        else:
            self.mantissa[chunk_index] &= ~(1 << bit_offset)
            
        self._normalize()