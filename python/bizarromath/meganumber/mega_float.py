import math
import array
from typing import List, Union, TYPE_CHECKING
from .mega_number import MegaNumber

if TYPE_CHECKING:
    from .mega_integer import MegaInteger

class MegaFloat(MegaNumber):
    """
    MegaFloat class for float-specific math operations.
    Inherits from MegaNumber but forces is_float=True.
    """

    def __init__(
        self,
        value=None,
        mantissa: array.array = None,
        exponent: array.array = None,
        negative=False,
        is_float=True,               # Always float
        exponent_negative=False
    ):
        if isinstance(value, str):
            # Parse string with MegaNumber, but force float
            temp = MegaNumber.from_decimal_string(value)
            super().__init__(
                mantissa=temp.mantissa,
                exponent=temp.exponent,
                negative=temp.negative,
                is_float=True,
                exponent_negative=temp.exponent_negative
            )
        else:
            # Normal constructor usage
            if mantissa is None:
                mantissa = array.array(self._chunk_code, [0])  # HPC array
            if exponent is None:
                exponent = array.array(self._chunk_code, [0])
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
        Float addition. Minimal approach: aligns exponents by adding zero limbs.
        """
        if not self.is_float or not other.is_float:
            raise ValueError("Both numbers must be floating-point numbers")

        expA = self._chunklist_to_int(self.exponent)
        expB = other._chunklist_to_int(other.exponent)
        exp_diff = expA - expB

        if exp_diff > 0:
            # self has bigger exponent => shift other's mantissa
            aligned_mantissa = array.array(self._chunk_code, other.mantissa)
            # Extend with exp_diff zero limbs
            aligned_mantissa.extend(array.array(self._chunk_code, [0]*exp_diff))
            result_mantissa = self._add_chunklists(self.mantissa, aligned_mantissa)
            result_exponent = array.array(self._chunk_code, self.exponent)  # copy
        else:
            # other has bigger exponent => shift self's mantissa
            shift_amount = -exp_diff
            aligned_mantissa = array.array(self._chunk_code, self.mantissa)
            aligned_mantissa.extend(array.array(self._chunk_code, [0]*shift_amount))
            result_mantissa = self._add_chunklists(aligned_mantissa, other.mantissa)
            result_exponent = array.array(self._chunk_code, other.exponent)  # copy

        out = MegaFloat(
            mantissa=result_mantissa,
            exponent=result_exponent,
            negative=self.negative,
            is_float=True,
            exponent_negative=self.exponent_negative
        )
        out._normalize()
        return out

    def sub(self, other: "MegaFloat") -> "MegaFloat":
        """
        Float subtraction with a naive "decimal places" approach.
        (Likely incomplete for HPC usage, but updated to array format.)
        """
        if not self.is_float or not other.is_float:
            raise NotImplementedError("sub is for float mode only.")

        # Compare decimal lengths in string form
        str_self = str(self._chunklist_to_int(self.mantissa))
        str_other = str(other._chunklist_to_int(other.mantissa))
        max_decimal_places = max(len(str_self), len(str_other))

        a_scaled = array.array(self._chunk_code, self.mantissa)
        b_scaled = array.array(self._chunk_code, other.mantissa)

        # Scale up to match decimal places
        ten_array = array.array(self._chunk_code, [10])
        while len(str(self._chunklist_to_int(a_scaled))) < max_decimal_places:
            a_scaled = self._mul_chunklists(a_scaled, ten_array, self._global_chunk_size, self._base)
        while len(str(self._chunklist_to_int(b_scaled))) < max_decimal_places:
            b_scaled = self._mul_chunklists(b_scaled, ten_array, self._global_chunk_size, self._base)

        result = self._sub_chunklists(a_scaled, b_scaled)

        return MegaFloat(
            mantissa=result,
            exponent=self.exponent,  # naive approach
            negative=self.negative,
            is_float=True,
            exponent_negative=self.exponent_negative
        )

    def mul(self, other: Union["MegaFloat", "MegaInteger"]) -> "MegaFloat":
        """
        Float multiplication, returns MegaFloat.
        """
        from .mega_integer import MegaInteger  # avoid circular dependency

        if not isinstance(other, (MegaFloat, MegaInteger)):
            raise TypeError("Operand must be MegaFloat or MegaInteger")

        other_mantissa = other.mantissa
        other_negative = other.negative

        # HPC multiply
        out_limb = self._mul_chunklists(
            self.mantissa,
            other_mantissa,
            self._global_chunk_size,
            self._base
        )
        sign = (self.negative != other_negative)
        return MegaFloat(
            mantissa=out_limb,
            negative=sign,
            is_float=True
        )

    def div(self, other: "MegaFloat") -> "MegaFloat":
        """
        Float division with naive approach: scale numerator by 10^6, then divide.
        """
        if not self.is_float or not other.is_float:
            raise NotImplementedError("div is for float mode only.")

        # Scale up by 10^6
        scaled_mantissa = array.array(self._chunk_code, self.mantissa)
        ten_array = array.array(self._chunk_code, [10])
        for _ in range(6):
            scaled_mantissa = self._mul_chunklists(
                scaled_mantissa,
                ten_array,
                self._global_chunk_size,
                self._base
            )

        q, _ = self._div_chunk(scaled_mantissa, other.mantissa)

        sign = (self.negative != other.negative)
        out = MegaFloat(
            mantissa=q,
            exponent=self.exponent,  # naive approach
            negative=sign,
            is_float=True,
            exponent_negative=self.exponent_negative
        )
        out._normalize()
        return out

    def pow(self, exponent: "MegaFloat") -> "MegaFloat":
        """
        Minimal float exponent (by repeated squaring with chunk-based mantissa).
        """
        if not self.is_float or not exponent.is_float:
            raise NotImplementedError("pow is for float mode only.")

        result = self._int_to_chunklist(1, self._global_chunk_size)
        base = array.array(self._chunk_code, self.mantissa)
        exp_val = self._chunklist_to_int(exponent.mantissa)

        while exp_val > 0:
            if exp_val & 1:
                result = self._mul_chunklists(result, base, self._global_chunk_size, self._base)
            base = self._mul_chunklists(base, base, self._global_chunk_size, self._base)
            exp_val >>= 1

        return MegaFloat(
            mantissa=result,
            negative=self.negative,
            is_float=True
        )

    def sqrt(self) -> "MegaFloat":
        """
        Float sqrt => convert to Python int, do math.sqrt, convert back (naive).
        """
        if not self.is_float:
            raise NotImplementedError("sqrt is for float mode only.")

        x_val = self._chunklist_to_int(self.mantissa)
        approx = int(x_val**0.5)
        out_limb = self._int_to_chunklist(approx, self._global_chunk_size)

        return MegaFloat(
            mantissa=out_limb,
            negative=self.negative,
            is_float=True
        )

    def to_decimal_string(self, max_digits=None) -> str:
        """
        Minimal float => decimal approach. 
        Currently inserts decimal 3 places from right, then strips zeros.
        """
        if len(self.mantissa) == 1 and self.mantissa[0] == 0:
            return "0.0"

        sign_str = "-" if self.negative else ""
        num_str = str(self._chunklist_to_int(self.mantissa))

        # If not float, just return integer form (though we forced is_float = True)
        if not self.is_float:
            return sign_str + num_str

        # Insert decimal 3 places from the right (naive approach)
        if len(num_str) <= 3:
            # pad with leading zeros
            num_str = "0"*(4 - len(num_str)) + num_str

        dec_pos = len(num_str) - 3
        result = num_str[:dec_pos] + "." + num_str[dec_pos:]

        # Remove trailing zeros
        while result.endswith("0"):
            result = result[:-1]
        if result.endswith("."):
            result += "0"

        return sign_str + result

    @classmethod
    def from_value(cls, value: Union[int, float, str, List[int]]) -> "MegaFloat":
        """
        Build MegaFloat from various types: int, float, str, or list of int-limbs.
        """
        if isinstance(value, int):
            # If you truly want HPC float from an int, do str(...) or from_decimal_string
            raise ValueError("Use string inputs for higher precision when creating MegaFloat.")
        elif isinstance(value, float):
            return cls.from_decimal_string(str(value))
        elif isinstance(value, str):
            return cls.from_decimal_string(value)
        elif isinstance(value, list):
            arr = array.array(cls._chunk_code, value)
            return cls(mantissa=arr, is_float=True)
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")