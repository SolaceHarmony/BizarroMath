from .mega_number import MegaNumber

class MegaFloat(MegaNumber):
    """
    MegaFloat class for float-specific math operations.
    Inherits from MegaNumber.
    """

    def add(self, other: "MegaFloat") -> "MegaFloat":
        """
        Float addition.
        """
        if not self.is_float or not other.is_float:
            raise NotImplementedError("add is for float mode only.")
        result = self._add_chunklists(self.mantissa, other.mantissa)
        return MegaFloat(mantissa=result, negative=self.negative, is_float=True)

    def sub(self, other: "MegaFloat") -> "MegaFloat":
        """
        Float subtraction.
        """
        if not self.is_float or not other.is_float:
            raise NotImplementedError("sub is for float mode only.")
        result = self._sub_chunklists(self.mantissa, other.mantissa)
        return MegaFloat(mantissa=result, negative=self.negative, is_float=True)

    def mul(self, other: "MegaFloat") -> "MegaFloat":
        """
        Float multiplication.
        """
        if not self.is_float or not other.is_float:
            raise NotImplementedError("mul is for float mode only.")
        result = self._mul_chunklists(self.mantissa, other.mantissa, self._global_chunk_size, self._base)
        return MegaFloat(mantissa=result, negative=self.negative, is_float=True)

    def div(self, other: "MegaFloat") -> "MegaFloat":
        """
        Float division.
        """
        if not self.is_float or not other.is_float:
            raise NotImplementedError("div is for float mode only.")
        quotient, _ = self._div_chunk(self.mantissa, other.mantissa)
        return MegaFloat(mantissa=quotient, negative=self.negative, is_float=True)

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
