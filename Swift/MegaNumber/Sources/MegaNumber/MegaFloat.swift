//
//  MegaFloat.swift
//  MegaNumber
//
//  Created by Sydney Bach on 1/9/25.
//

import Foundation

/// Represents an arbitrary-precision floating-point number.
public class MegaFloat: MegaNumber {
    
    // MARK: - Initializers
    
    /// Initializes a new `MegaFloat` with specified parameters.
    ///
    /// - Parameters:
    ///   - mantissa: The mantissa in chunk-limbs form.
    ///   - exponent: The exponent in chunk-limbs form.
    ///   - negative: Indicates if the number is negative.
    ///   - isFloat: Indicates if the number is a floating-point number (should be `true`).
    ///   - exponentNegative: Indicates if the exponent is negative.
    public override init(
        mantissa: [Int] = [0],
        exponent: [Int] = [0],
        negative: Bool = false,
        isFloat: Bool = true,
        exponentNegative: Bool = false
    ) {
        super.init(
            mantissa: mantissa,
            exponent: exponent,
            negative: negative,
            isFloat: true,
            exponentNegative: exponentNegative
        )
    }

    /// Convenience initializer to create a `MegaFloat` from a decimal string.
    ///
    /// - Parameter decimalStr: The decimal string representation of the number (e.g., "123.456").
    public convenience init(_ decimalStr: String) {
        let tmp = MegaNumber.from_decimal_string(decimalStr)
        self.init(
            mantissa: tmp.mantissa,
            exponent: tmp.exponent,
            negative: tmp.negative,
            isFloat: true,
            exponentNegative: tmp.exponentNegative
        )
    }

    /// Convenience initializer to create a `MegaFloat` from a base `MegaNumber`.
    /// Copies its mantissa, exponent, sign, etc., but forces `isFloat=true`.
    public convenience init(_ source: MegaNumber) {
        self.init(
            mantissa: source.mantissa,
            exponent: source.exponent,
            negative: source.negative,
            isFloat: true,
            exponentNegative: source.exponentNegative
        )
    }

    /// Creates a `MegaFloat` instance from a decimal string specifically as a float.
    ///
    /// - Parameter s: The decimal string representation of the number.
    /// - Returns: A new `MegaFloat` instance.
    public override class func from_decimal_string(_ s: String) -> MegaFloat {
        let baseNum = MegaNumber.from_decimal_string(s)
        return MegaFloat(baseNum)
    }

    /// Provides a textual representation of the `MegaFloat`.
    public override var description: String {
        return "<MegaFloat \(to_decimal_string())>"
    }

    // MARK: - Overridden Float Arithmetic Methods

    /// Adds another `MegaNumber` to this `MegaFloat`. Returns `MegaFloat`.
    public override func addFloat(_ other: MegaNumber) -> MegaFloat {
        let baseResult = super.addFloat(other) // returns MegaNumber
        return MegaFloat(baseResult)
    }

    /// Multiplies this `MegaFloat` with another `MegaNumber`. Returns `MegaFloat`.
    public override func mulFloat(_ other: MegaNumber) -> MegaFloat {
        let baseResult = super.mulFloat(other)
        return MegaFloat(baseResult)
    }

    /// Divides this `MegaFloat` by another `MegaNumber`. Returns `MegaFloat`.
    public override func divFloat(_ other: MegaNumber) -> MegaFloat {
        let baseResult = super.divFloat(other)
        return MegaFloat(baseResult)
    }

    /// Computes the square root of this `MegaFloat`. Returns `MegaFloat`.
    public override func sqrtFloat() -> MegaFloat {
        let baseResult = super.sqrtFloat()
        return MegaFloat(baseResult)
    }

    // (Optional) If you want to ensure all ops returning MegaFloat:
    public override func add(_ other: MegaNumber) -> MegaNumber {
        let baseResult = super.add(other)
        return MegaFloat(baseResult)
    }

    public override func sub(_ other: MegaNumber) -> MegaNumber {
        let baseResult = super.sub(other)
        return MegaFloat(baseResult)
    }

    public override func mul(_ other: MegaNumber) -> MegaNumber {
        let baseResult = super.mul(other)
        return MegaFloat(baseResult)
    }

    public override func div(_ other: MegaNumber) -> MegaNumber {
        let baseResult = super.div(other)
        return MegaFloat(baseResult)
    }

    public override func sqrt() -> MegaNumber {
        let baseResult = super.sqrt()
        return MegaFloat(baseResult)
    }
}
