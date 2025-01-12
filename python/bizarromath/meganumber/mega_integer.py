import array
from typing import List, Union, TYPE_CHECKING
from .mega_number import MegaNumber

if TYPE_CHECKING:
    from .mega_float import MegaFloat


class MegaInteger(MegaNumber):
    """
    MegaInteger class for integer-specific math operations.
    Inherits from MegaNumber, but always enforces integer mode (is_float=False).
    """

    def __init__(
        self,
        value=None,
        mantissa=None,
        exponent=None,
        negative=False,
        is_float=False,       # Will ignore this and force False
        exponent_negative=False
    ):
        # If user passes a string, parse as decimal:
        if isinstance(value, str):
            result = MegaInteger.from_decimal_string(value)
            self.mantissa = result.mantissa
            self.exponent = result.exponent
            self.negative = result.negative
            self.is_float = False  # Always integer
            self.exponent_negative = result.exponent_negative
            return

        # For normal constructor usage (no string in 'value'):
        if mantissa is None:
            # Use array of the parent's chosen chunk type (Q or L)
            mantissa = array.array(self._chunk_code, [0])
        if exponent is None:
            exponent = array.array(self._chunk_code, [0])

        super().__init__(
            mantissa=mantissa,
            exponent=exponent,
            negative=negative,
            is_float=False,  # Always integer mode
            exponent_negative=exponent_negative
        )

    def add(self, other: "MegaInteger") -> "MegaInteger":
        """
        Integer addition.
        """
        if self.is_float or other.is_float:
            raise NotImplementedError("add() is for integer mode only.")

        # Combine the limb arrays
        result = self._add_chunklists(self.mantissa, other.mantissa)
        # Construct a new MegaInteger with the same sign logic
        # We'll pick sign = self.negative if they share sign, etc.
        # But for a minimal approach, assume sign is self.negative
        # If you want to handle sign collisions, do it like in MegaNumber.
        return MegaInteger(
            mantissa=result,
            negative=self.negative
        )

    def sub(self, other: "MegaInteger") -> "MegaInteger":
        """
        Integer subtraction.
        """
        if self.is_float or other.is_float:
            raise NotImplementedError("sub() is for integer mode only.")

        # Minimal approach: directly call _sub_chunklists
        # If you need sign handling, adapt from MegaNumber's logic
        result = self._sub_chunklists(self.mantissa, other.mantissa)
        return MegaInteger(
            mantissa=result,
            negative=self.negative
        )

    def mul(self, other: Union["MegaInteger", "MegaFloat"]) -> Union["MegaInteger", "MegaFloat"]:
        """
        Integer multiplication. If 'other' is MegaFloat, forward to MegaFloat logic.
        """
        from .mega_float import MegaFloat  # Avoid circular imports at top

        if isinstance(other, MegaFloat):
            # Delegate float multiplication to MegaFloat's .mul()
            # so it can handle exponent logic.
            return other.mul(self)

        # Both sides are integer => normal chunk-based multiply
        out_limb = self._mul_chunklists(
            self.mantissa,
            other.mantissa,
            self._global_chunk_size,
            self._base
        )
        # XOR the sign bits to get the new sign
        new_sign = (self.negative != other.negative)
        return MegaInteger(mantissa=out_limb, negative=new_sign)

    def div(self, other: "MegaInteger") -> "MegaInteger":
        """
        Integer division (floor division).
        """
        if self.is_float or other.is_float:
            raise NotImplementedError("div() is for integer mode only.")

        # Normal chunk-based division
        q, _ = self._div_chunk(self.mantissa, other.mantissa)
        return MegaInteger(
            mantissa=q,
            negative=self.negative
        )

    def pow(self, exponent: "MegaInteger") -> "MegaInteger":
        """
        Integer exponentiation by repeated squaring (exponent must be >= 0).
        """
        if self.is_float or exponent.is_float:
            raise NotImplementedError("pow() is for integer mode only.")

        # Build chunk-limb array "1"
        result = self._int_to_chunklist(1, self._global_chunk_size)
        base = self.mantissa[:]
        exp_val = self._chunklist_to_int(exponent.mantissa)

        while exp_val > 0:
            if (exp_val & 1) == 1:
                result = self._mul_chunklists(result, base, self._global_chunk_size, self._base)
            base = self._mul_chunklists(base, base, self._global_chunk_size, self._base)
            exp_val >>= 1

        return MegaInteger(
            mantissa=result,
            negative=self.negative
        )

    def sqrt(self) -> "MegaInteger":
        """
        Integer square root (approx floor sqrt).
        """
        if self.is_float:
            raise NotImplementedError("sqrt() is for integer mode only.")

        # Minimal approach: convert to Python int, do sqrt, convert back
        x = self._chunklist_to_int(self.mantissa)
        y = int(x**0.5)
        result = self._int_to_chunklist(y, self._global_chunk_size)
        return MegaInteger(
            mantissa=result,
            negative=self.negative
        )

    def __repr__(self):
        return f"<MegaInteger {self.to_decimal_string(50)}>"

    @classmethod
    def from_value(cls, value: Union[int, str, List[int]]) -> "MegaInteger":
        """
        Create a MegaInteger from an int, str, or list of int-limbs (older style).
        """
        if isinstance(value, int):
            # If user wants direct int => they can do .from_int(...) or .from_decimal_string(str(value)).
            raise ValueError("Use string inputs for higher precision or .from_int() method.")
        elif isinstance(value, str):
            return cls.from_decimal_string(value)
        elif isinstance(value, list):
            # Convert the Python list => array.array of the correct chunk type
            import array
            arr = array.array(cls._chunk_code, value)
            return cls(mantissa=arr)
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")