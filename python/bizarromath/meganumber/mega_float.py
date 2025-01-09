import math
from typing import List, Union, TYPE_CHECKING
from .mega_number import MegaNumber

if TYPE_CHECKING:
    from .mega_integer import MegaInteger

class MegaFloat(MegaNumber):
    """
    MegaFloat class for float-specific math operations.
    Inherits from MegaNumber.
    """
    
    def __init__(self, value=None, mantissa=None, exponent=None, negative=False, is_float=True, exponent_negative=False):
        if isinstance(value, str):
            # Use parent's string parsing but ensure float result
            temp = MegaNumber.from_decimal_string(value)
            super().__init__(
                mantissa=temp.mantissa,
                exponent=temp.exponent,
                negative=temp.negative,
                is_float=True,  # Force float mode
                exponent_negative=temp.exponent_negative
            )
        else:
            super().__init__(
                mantissa=mantissa,
                exponent=exponent,
                negative=negative,
                is_float=True,  # Force float mode
                exponent_negative=exponent_negative
            )

    def __repr__(self):
        return f"<MegaFloat {self.to_decimal_string(50)}>"

    def add(self, other: "MegaFloat") -> "MegaFloat":
        """
        Float addition.
        """
        if not self.is_float or not other.is_float:
            raise ValueError("Both numbers must be floating-point numbers")

        # Align the exponents
        exp_diff = self._chunklist_to_int(self.exponent) - self._chunklist_to_int(other.exponent)
        if exp_diff > 0:
            aligned_mantissa = self.mantissa + [0] * exp_diff
            result_mantissa = self._add_chunklists(aligned_mantissa, other.mantissa)
            result_exponent = self.exponent
        else:
            aligned_mantissa = other.mantissa + [0] * (-exp_diff)
            result_mantissa = self._add_chunklists(self.mantissa, aligned_mantissa)
            result_exponent = other.exponent

        result = MegaFloat(
            mantissa=result_mantissa,
            exponent=result_exponent,
            negative=self.negative,
            is_float=True,
            exponent_negative=self.exponent_negative
        )
        result._normalize()
        return result

    def sub(self, other: "MegaFloat") -> "MegaFloat":
        """
        Float subtraction with precision maintenance.
        """
        if not self.is_float or not other.is_float:
            raise NotImplementedError("sub is for float mode only.")
            
        # Align decimal points
        max_decimal_places = max(
            len(str(self._chunklist_to_int(self.mantissa))),
            len(str(self._chunklist_to_int(other.mantissa)))
        )
        
        a_scaled = self.mantissa[:]
        b_scaled = other.mantissa[:]
        
        # Scale up to match decimal places
        while len(str(self._chunklist_to_int(a_scaled))) < max_decimal_places:
            a_scaled = self._mul_chunklists(a_scaled, [10], self._global_chunk_size, self._base)
        while len(str(self._chunklist_to_int(b_scaled))) < max_decimal_places:
            b_scaled = self._mul_chunklists(b_scaled, [10], self._global_chunk_size, self._base)
            
        result = self._sub_chunklists(a_scaled, b_scaled)
        
        return MegaFloat(
            mantissa=result,
            exponent=self.exponent,
            negative=self.negative,
            is_float=True,
            exponent_negative=self.exponent_negative
        )

    def mul(self, other: Union["MegaFloat", "MegaInteger"]) -> "MegaFloat":
        """
        Float multiplication, supporting both MegaFloat and MegaInteger operands.
        Result is always MegaFloat.
        """
        from .mega_integer import MegaInteger  # Import here to avoid circular dependency
        
        if not isinstance(other, (MegaFloat, MegaInteger)):
            raise TypeError("Operand must be MegaFloat or MegaInteger")
            
        # Convert MegaInteger to MegaFloat if needed
        if isinstance(other, MegaInteger):
            other_mantissa = other.mantissa
            other_negative = other.negative
        else:
            other_mantissa = other.mantissa
            other_negative = other.negative
            
        result = self._mul_chunklists(self.mantissa, other_mantissa, self._global_chunk_size, self._base)
        return MegaFloat(
            mantissa=result,
            negative=(self.negative != other_negative),
            is_float=True
        )

    def div(self, other: "MegaFloat") -> "MegaFloat":
        """
        Float division with precision maintenance.
        """
        if not self.is_float or not other.is_float:
            raise NotImplementedError("div is for float mode only.")
            
        # Scale up numerator by adding precision digits
        scaled_mantissa = self.mantissa[:]
        for _ in range(6):  # Add 6 decimal places of precision
            scaled_mantissa = self._mul_chunklists(scaled_mantissa, [10], self._global_chunk_size, self._base)
            
        quotient, _ = self._div_chunk(scaled_mantissa, other.mantissa)
        
        result = MegaFloat(
            mantissa=quotient,
            exponent=self.exponent,
            negative=(self.negative != other.negative),
            is_float=True,
            exponent_negative=self.exponent_negative
        )
        result._normalize()
        return result

    def pow(self, exponent: "MegaFloat") -> "MegaFloat":
        """
        Float exponentiation.
        """
        if not self.is_float or not exponent.is_float:
            raise NotImplementedError("pow is for float mode only.")
        result = self._int_to_chunklist(1, self._global_chunk_size)
        base = self.mantissa[:]
        exp = self._chunklist_to_int(exponent.mantissa)
        while exp > 0:
            if exp % 2 == 1:
                result = self._mul_chunklists(result, base, self._global_chunk_size, self._base)
            base = self._mul_chunklists(base, base, self._global_chunk_size, self._base)
            exp //= 2
        return MegaFloat(mantissa=result, negative=self.negative, is_float=True)

    def sqrt(self) -> "MegaFloat":
        """
        Float square root.
        """
        if not self.is_float:
            raise NotImplementedError("sqrt is for float mode only.")
        x = self._chunklist_to_int(self.mantissa)
        y = int(x ** 0.5)
        result = self._int_to_chunklist(y, self._global_chunk_size)
        return MegaFloat(mantissa=result, negative=self.negative, is_float=True)

    def to_decimal_string(self, max_digits=None) -> str:
        """
        Convert to decimal string with proper decimal point placement.
        """
        if len(self.mantissa) == 1 and self.mantissa[0] == 0:
            return "0.0"
            
        num_str = str(self._chunklist_to_int(self.mantissa))
        if not self.is_float:
            return num_str
            
        # Handle decimal point placement
        if len(num_str) <= 3:  # Add leading zeros if needed
            num_str = "0" * (4 - len(num_str)) + num_str
            
        # Insert decimal point 3 positions from the right
        dec_pos = len(num_str) - 3
        result = num_str[:dec_pos] + "." + num_str[dec_pos:]
        
        # Remove trailing zeros after decimal point
        while result.endswith('0'):
            result = result[:-1]
        if result.endswith('.'):
            result += "0"
            
        return ("-" if self.negative else "") + result

    @classmethod
    def from_value(cls, value: Union[int, float, str, List[int]]) -> "MegaFloat":
        """
        Create a MegaFloat from a given value.
        """
        if isinstance(value, int):
            raise ValueError("Use string inputs for higher precision.")
        elif isinstance(value, float):
            return cls.from_decimal_string(str(value))
        elif isinstance(value, str):
            return cls.from_decimal_string(value)
        elif isinstance(value, list):
            return cls(mantissa=value, is_float=True)
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
