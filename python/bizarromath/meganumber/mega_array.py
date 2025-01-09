from typing import List
from .mega_number import MegaNumber

class MegaArray:
    def __init__(self, value: str):
        self.numbers = self._parse_comma_delimited_string(value)

    def _parse_comma_delimited_string(self, value: str):
        # Parse the comma-delimited string into an array of MegaNumber instances
        return [MegaNumber.from_decimal_string(num.strip()) for num in value.split(',')]

    @classmethod
    def from_decimal_string(cls, dec_str: str) -> "MegaArray":
        # Convert the decimal string to a MegaArray
        return cls(value=dec_str)

    def add(self, other: "MegaArray") -> "MegaArray":
        # Implement array-specific addition
        result = [a.add(b) for a, b in zip(self.numbers, other.numbers)]
        return MegaArray.from_numbers(result)

    def sub(self, other: "MegaArray") -> "MegaArray":
        # Implement array-specific subtraction
        result = [a.sub(b) for a, b in zip(self.numbers, other.numbers)]
        return MegaArray.from_numbers(result)

    def mul(self, other: "MegaArray") -> "MegaArray":
        # Implement array-specific multiplication
        result = [a.mul(b) for a, b in zip(self.numbers, other.numbers)]
        return MegaArray.from_numbers(result)

    def div(self, other: "MegaArray") -> "MegaArray":
        # Implement array-specific division
        result = [a.div(b) for a, b in zip(self.numbers, other.numbers)]
        return MegaArray.from_numbers(result)

    def to_string(self) -> str:
        # Convert the array back to a string representation
        return ','.join(num.to_decimal_string() for num in self.numbers)

    @classmethod
    def from_numbers(cls, numbers: List[MegaNumber]) -> "MegaArray":
        # Create a MegaArray from a list of MegaNumber instances
        obj = cls("")
        obj.numbers = numbers
        return obj
