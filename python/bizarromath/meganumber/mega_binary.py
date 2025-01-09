from typing import Union
from .mega_number import MegaNumber
from .mega_float import MegaFloat

class MegaBinary(MegaNumber):
    def __init__(self, value: Union[str, bytes, bytearray]):
        super().__init__()  # Initialize MegaNumber first to set chunk size
        
        # Ensure chunk size is initialized
        if self._global_chunk_size is None:
            self._auto_pick_chunk_size()
            type(self)._auto_detect_done = True

        if isinstance(value, (bytes, bytearray)):
            binary_str = self._parse_bytes(value)
        else:
            binary_str = self._parse_binary_string(value)

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
        return MegaBinary(bin(self._chunklist_to_int(result.mantissa))[2:])

    def sub(self, other: "MegaBinary") -> "MegaBinary":
        """Subtract using superclass chunked arithmetic"""
        result = super().sub(other)
        return MegaBinary(bin(self._chunklist_to_int(result.mantissa))[2:])

    def mul(self, other: "MegaBinary") -> "MegaBinary":
        """Multiply using superclass chunked arithmetic"""
        result = super().mul(other)
        return MegaBinary(bin(self._chunklist_to_int(result.mantissa))[2:])

    def div(self, other: "MegaBinary") -> Union["MegaBinary", MegaFloat]:
        """Divide using superclass chunked arithmetic"""
        if not other.mantissa or (len(other.mantissa) == 1 and other.mantissa[0] == 0):
            raise ZeroDivisionError("Division by zero")

        # Perform division using chunked arithmetic
        result = super().div(other)
        
        # Check if result is a float
        if result.is_float:
            return result  # Already a MegaFloat
        else:
            # Convert to binary representation
            return MegaBinary(bin(self._chunklist_to_int(result.mantissa))[2:])

    def to_bytes(self) -> bytes:
        """Convert binary string to bytes"""
        # Pad to multiple of 8 bits
        padded = self.binary_string.zfill((len(self.binary_string) + 7) // 8 * 8)
        return bytes(int(padded[i:i+8], 2) for i in range(0, len(padded), 8))

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
        return MegaBinary(bin(int_value)[2:])
        
    def to_string(self) -> str:
        return self.binary_string