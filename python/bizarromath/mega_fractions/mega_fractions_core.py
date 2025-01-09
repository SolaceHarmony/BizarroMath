from bizarromath.meganumber.mega_number import MegaNumber

class MegaFraction:
    def __init__(self, numerator: MegaNumber, denominator: MegaNumber):
        self.numerator = numerator
        self.denominator = denominator

    def add(self, other: "MegaFraction") -> "MegaFraction":
        """Add two MegaFractions"""
        new_numerator = self.numerator.mul(other.denominator).add(other.numerator.mul(self.denominator))
        new_denominator = self.denominator.mul(other.denominator)
        return MegaFraction(new_numerator, new_denominator)

    def sub(self, other: "MegaFraction") -> "MegaFraction":
        """Subtract two MegaFractions"""
        new_numerator = self.numerator.mul(other.denominator).sub(other.numerator.mul(self.denominator))
        new_denominator = self.denominator.mul(other.denominator)
        return MegaFraction(new_numerator, new_denominator)

    def mul(self, other: "MegaFraction") -> "MegaFraction":
        """Multiply two MegaFractions"""
        new_numerator = self.numerator.mul(other.numerator)
        new_denominator = self.denominator.mul(other.denominator)
        return MegaFraction(new_numerator, new_denominator)

    def div(self, other: "MegaFraction") -> "MegaFraction":
        """Divide two MegaFractions"""
        new_numerator = self.numerator.mul(other.denominator)
        new_denominator = self.denominator.mul(other.numerator)
        return MegaFraction(new_numerator, new_denominator)

    def to_meganumber(self) -> MegaNumber:
        """Convert MegaFraction to MegaNumber"""
        return self.numerator.div(self.denominator)
