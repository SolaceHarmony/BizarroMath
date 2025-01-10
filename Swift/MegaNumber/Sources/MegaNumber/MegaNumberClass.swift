import Foundation

/// Class representing a large number with arbitrary chunk sizes
public class MegaNumberClass {
    // MARK: - Static Properties for Chunk Management
    
    /// Current chunk size in bits (configurable at runtime)
    public static var currentChunkSize: Int = 32 // Default chunk size
    
    /// Base value based on chunk size
    public static var base: UInt64 {
        // Ensure chunk size is less than 64 to prevent undefined behavior
        guard currentChunkSize < 64 else {
            return 0 // Alternatively, handle as needed
        }
        return 1 << currentChunkSize
    }
    
    /// Mask based on chunk size
    public static var mask: UInt64 {
        guard currentChunkSize < 64 else {
            return UInt64.max
        }
        return base - 1
    }
    
    // MARK: - Instance Properties
    
    /// Mantissa chunks (Little Endian: index 0 is least significant)
    public var mantissa: [AnyChunk]
    
    /// Exponent chunks
    public var exponent: [AnyChunk]
    
    /// Sign flag
    public var isNegative: Bool
    
    /// Float flag
    public var isFloat: Bool
    
    /// Exponent negative flag
    public var exponentNegative: Bool
    
    // MARK: - Initializer
    
    /// Initialize a MegaNumberClass
    /// - Parameters:
    ///   - mantissa: Mantissa chunks
    ///   - exponent: Exponent chunks
    ///   - isNegative: Sign flag
    ///   - isFloat: Float flag
    ///   - exponentNegative: Exponent negative flag
    public init(
        mantissa: [AnyChunk] = [AnyChunk(UInt64(0))],
        exponent: [AnyChunk] = [AnyChunk(UInt64(0))],
        isNegative: Bool = false,
        isFloat: Bool = false,
        exponentNegative: Bool = false
    ) {
        self.mantissa = mantissa
        self.exponent = exponent
        self.isNegative = isNegative
        self.isFloat = isFloat
        self.exponentNegative = exponentNegative
        self.normalize()
    }
    
    // MARK: - Normalization
    
    /// Normalize the MegaNumberClass (remove trailing zeros, fix signs)
    public func normalize() {
        // Remove trailing zero chunks from mantissa
        while mantissa.count > 1 && mantissa.last!.asUInt64 == 0 {
            mantissa.removeLast()
        }
        
        // Remove trailing zero chunks from exponent if float
        if isFloat {
            while exponent.count > 1 && exponent.last!.asUInt64 == 0 {
                exponent.removeLast()
            }
        }
        
        // Handle zero case
        if mantissa.count == 1 && mantissa.first!.asUInt64 == 0 {
            isNegative = false
            exponent = [AnyChunk(UInt64(0))]
            exponentNegative = false
        }
    }
    
    // MARK: - Arithmetic Operations
    
    /// Add another MegaNumberClass to this instance
    /// - Parameter other: The MegaNumberClass to add
    /// - Throws: An error if float addition is not implemented
    /// - Returns: A new MegaNumberClass representing the sum
    public func add(_ other: MegaNumberClass) throws -> MegaNumberClass {
        var result = MegaNumberClass()
        
        if self.isFloat || other.isFloat {
            return try self.addFloat(other)
        }
        
        if self.isNegative == other.isNegative {
            let sumMantissa = MegaNumberClass.addChunkLists(self.mantissa, other.mantissa)
            result = MegaNumberClass(
                mantissa: sumMantissa,
                exponent: [AnyChunk(UInt64(0))],
                isNegative: self.isNegative,
                isFloat: false,
                exponentNegative: false
            )
        } else {
            let comparison = MegaNumberClass.compareChunkLists(self.mantissa, other.mantissa)
            if comparison == .orderedSame {
                return MegaNumberClass()
            } else if comparison == .orderedDescending {
                let diffMantissa = try MegaNumberClass.subtractChunkLists(self.mantissa, other.mantissa)
                result = MegaNumberClass(
                    mantissa: diffMantissa,
                    exponent: [AnyChunk(UInt64(0))],
                    isNegative: self.isNegative,
                    isFloat: false,
                    exponentNegative: false
                )
            } else {
                let diffMantissa = try MegaNumberClass.subtractChunkLists(other.mantissa, self.mantissa)
                result = MegaNumberClass(
                    mantissa: diffMantissa,
                    exponent: [AnyChunk(UInt64(0))],
                    isNegative: other.isNegative,
                    isFloat: false,
                    exponentNegative: false
                )
            }
        }
        
        result.normalize()
        return result
    }
    
    /// Subtract another MegaNumberClass from this instance
    /// - Parameter other: The MegaNumberClass to subtract
    /// - Throws: An error if float subtraction is not implemented
    /// - Returns: A new MegaNumberClass representing the difference
    public func subtract(_ other: MegaNumberClass) throws -> MegaNumberClass {
        var negatedOther = other
        negatedOther.isNegative.toggle()
        return try self.add(negatedOther)
    }
    
    /// Multiply this MegaNumberClass by another
    /// - Parameter other: The MegaNumberClass to multiply by
    /// - Throws: An error if float multiplication is not implemented
    /// - Returns: A new MegaNumberClass representing the product
    public func multiply(by other: MegaNumberClass) throws -> MegaNumberClass {
        var result = MegaNumberClass()
        
        if self.isFloat || other.isFloat {
            return try self.multiplyFloat(other)
        }
        
        let productMantissa = try MegaNumberClass.multiplyChunkLists(self.mantissa, other.mantissa)
        let isNegativeResult = self.isNegative != other.isNegative
        result = MegaNumberClass(
            mantissa: productMantissa,
            exponent: [AnyChunk(UInt64(0))],
            isNegative: isNegativeResult,
            isFloat: false,
            exponentNegative: false
        )
        
        result.normalize()
        return result
    }
    
    // MARK: - Floating-Point Operations (Placeholders)
    
    /// Add another MegaNumberClass as floating-point
    /// - Parameter other: The MegaNumberClass to add
    /// - Throws: An error indicating not implemented
    /// - Returns: A new MegaNumberClass representing the sum
    private func addFloat(_ other: MegaNumberClass) throws -> MegaNumberClass {
        // Implement floating-point addition logic here
        throw NSError(domain: "NotImplemented", code: 1, userInfo: [NSLocalizedDescriptionKey: "Floating-point addition is not implemented yet."])
    }
    
    /// Multiply another MegaNumberClass as floating-point
    /// - Parameter other: The MegaNumberClass to multiply by
    /// - Throws: An error indicating not implemented
    /// - Returns: A new MegaNumberClass representing the product
    private func multiplyFloat(_ other: MegaNumberClass) throws -> MegaNumberClass {
        // Implement floating-point multiplication logic here
        throw NSError(domain: "NotImplemented", code: 2, userInfo: [NSLocalizedDescriptionKey: "Floating-point multiplication is not implemented yet."])
    }
    
    // MARK: - Utility Methods
    
    /// Add two chunk lists
    /// - Parameters:
    ///   - a: First chunk list
    ///   - b: Second chunk list
    /// - Returns: A new chunk list representing the sum
    public static func addChunkLists(_ a: [AnyChunk], _ b: [AnyChunk]) -> [AnyChunk] {
        let maxLength = max(a.count, b.count)
        var result: [AnyChunk] = []
        var carry: UInt64 = 0
        
        for i in 0..<maxLength {
            let aVal = i < a.count ? a[i].asUInt64 : 0
            let bVal = i < b.count ? b[i].asUInt64 : 0
            let sum = aVal &+ bVal &+ carry
            let maskedSum = sum & mask
            result.append(AnyChunk(maskedSum))
            carry = sum >> currentChunkSize
        }
        
        if carry > 0 {
            result.append(AnyChunk(carry))
        }
        
        return result
    }
    
    /// Subtract two chunk lists (a >= b)
    /// - Parameters:
    ///   - a: First chunk list
    ///   - b: Second chunk list
    /// - Throws: An error if a < b
    /// - Returns: A new chunk list representing the difference
    public static func subtractChunkLists(_ a: [AnyChunk], _ b: [AnyChunk]) throws -> [AnyChunk] {
        precondition(a.count >= b.count, "Cannot subtract a larger number from a smaller one.")
        var result: [AnyChunk] = []
        var borrow: UInt64 = 0
        
        for i in 0..<a.count {
            let aVal = a[i].asUInt64
            let bVal = i < b.count ? b[i].asUInt64 : 0
            let diff = Int64(aVal) - Int64(bVal) - Int64(borrow)
            
            if diff < 0 {
                let newVal = UInt64(diff + Int64(mask) + 1)
                result.append(AnyChunk(newVal))
                borrow = 1
            } else {
                result.append(AnyChunk(UInt64(diff)))
                borrow = 0
            }
        }
        
        while result.count > 1 && result.last!.asUInt64 == 0 {
            result.removeLast()
        }
        
        return result
    }
    
    /// Compare two chunk lists
    /// - Parameters:
    ///   - a: First chunk list
    ///   - b: Second chunk list
    /// - Returns: ComparisonResult indicating the ordering
    public static func compareChunkLists(_ a: [AnyChunk], _ b: [AnyChunk]) -> ComparisonResult {
        if a.count > b.count { return .orderedDescending }
        if a.count < b.count { return .orderedAscending }
        
        for i in (0..<a.count).reversed() {
            let aVal = a[i].asUInt64
            let bVal = b[i].asUInt64
            if aVal > bVal { return .orderedDescending }
            if aVal < bVal { return .orderedAscending }
        }
        
        return .orderedSame
    }
    
    /// Multiply two chunk lists
    /// - Parameters:
    ///   - a: First chunk list
    ///   - b: Second chunk list
    /// - Throws: An error if multiplication fails
    /// - Returns: A new chunk list representing the product
    public static func multiplyChunkLists(_ a: [AnyChunk], _ b: [AnyChunk]) throws -> [AnyChunk] {
        var result: [AnyChunk] = [AnyChunk(UInt64(0))]
        
        for (i, aChunk) in a.enumerated() {
            var carry: UInt64 = 0
            for (j, bChunk) in b.enumerated() {
                if i + j >= result.count {
                    result.append(AnyChunk(UInt64(0)))
                }
                
                let aVal = aChunk.asUInt64
                let bVal = bChunk.asUInt64
                let existing = result[i + j].asUInt64
                let product = aVal &* bVal &+ existing &+ carry
                let maskedProduct = product & mask
                carry = product >> currentChunkSize
                result[i + j] = AnyChunk(maskedProduct)
            }
            
            if carry > 0 {
                if i + b.count >= result.count {
                    result.append(AnyChunk(UInt64(0)))
                }
                let existing = result[i + b.count].asUInt64
                let sum = existing &+ carry
                let maskedSum = sum & mask
                carry = sum >> currentChunkSize
                result[i + b.count] = AnyChunk(maskedSum)
                
                if carry > 0 {
                    result.append(AnyChunk(carry))
                }
            }
        }
        
        // Remove trailing zeros
        while result.count > 1 && result.last!.asUInt64 == 0 {
            result.removeLast()
        }
        
        return result
    }
    
    /// Divide two chunk lists, returning (quotient, remainder)
    /// - Parameters:
    ///   - dividend: Dividend chunk list
    ///   - divisor: Divisor chunk list
    /// - Throws: An error if division by zero occurs
    /// - Returns: A tuple containing quotient and remainder chunk lists
    public static func divideChunkLists(_ dividend: [AnyChunk], _ divisor: [AnyChunk]) throws -> (quotient: [AnyChunk], remainder: [AnyChunk]) {
        precondition(!divisor.isEmpty && !(divisor.count == 1 && divisor[0].asUInt64 == 0), "Division by zero")
        
        var quotient: [AnyChunk] = []
        var remainder: [AnyChunk] = []
        
        for chunk in dividend.reversed() {
            // Shift remainder left by one chunk and add the current chunk
            remainder.insert(chunk, at: 0)
            remainder = normalizeChunkList(remainder)
            
            // Initialize quotient chunk
            var q: UInt64 = 0
            
            // Binary search for the maximum q where (divisor * q) <= remainder
            var low: UInt64 = 0
            var high: UInt64 = UInt64.max
            var mid: UInt64 = 0
            var product: [AnyChunk] = []
            var comparison: ComparisonResult = .orderedSame
            
            while low <= high {
                mid = (low + high) / 2
                product = try multiplyChunkLists(divisor, [AnyChunk(mid)])
                comparison = compareChunkLists(product, remainder)
                
                if comparison == .orderedDescending {
                    high = mid - 1
                } else {
                    q = mid
                    low = mid + 1
                }
                
                if q == mid {
                    break
                }
            }
            
            quotient.insert(AnyChunk(q), at: 0)
            let productFinal = try multiplyChunkLists(divisor, [AnyChunk(q)])
            remainder = try subtractChunkLists(remainder, productFinal)
        }
        
        // Normalize quotient and remainder
        quotient = normalizeChunkList(quotient)
        remainder = normalizeChunkList(remainder)
        
        return (quotient, remainder)
    }
    
    /// Normalize a chunk list (remove trailing zeros)
    /// - Parameter chunks: The chunk list to normalize
    /// - Returns: A normalized chunk list
    public static func normalizeChunkList(_ chunks: [AnyChunk]) -> [AnyChunk] {
        var normalized = chunks
        while normalized.count > 1 && normalized.last!.asUInt64 == 0 {
            normalized.removeLast()
        }
        return normalized
    }
}