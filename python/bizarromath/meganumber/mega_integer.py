from .mega_number import MegaNumber

class MegaInteger(MegaNumber):
    """
    MegaInteger class for integer-specific math operations.
    Inherits from MegaNumber.
    """

    def add(self, other: "MegaInteger") -> "MegaInteger":
        """
        Integer addition.
        """
        if self.is_float or other.is_float:
            raise NotImplementedError("add is for integer mode only.")
        result = self._add_chunklists(self.mantissa, other.mantissa)
        return MegaInteger(mantissa=result, negative=self.negative)

    def sub(self, other: "MegaInteger") -> "MegaInteger":
        """
        Integer subtraction.
        """
        if self.is_float or other.is_float:
            raise NotImplementedError("sub is for integer mode only.")
        result = self._sub_chunklists(self.mantissa, other.mantissa)
        return MegaInteger(mantissa=result, negative=self.negative)

    def mul(self, other: "MegaInteger") -> "MegaInteger":
        """
        Integer multiplication.
        """
        if self.is_float or other.is_float:
            raise NotImplementedError("mul is for integer mode only.")
        result = self._mul_chunklists(self.mantissa, other.mantissa, self._global_chunk_size, self._base)
        return MegaInteger(mantissa=result, negative=self.negative)

    def div(self, other: "MegaInteger") -> "MegaInteger":
        """
        Integer division.
        """
        if self.is_float or other.is_float:
            raise NotImplementedError("div is for integer mode only.")
        quotient, _ = self._div_chunk(self.mantissa, other.mantissa)
        return MegaInteger(mantissa=quotient, negative=self.negative)

    def pow(self, exponent: "MegaInteger") -> "MegaInteger":
        """
        Integer exponentiation.
        """
        if self.is_float or exponent.is_float:
            raise NotImplementedError("pow is for integer mode only.")
        result = self._int_to_chunklist(1, self._global_chunk_size)
        base = self.mantissa[:]
        exp = self._chunklist_to_int(exponent.mantissa)
        while exp > 0:
            if exp % 2 == 1:
                result = self._mul_chunklists(result, base, self._global_chunk_size, self._base)
            base = self._mul_chunklists(base, base, self._global_chunk_size, self._base)
            exp //= 2
        return MegaInteger(mantissa=result, negative=self.negative)

    def sqrt(self) -> "MegaInteger":
        """
        Integer square root.
        """
        if self.is_float:
            raise NotImplementedError("sqrt is for integer mode only.")
        x = self._chunklist_to_int(self.mantissa)
        y = int(x ** 0.5)
        result = self._int_to_chunklist(y, self._global_chunk_size)
        return MegaInteger(mantissa=result, negative=self.negative)

    @classmethod
    def from_value(cls, value: Union[int, str, List[int]]) -> "MegaInteger":
        """
        Create a MegaInteger from a given value.
        """
        if isinstance(value, int):
            raise ValueError("Use string inputs for higher precision.")
        elif isinstance(value, str):
            return cls.from_decimal_string(value)
        elif isinstance(value, list):
            return cls(mantissa=value)
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
