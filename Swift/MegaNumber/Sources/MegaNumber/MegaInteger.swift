//
//  MegaInteger.swift
//  MegaNumber
//
//  Created by Sydney Renee on 1/9/25.
//

import Foundation

// MARK: - MegaInteger

/// Represents an arbitrary-precision integer.
public class MegaInteger: MegaNumber {
    
    // MARK: - Initializers
    
    /// Initializes a new `MegaInteger` with specified parameters.
    ///
    /// - Parameters:
    ///   - mantissa: The mantissa in chunk-limbs form.
    ///   - exponent: The exponent in chunk-limbs form (should be `[0]` for integers).
    ///   - negative: Indicates if the number is negative.
    ///   - isFloat: Indicates if the number is a floating-point number (should be `false` for integers).
    ///   - exponentNegative: Indicates if the exponent is negative.
    public override init(
        mantissa: [Int] = [0],
        exponent: [Int] = [0],
        negative: Bool = false,
        isFloat: Bool = false, // Always integer
        exponentNegative: Bool = false
    ) {
        super.init(
            mantissa: mantissa,
            exponent: [0], // Exponent is zero for integers
            negative: negative,
            isFloat: false,  // Always integer
            exponentNegative: false
        )
    }
    
    /// Convenience initializer to create a `MegaInteger` from a decimal string.
    ///
    /// - Parameter decimalStr: The decimal string representation of the integer (e.g., "123456789").
    public convenience init(_ decimalStr: String) {
        let tmp = MegaNumber.from_decimal_string(decimalStr)
        self.init(
            mantissa: tmp.mantissa,
            exponent: [0], // Exponent is zero for integers
            negative: tmp.negative,
            isFloat: false,
            exponentNegative: false
        )
    }
    
    /// Creates a `MegaInteger` instance from a decimal string specifically as an integer.
    ///
    /// - Parameter s: The decimal string representation of the integer.
    /// - Returns: A new `MegaInteger` instance.
    public override class func from_decimal_string(_ s: String) -> MegaInteger {
        let baseNum = MegaNumber.from_decimal_string(s)
        // Force exponent to zero
        return MegaInteger(
            mantissa: baseNum.mantissa,
            exponent: [0],
            negative: baseNum.negative,
            isFloat: false,
            exponentNegative: false
        )
    }
    
    /// Creates a `MegaInteger` instance from an Int.
    ///
    /// - Parameter val: The integer value to initialize with.
    /// - Returns: A new `MegaInteger` instance.
    public class func from_int(_ val: Int) -> MegaInteger {
        let limbs = intToChunks(val)
        let negative = val < 0
        return MegaInteger(
            mantissa: limbs,
            exponent: [0],
            negative: negative,
            isFloat: false,
            exponentNegative: false
        )
    }
    
    // MARK: - Overridden Float Arithmetic Methods to Prevent Their Use
    
    /// Overrides the base class's `addFloat` to prevent floating-point addition in integer context.
    ///
    /// - Parameter other: The `MegaNumber` to add.
    /// - Returns: Never returns; always throws a runtime error.
    public override func addFloat(_ other: MegaNumber) -> MegaNumber {
        fatalError("MegaInteger cannot perform floating-point addition.")
    }
    
    /// Overrides the base class's `mulFloat` to prevent floating-point multiplication in integer context.
    ///
    /// - Parameter other: The `MegaNumber` to multiply with.
    /// - Returns: Never returns; always throws a runtime error.
    public override func mulFloat(_ other: MegaNumber) -> MegaNumber {
        fatalError("MegaInteger cannot perform floating-point multiplication.")
    }
    
    /// Overrides the base class's `divFloat` to prevent floating-point division in integer context.
    ///
    /// - Parameter other: The `MegaNumber` to divide by.
    /// - Returns: Never returns; always throws a runtime error.
    public override func divFloat(_ other: MegaNumber) -> MegaNumber {
        fatalError("MegaInteger cannot perform floating-point division.")
    }
    
    /// Overrides the base class's `sqrtFloat` to prevent floating-point square root in integer context.
    ///
    /// - Returns: Never returns; always throws a runtime error.
    public override func sqrtFloat() -> MegaNumber {
        fatalError("MegaInteger cannot perform floating-point square root.")
    }
    
    // MARK: - Overridden Arithmetic Methods for Type Safety
    
    /// Adds another `MegaNumber` to this `MegaInteger`. Only allows addition with another `MegaInteger`.
    ///
    /// - Parameter other: The `MegaNumber` to add.
    /// - Returns: A new `MegaInteger` representing the sum.
    public override func add(_ other: MegaNumber) -> MegaNumber {
        guard let otherInt = other as? MegaInteger else {
            fatalError("MegaInteger can only be added to another MegaInteger.")
        }
        let sumMant = MegaNumber.addChunks(self.mantissa, otherInt.mantissa)
        let result = MegaInteger(
            mantissa: sumMant,
            exponent: [0],
            negative: self.negative,
            isFloat: false,
            exponentNegative: false
        )
        result.normalize()
        return result
    }
    
    /// Subtracts another `MegaNumber` from this `MegaInteger`. Only allows subtraction with another `MegaInteger`.
    ///
    /// - Parameter other: The `MegaNumber` to subtract.
    /// - Returns: A new `MegaInteger` representing the difference.
    public override func sub(_ other: MegaNumber) -> MegaNumber {
        guard let otherInt = other as? MegaInteger else {
            fatalError("MegaInteger can only subtract another MegaInteger.")
        }
        let diffMant = try! MegaNumber.subChunks(self.mantissa, otherInt.mantissa)
        let result = MegaInteger(
            mantissa: diffMant,
            exponent: [0],
            negative: self.negative,
            isFloat: false,
            exponentNegative: false
        )
        result.normalize()
        return result
    }
    
    /// Multiplies this `MegaInteger` with another `MegaNumber`. Only allows multiplication with another `MegaInteger`.
    ///
    /// - Parameter other: The `MegaNumber` to multiply with.
    /// - Returns: A new `MegaInteger` representing the product.
    public override func mul(_ other: MegaNumber) -> MegaNumber {
        guard let otherInt = other as? MegaInteger else {
            fatalError("MegaInteger can only multiply with another MegaInteger.")
        }
        let productMant = MegaNumber.mulChunksStandard(self.mantissa, otherInt.mantissa)
        let sign = (self.negative != otherInt.negative)
        let result = MegaInteger(
            mantissa: productMant,
            exponent: [0],
            negative: sign,
            isFloat: false,
            exponentNegative: false
        )
        result.normalize()
        return result
    }
    
    /// Divides this `MegaInteger` by another `MegaNumber`. Only allows division with another `MegaInteger`.
    ///
    /// - Parameter other: The `MegaNumber` to divide by.
    /// - Returns: A new `MegaInteger` representing the quotient.
    public override func div(_ other: MegaNumber) -> MegaNumber {
        guard let otherInt = other as? MegaInteger else {
            fatalError("MegaInteger can only divide by another MegaInteger.")
        }
        // Check for division by zero
        if otherInt.mantissa.count == 1 && otherInt.mantissa[0] == 0 {
            fatalError("Division by zero is not allowed.")
        }
        let sign = (self.negative != otherInt.negative)
        let comparison = MegaNumber.compareAbs(self.mantissa, otherInt.mantissa)
        if comparison < 0 {
            // Self < Other => quotient is 0
            return MegaInteger(
                mantissa: [0],
                exponent: [0],
                negative: false,
                isFloat: false,
                exponentNegative: false
            )
        } else if comparison == 0 {
            // Self == Other => quotient is 1 or -1 based on sign
            return MegaInteger(
                mantissa: [1],
                exponent: [0],
                negative: sign,
                isFloat: false,
                exponentNegative: false
            )
        } else {
            let (quotient, _) = try! self.divChunks(self.mantissa, otherInt.mantissa)
            let result = MegaInteger(
                mantissa: quotient,
                exponent: [0],
                negative: sign,
                isFloat: false,
                exponentNegative: false
            )
            result.normalize()
            return result
        }
    }
    
    /// Computes the square root of this `MegaInteger`.
    ///
    /// - Returns: A new `MegaInteger` representing the square root.
    public override func sqrt() -> MegaNumber {
        // Ensure integer square root
        let sqrtMant = try! sqrtChunks(self.mantissa)
        let result = MegaInteger(
            mantissa: sqrtMant,
            exponent: [0],
            negative: false,
            isFloat: false,
            exponentNegative: false
        )
        result.normalize()
        return result
    }
    
    // MARK: - Additional Integer-Specific Methods
    
    /// Negates the integer.
    ///
    /// - Returns: A new `MegaInteger` representing the negated value.
    public override func negate() -> MegaInteger {
        return MegaInteger(
            mantissa: mantissa,
            exponent: [0],
            negative: !self.negative,
            isFloat: false,
            exponentNegative: false
        )
    }
    
    /// Computes the modulo of this integer with another.
    ///
    /// - Parameter other: The `MegaInteger` to modulo with.
    /// - Returns: A new `MegaInteger` representing the result.
    public func mod(_ other: MegaInteger) -> MegaInteger {
        do {
            let (_, remainder) = try self.divChunks(self.mantissa, other.mantissa)
            return MegaInteger(
                mantissa: remainder,
                exponent: [0],
                negative: self.negative,
                isFloat: false,
                exponentNegative: false
            )
        } catch {
            fatalError("Modulo by zero is not allowed.")
        }
    }
    /// Creates a copy of the current MegaInteger instance.
    ///
    /// - Returns: A new `MegaInteger` instance with the same properties.
    public override func copy() -> MegaNumber {
        return MegaInteger(
            mantissa: self.mantissa,
            exponent: self.exponent, // Exponent is always zero for integers
            negative: self.negative,
            isFloat: self.isFloat,
            exponentNegative: self.exponentNegative
        )
    }
    /// Computes the exponentiation of this integer to a non-negative power.
    ///
    /// - Parameter power: The non-negative power to raise the integer to.
    /// - Returns: A new `MegaInteger` representing the result.
    public func pow(_ power: MegaInteger) -> MegaInteger {
        var result = MegaInteger.from_int(1)
        var base = self.copy() as! MegaInteger
        var exp = power
        
        while exp > 0 {
            if exp % 2 == 1 {
                result = result.mul(base)
            }
            base = base.mul(base)
            exp /= 2
        }
        
        return result
    }
    
    /// Performs a bitwise AND operation with another `MegaInteger`.
    ///
    /// - Parameter other: The `MegaInteger` to perform the AND with.
    /// - Returns: A new `MegaInteger` representing the result.
    public func and(_ other: MegaInteger) -> MegaInteger {
        let minCount = min(self.mantissa.count, other.mantissa.count)
        var resultMantissa: [Int] = []
        
        for i in 0..<minCount {
            resultMantissa.append(self.mantissa[i] & other.mantissa[i])
        }
        // If self has more limbs, append the remaining (AND with 0 would be 0)
        if self.mantissa.count > minCount {
            for _ in minCount..<self.mantissa.count {
                resultMantissa.append(0)
            }
        }
        // Similarly, if other has more limbs, append 0s
        if other.mantissa.count > minCount {
            for _ in minCount..<other.mantissa.count {
                resultMantissa.append(0)
            }
        }
        return MegaInteger(
            mantissa: resultMantissa,
            exponent: [0],
            negative: self.negative && other.negative,
            isFloat: false,
            exponentNegative: false
        )
    }
    
    /// Performs a bitwise OR operation with another `MegaInteger`.
    ///
    /// - Parameter other: The `MegaInteger` to perform the OR with.
    /// - Returns: A new `MegaInteger` representing the result.
    public func or(_ other: MegaInteger) -> MegaInteger {
        let maxCount = max(self.mantissa.count, other.mantissa.count)
        var resultMantissa: [Int] = []
        
        for i in 0..<maxCount {
            let a = i < self.mantissa.count ? self.mantissa[i] : 0
            let b = i < other.mantissa.count ? other.mantissa[i] : 0
            resultMantissa.append(a | b)
        }
        return MegaInteger(
            mantissa: resultMantissa,
            exponent: [0],
            negative: self.negative || other.negative,
            isFloat: false,
            exponentNegative: false
        )
    }
    
    /// Performs a bitwise XOR operation with another `MegaInteger`.
    ///
    /// - Parameter other: The `MegaInteger` to perform the XOR with.
    /// - Returns: A new `MegaInteger` representing the result.
    public func xor(_ other: MegaInteger) -> MegaInteger {
        let maxCount = max(self.mantissa.count, other.mantissa.count)
        var resultMantissa: [Int] = []
        
        for i in 0..<maxCount {
            let a = i < self.mantissa.count ? self.mantissa[i] : 0
            let b = i < other.mantissa.count ? other.mantissa[i] : 0
            resultMantissa.append(a ^ b)
        }
        return MegaInteger(
            mantissa: resultMantissa,
            exponent: [0],
            negative: self.negative != other.negative,  // XOR sign
            isFloat: false,
            exponentNegative: false
        )
    }
    
    /// Performs a bitwise NOT operation on the integer.
    ///
    /// - Returns: A new `MegaInteger` representing the bitwise NOT of the original integer.
    public func bitwiseNot() -> MegaInteger {
        let maxCount = mantissa.count
        var resultMantissa: [Int] = []
        for limb in mantissa {
            resultMantissa.append(~limb & MegaNumberConstants.mask)
        }
        return MegaInteger(
            mantissa: resultMantissa,
            exponent: [0],
            negative: !self.negative,
            isFloat: false,
            exponentNegative: false
        )
    }
    
    /// Performs a right shift by a specified number of bits.
    ///
    /// - Parameter bits: The number of bits to shift.
    /// - Returns: A new `MegaInteger` representing the shifted value.
    public func rightShift(_ bits: Int) -> MegaInteger {
        let chunkShift = bits / MegaNumberConstants.globalChunkSize
        let bitShift = bits % MegaNumberConstants.globalChunkSize
        var shifted = self.shiftRight(mantissa, chunkShift)
        if bitShift > 0 {
            var carry = 0
            for i in (0..<shifted.count).reversed() {
                let newVal = (shifted[i] >> bitShift) | (carry << (MegaNumberConstants.globalChunkSize - bitShift))
                carry = shifted[i] & ((1 << bitShift) - 1)
                shifted[i] = newVal & MegaNumberConstants.mask
            }
            // Trim trailing zeros
            while shifted.count > 1 && shifted.last == 0 {
                shifted.removeLast()
            }
        }
        return MegaInteger(
            mantissa: shifted,
            exponent: [0],
            negative: self.negative,
            isFloat: false,
            exponentNegative: false
        )
    }
    
    /// Computes the greatest common divisor (GCD) of this integer and another.
    ///
    /// - Parameter other: The `MegaInteger` to compute the GCD with.
    /// - Returns: A new `MegaInteger` representing the GCD.
    public func gcd(_ other: MegaInteger) -> MegaInteger {
        var a = self.copy() as! MegaInteger
        var b = other.copy() as! MegaInteger
        while !(b.mantissa.count == 1 && b.mantissa[0] == 0) {
            let r = a.mod(b)
            a = b
            b = r
        }
        return a
    }
    
    /// Computes the least common multiple (LCM) of this integer and another.
    ///
    /// - Parameter other: The `MegaInteger` to compute the LCM with.
    /// - Returns: A new `MegaInteger` representing the LCM.
    public func lcm(_ other: MegaInteger) -> MegaInteger {
        let gcdValue = self.gcd(other)
        return (self.mul(other)).div(gcdValue) as! MegaInteger
    }
    
    // MARK: - Log2 Implementation
    
    /// Computes the binary logarithm (log2) of the `MegaInteger`.
    ///
    /// - Returns: A new `MegaInteger` representing floor(log2(N)).
    /// - Throws: An error if the number is zero or negative.
    public func log2() throws -> MegaInteger {
        // Handle zero and negative numbers
        if mantissa.count == 1 && mantissa[0] == 0 {
            throw NSError(domain: "LogarithmError", code: 1, userInfo: [NSLocalizedDescriptionKey: "Cannot compute log2 of zero."])
        }
        if self.negative {
            throw NSError(domain: "LogarithmError", code: 2, userInfo: [NSLocalizedDescriptionKey: "Cannot compute log2 of a negative number."])
        }
        
        // Compute log2(mantissa)
        let log2Mantissa = try self.log2Integer()
        
        // Compute log2(BASE) = globalChunkSize
        let log2Base = MegaNumber.intToChunks(MegaNumberConstants.globalChunkSize)
        
        // Since MegaInteger represents integers only, exponent is zero
        // Total log2(N) = log2(mantissa)
        let totalLog2 = log2Mantissa
        
        return totalLog2
    }
    
    /// Computes the integer part of log2(mantissa).
    ///
    /// - Returns: A new `MegaInteger` representing floor(log2(mantissa)).
    /// - Throws: An error if mantissa is zero.
    private func log2Integer() throws -> MegaInteger {
        // Initialize log2 to zero
        var log2 = MegaInteger.from_int(0)
        
        // Iterate from the most significant chunk to the least
        for chunkIndex in stride(from: mantissa.count - 1, through: 0, by: -1) {
            let chunk = mantissa[chunkIndex]
            if chunk == 0 {
                continue
            }
            // Find the highest set bit in this chunk
            let highestBit = highestSetBit(in: chunk)
            // Calculate log2 contribution from this chunk
            let chunkLog2 = MegaInteger.from_int(chunkIndex * MegaNumberConstants.globalChunkSize + highestBit)
            log2 = chunkLog2
            break
        }
        
        return log2
    }
    
    /// Finds the position of the highest set bit in an integer.
    ///
    /// - Parameter x: The integer to inspect.
    /// - Returns: The zero-based position of the highest set bit.
    private func highestSetBit(in x: Int) -> Int {
        var value = x
        var pos = 0
        while value > 1 {
            value >>= 1
            pos += 1
        }
        return pos
    }
    
    /// Creates a `MegaInteger` from a single integer.
    ///
    /// - Parameter val: The integer value.
    /// - Returns: A new `MegaInteger` instance.
    internal class func fromInt(_ val: Int) -> MegaInteger {
        return MegaInteger.from_int(val)
    }
    
    // MARK: - Description
    
    /// Provides a textual representation of the `MegaInteger`.
    public override var description: String {
        return "<MegaInteger \(to_decimal_string())>"
    }
}
