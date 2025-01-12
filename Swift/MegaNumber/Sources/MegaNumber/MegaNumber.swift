//
//  MegaNumber.swift
//  MegaNumber
//
//  Created by Sydney Renee
//

import Foundation



// MARK: - MegaNumber Base Class

open class MegaNumber: CustomStringConvertible {
    /// The mantissa in chunk-limbs form (low-order chunk is index 0).
    open var mantissa: [Int]
    /// The exponent in chunk-limbs form (only relevant if `isFloat == true`).
    open var exponent: [Int]
    open var negative: Bool
    open var isFloat: Bool
    open var exponentNegative: Bool
    
    public init(
        mantissa: [Int] = [0],
        exponent: [Int] = [0],
        negative: Bool = false,
        isFloat: Bool = false,
        exponentNegative: Bool = false
    ) {
        self.mantissa = mantissa
        self.exponent = exponent
        self.negative = negative
        self.isFloat = isFloat
        self.exponentNegative = exponentNegative
        normalize()
    }
    
    // MARK: - Normalization
    /// Remove trailing zeros, handle zero sign, etc.
    open func normalize() {
        while mantissa.count > 1 && mantissa.last == 0 {
            mantissa.removeLast()
        }
        if isFloat {
            while exponent.count > 1 && exponent.last == 0 {
                exponent.removeLast()
            }
        }
        // if zero => unify sign
        if mantissa.count == 1 && mantissa[0] == 0 {
            negative = false
            exponent = [0]
            exponentNegative = false
        }
    }
    
    // MARK: - Chunk Functions



    /// Add two chunk-limb arrays => sum-limb array
    internal class func addChunks(_ A: [Int], _ B: [Int]) -> [Int] {
        let maxLen = max(A.count, B.count)
        var out: [Int] = []
        out.reserveCapacity(maxLen + 1)
        var carry = 0
        
        for i in 0..<maxLen {
            let av = i < A.count ? A[i] : 0
            let bv = i < B.count ? B[i] : 0
            let s = av &+ bv &+ carry
            let lo = s & MegaNumberConstants.mask
            carry = s >> MegaNumberConstants.globalChunkSize
            out.append(lo)
        }
        if carry != 0 { out.append(carry) }
        
        // Trim trailing zeros
        while out.count > 1 && out.last == 0 {
            out.removeLast()
        }
        return out
    }

    /// Subtract B from A (assuming A >= B), returning chunk-limb array
    internal class func subChunks(_ A: [Int], _ B: [Int]) -> [Int] {
        // A>=B must hold externally; we do a standard chunk-based subtraction with borrow
        var out: [Int] = []
        out.reserveCapacity(A.count)
        var carry = 0
        
        let maxLen = max(A.count, B.count)
        for i in 0..<maxLen {
            let av = i < A.count ? A[i] : 0
            let bv = i < B.count ? B[i] : 0
            var diff = av &- bv &- carry
            if diff < 0 {
                diff = diff &+ MegaNumberConstants.base
                carry = 1
            } else {
                carry = 0
            }
            out.append(diff & MegaNumberConstants.mask)
        }
        // trim
        while out.count > 1 && out.last == 0 {
            out.removeLast()
        }
        return out
    }
    /// Compute sqrt of mantissa assuming it's an integer
    internal func sqrtChunks(_ limbs: [Int]) throws -> [Int] {
        // Implement binary search for sqrt
        var low = [0]
        var high = limbs
        while true {
            let sum_lh = MegaNumber.addChunks(low, high)
            let (mid, _) = try divChunks(sum_lh, [2])  // divide by 2
            let cLo = MegaNumber.compareAbs(mid, low)
            let cHi = MegaNumber.compareAbs(mid, high)
            if cLo == 0 || cHi == 0 {
                return mid
            }
            let midSq = MegaNumber.mulChunks(mid, mid)
            let cCmp = MegaNumber.compareAbs(midSq, limbs)
            if cCmp == 0 {
                return mid
            } else if cCmp < 0 {
                low = mid
            } else {
                high = mid
            }
        }
    }
    /// Compare absolute magnitude of A vs. B => -1 if A<B, 0 if ==, 1 if A>B
    internal class func compareAbs(_ A: [Int], _ B: [Int]) -> Int {
        if A.count > B.count { return 1 }
        if A.count < B.count { return -1 }
        
        for i in (0..<A.count).reversed() {
            if A[i] > B[i] { return 1 }
            if A[i] < B[i] { return -1 }
        }
        return 0
    }
    
    /// Multiply two chunk-limb arrays => product-limb array using Karatsuba algorithm for large numbers
    fileprivate class func mulChunks(_ A: [Int], _ B: [Int]) -> [Int] {
        return karatsubaMulChunks(A, B)
    }
    /// Multiply two chunk-limb arrays => product-limb array
    internal class func mulChunksStandard(_ A: [Int], _ B: [Int]) -> [Int] {
        if A.count == 1 && A[0] == 0 { return [0] }
        if B.count == 1 && B[0] == 0 { return [0] }
        
        let la = A.count
        let lb = B.count
        var out: [Int] = Array(repeating: 0, count: la + lb)
        
        for i in 0..<la {
            var carry = 0
            let av = A[i]
            for j in 0..<lb {
                let prod = av &* B[j] &+ out[i + j] &+ carry
                let lo = prod & MegaNumberConstants.mask
                carry = prod >> MegaNumberConstants.globalChunkSize
                out[i + j] = lo
            }
            if carry != 0 {
                out[i + lb] = out[i + lb] &+ carry
            }
        }
        // trim
        while out.count > 1 && out.last == 0 {
            out.removeLast()
        }
        return out
    }
    /// Implement chunk-based right shift
    internal func shiftRight(_ limbs: [Int], _ shiftBits: Int) -> [Int] {
        // If shift <= 0, do nothing.
        guard shiftBits > 0 else { return limbs }
        
        // Number of whole chunks to drop.
        let chunkShift = shiftBits / MegaNumberConstants.globalChunkSize
        // Bits within one chunk to shift.
        let bitShift = shiftBits % MegaNumberConstants.globalChunkSize
    
        // If chunkShift >= limbs.count => result is 0.
        if chunkShift >= limbs.count {
            return [0]
        }
        
        // Remove the lowest 'chunkShift' limbs (since each is 2^GLOBAL_CHUNK_SIZE).
        var shifted = Array(limbs.dropFirst(chunkShift))
        
        // If there's no partial bit shift, we're done.
        if bitShift == 0 {
            // Possibly trim trailing zeroes
            while shifted.count > 1 && shifted.last == 0 {
                shifted.removeLast()
            }
            return shifted
        }
        
        // Otherwise, shift each limb to the right by bitShift bits,
        // carrying bits from the next limb.
        var carry = 0
        for i in (0..<shifted.count).reversed() {
            let val = shifted[i]
            // Right-shift this limb
            let newVal = (val >> bitShift) | (carry << (MegaNumberConstants.globalChunkSize - bitShift))
            // The "carry" (i.e. bits that fall off) comes from the lower part of val
            carry = val & ((1 << bitShift) - 1)
            
            shifted[i] = newVal & MegaNumberConstants.mask  // ensure we stay within chunk size
        }
        // Trim trailing zeroes
        while shifted.count > 1 && shifted.last == 0 {
            shifted.removeLast()
        }
        
        return shifted
    }
    /// Shifts the limbs left by `shift` chunks (equivalent to multiplying by BASE^shift).
    internal class func shiftLeft(_ limbs: [Int], _ shift: Int) -> [Int] {
        var shifted = limbs
        for _ in 0..<shift {
            shifted.insert(0, at: 0)
        }
        return shifted
    }
    /// Implements Karatsuba multiplication for large numbers.
    internal class func karatsubaMulChunks(_ A: [Int], _ B: [Int]) -> [Int] {
        let n = max(A.count, B.count)
        if n <= 32 {
            return mulChunksStandard(A, B) // Use standard multiplication for small sizes
        }
        
        let m = n / 2
        
        let A_low = Array(A.prefix(m))
        let A_high = Array(A.dropFirst(m))
        let B_low = Array(B.prefix(m))
        let B_high = Array(B.dropFirst(m))
        
        let z0 = karatsubaMulChunks(A_low, B_low)
        let z2 = karatsubaMulChunks(A_high, B_high)
        
        // Perform (A_low + A_high) * (B_low + B_high)
        let A_sum = self.addChunks(A_low, A_high)
        let B_sum = self.addChunks(B_low, B_high)
        let z1_full = karatsubaMulChunks(A_sum, B_sum)
        
        // Compute z1 = z1_full - z0 - z2
        let z1_intermediate = self.subChunks(z1_full, z0)
        let z1 = self.subChunks(z1_intermediate, z2)

        let intermediate = self.addChunks(self.shiftLeft(z2, 2 * m), self.shiftLeft(z1, m))
        let result = self.addChunks(intermediate, z0)
        
        return result
    }
    /// Divide chunk-limb arrays => (quotient, remainder), integer division
    internal func divChunks(_ A: [Int], _ B: [Int]) throws -> ([Int], [Int]) {
        // B must not be zero
        if B.count == 1 && B[0] == 0 {
            throw NSError(domain: "DivideByZero", code: 1, userInfo: nil)
        }
        let c = MegaNumber.compareAbs(A, B)
        if c < 0 { return ([0], A) } // A<B => Q=0, R=A
        if c == 0 { return ([1], [0]) } // A=B => Q=1, R=0
        
        var Q: [Int] = Array(repeating: 0, count: A.count)
        var R: [Int] = [0]
        
        // We do a standard chunk-based long division
        for i in (0..<A.count).reversed() {
            // shift R left by one chunk
            R.insert(0, at: 0)
            R[0] = A[i]
            
            // binary search in [0..BASE-1] for the best q
            var low = 0
            var high = MegaNumberConstants.base - 1
            var guess = 0
            
            while low <= high {
                let mid = (low &+ high) >> 1
                let mm = MegaNumber.mulChunks(B, [mid])
                let cmpv = MegaNumber.compareAbs(mm, R)
                if cmpv <= 0 {
                    guess = mid
                    low = mid &+ 1
                } else {
                    high = mid &- 1
                }
            }
            if guess != 0 {
                let mm = MegaNumber.mulChunks(B, [guess])
                R = MegaNumber.subChunks(R, mm)
            }
            Q[i] = guess
        }
        
        // trim Q, R
        while Q.count > 1 && Q.last == 0 {
            Q.removeLast()
        }
        while R.count > 1 && R.last == 0 {
            R.removeLast()
        }
        return (Q, R)
    }

    /// Divmod by small_val <= BASE
    internal func divmodSmall(_ A: [Int], _ smallVal: Int) -> ([Int], Int) {
        var remainder = 0
        var out: [Int] = Array(repeating: 0, count: A.count)
        
        for i in (0..<A.count).reversed() {
            // Shift the remainder left by GLOBAL_CHUNK_SIZE bits and add the current limb
            let cur = (remainder << MegaNumberConstants.globalChunkSize) &+ A[i]
            
            // Compute the quotient digit and the new remainder
            let qd = cur / smallVal
            remainder = cur % smallVal
            
            // Assign the quotient digit to the output array, ensuring it fits within the chunk mask
            out[i] = qd & MegaNumberConstants.mask
        }
        
        // Trim any unnecessary trailing zeros from the output array
        while out.count > 1 && out.last == 0 {
            out.removeLast()
        }
        
        return (out, remainder)
    }
    /// Convert chunk-limbs to decimal string
    internal func chunkToDecimal(_ limbs: [Int]) -> String {
        // quick check for zero
        if limbs.count == 1 && limbs[0] == 0 {
            return "0"
        }
        var temp = limbs
        var digits: [Character] = []
        while !(temp.count == 1 && temp[0] == 0) {
            let (q, r) = divmodSmall(temp, 10)
            temp = q
            digits.append(Character("\(r)"))
        }
        return String(digits.reversed())
    }

    /// Compute exponent value as signed Int
    internal func exponentValue(_ exponent: [Int], _ exponentNegative: Bool) -> Int {
        let raw = MegaNumber.chunksToInt(exponent)
        return exponentNegative ? -raw : raw
    }
    // MARK: - Integer I/O
    /// Convert an Int into chunk-limbs. A zero value => [0].
    internal class func intToChunks(_ val: Int) -> [Int] {
        if val == 0 { return [0] }
        var x = val
        var out: [Int] = []
        while x != 0 {
            out.append(x & MegaNumberConstants.mask)
            // shift right by GLOBAL_CHUNK_SIZE bits
            x = x >> MegaNumberConstants.globalChunkSize
        }
        return out
    }

    /// Combine chunk-limbs => a single Swift Int. (May overflow if large.)
    internal class func chunksToInt(_ limbs: [Int]) -> Int {
        var val = 0
        var shift = 0
        for limb in limbs {
            let part = limb << shift
            val = val &+ part  // &+ for potential overflow
            shift += MegaNumberConstants.globalChunkSize
        }
        return val
    }
    // MARK: - Decimal I/O
    
    /// Return a decimal-string representation. (Integer-only if exponent=0.)
    open func to_decimal_string() -> String {
        // If zero
        if mantissa.count == 1 && mantissa[0] == 0 {
            return "0"
        }
        
        // If exponent is zero or we are integer => treat as integer
        let expNonZero = (exponent.count > 1 || exponent[0] != 0)
        if !expNonZero {
            // purely integer
            let s = chunkToDecimal(mantissa)
            return (negative ? "-" : "") + s
        } else {
            // float => represent as "mantissa * 2^(exponent * chunkBits)" for simplicity
            var eVal = MegaNumber.chunksToInt(exponent)
            if exponentNegative { eVal = -eVal }
            let mantString = chunkToDecimal(mantissa)
            let signStr = negative ? "-" : ""
            // This is a simplistic representation.
            return "\(signStr)\(mantString) * 2^\(eVal * MegaNumberConstants.globalChunkSize)"
        }
    }
    

    /// Create from decimal string, e.g. "123.456"
    /// - Returns: a `MegaNumber` instance
    public class func from_decimal_string(_ s: String) -> MegaNumber {
        // Basic parse
        var negative = false
        var raw = s.trimmingCharacters(in: .whitespacesAndNewlines)
        if raw.hasPrefix("-") {
            negative = true
            raw.removeFirst()
        }
        if raw.isEmpty { return MegaNumber() }
        
        // Check float or int
        let parts = raw.split(separator: ".", omittingEmptySubsequences: false)
        if parts.count == 1 {
            // Integer
            let mant = decimalStringToChunks(String(parts[0]))
            return MegaNumber(
                mantissa: mant,
                exponent: [0],
                negative: negative,
                isFloat: false,
                exponentNegative: false
            )
        } else {
            // Float
            let intPart = String(parts[0])
            let fracPart = String(parts[1])
            
            // Combine them as integer => do repeated multiply/add
            let fullNumStr = intPart + fracPart
            let mant = decimalStringToChunks(fullNumStr)
            // Approximate exponent using length of fraction => treat fraction as 2^some shift
            // E.g., log2(10) * fracLen
            let fracLen = fracPart.count
            let shiftBits = Int(ceil(Double(fracLen) * log2(10.0)))
            let expChunks = self.intToChunks(shiftBits)
            
            return MegaNumber(
                mantissa: mant,
                exponent: expChunks,
                negative: negative,
                isFloat: true,
                exponentNegative: true
            )
        }
    }
    
    /// Convert decimal string => chunk-limb array
    internal class func decimalStringToChunks(_ dec: String) -> [Int] {
        if dec.isEmpty { return [0] }
        if dec == "0" { return [0] }
        
        var limbs = [0]
        for ch in dec {
            guard let digit = ch.wholeNumberValue else {
                fatalError("Invalid decimal digit in \(dec)")
            }
            // Multiply limbs by 10, then add digit
            limbs = addChunks(mulChunks(limbs, [10]), [digit])
        }
        // Trim trailing zeros
        while limbs.count > 1 && limbs.last == 0 {
            limbs.removeLast()
        }
        return limbs
    }
    
    // MARK: - Arithmetic
    static func +(lhs: MegaNumber, rhs: MegaNumber) -> MegaNumber {
        return lhs.add(rhs)
    }

    static func -(lhs: MegaNumber, rhs: MegaNumber) -> MegaNumber {
        return lhs.sub(rhs)
    }

    static func *(lhs: MegaNumber, rhs: MegaNumber) -> MegaNumber {
        return lhs.mul(rhs)
    }

    static func /(lhs: MegaNumber, rhs: MegaNumber) -> MegaNumber {
        return lhs.div(rhs)
    }

    /// Add two MegaNumbers. If either is float, handle float addition
    open func add(_ other: MegaNumber) -> MegaNumber {
        // If either is float, handle float addition
        if self.isFloat || other.isFloat {
            return addFloat(other)
        }
        
        // Integer addition
        if self.negative == other.negative {
            // Same sign => add magnitudes
            let sumMant = MegaNumber.addChunks(self.mantissa, other.mantissa)
            let sign = self.negative
            return MegaNumber(
                mantissa: sumMant,
                exponent: [0],
                negative: sign,
                isFloat: false,
                exponentNegative: false
            )
        } else {
            // Different signs => subtract magnitudes
            let cmp = MegaNumber.compareAbs(self.mantissa, other.mantissa)
            if cmp == 0 {
                // Result is zero
                return MegaNumber(
                    mantissa: [0],
                    exponent: [0],
                    negative: false,
                    isFloat: false,
                    exponentNegative: false
                )
            } else if cmp > 0 {
                // self > other in magnitude
                let diff = MegaNumber.subChunks(self.mantissa, other.mantissa)
                let sign = self.negative
                return MegaNumber(
                    mantissa: diff,
                    exponent: [0],
                    negative: sign,
                    isFloat: false,
                    exponentNegative: false
                )
            } else {
                // other > self in magnitude
                let diff = MegaNumber.subChunks(other.mantissa, self.mantissa)
                let sign = other.negative
                return MegaNumber(
                    mantissa: diff,
                    exponent: [0],
                    negative: sign,
                    isFloat: false,
                    exponentNegative: false
                )
            }
        }
    }
    
    /// Float addition using chunk-based arithmetic
    open func addFloat(_ other: MegaNumber) -> MegaNumber {
        let expA = exponentValue()
        let expB = other.exponentValue()
        
        let diff = expA - expB
        var adjustedMantA = self.mantissa
        var adjustedMantB = other.mantissa
        var finalExp = expA
        
        // Align exponents by shifting mantissas
        if diff > 0 {
            adjustedMantB = shiftRight(adjustedMantB, diff)
            finalExp = expA
        } else if diff < 0 {
            adjustedMantA = shiftRight(adjustedMantA, -diff)
            finalExp = expB
        }
        
        // Add or subtract mantissas
        let sameSign = (self.negative == other.negative)
        let resultMant: [Int]
        let resultSign: Bool
        
        if sameSign {
            // Same sign => add
            resultMant = MegaNumber.addChunks(adjustedMantA, adjustedMantB)
            resultSign = self.negative
        } else {
            // Different sign => subtract
            let cmp = MegaNumber.compareAbs(adjustedMantA, adjustedMantB)
            if cmp == 0 {
                // Zero
                return MegaNumber(
                    mantissa: [0],
                    exponent: [0],
                    negative: false,
                    isFloat: false,
                    exponentNegative: false
                )
            } else if cmp > 0 {
                resultMant = MegaNumber.subChunks(adjustedMantA, adjustedMantB)
                resultSign = self.negative
            } else {
                resultMant = MegaNumber.subChunks(adjustedMantB, adjustedMantA)
                resultSign = other.negative
            }
        }
        
        // Build a new MegaNumber (float) with that mantissa and `finalExp`.
        let newExponent = MegaNumber.intToChunks(finalExp)
        let out = MegaNumber(
            mantissa: resultMant,
            exponent: newExponent,
            negative: resultSign,
            isFloat: true,
            exponentNegative: (finalExp < 0)
        )
        out.normalize()
        return out
    }

    
    /// Subtract two MegaNumbers. a - b = a + (-b)
    open func sub(_ other: MegaNumber) -> MegaNumber {
        let negOther = MegaNumber(
            mantissa: other.mantissa,
            exponent: other.exponent,
            negative: !other.negative,
            isFloat: other.isFloat,
            exponentNegative: other.exponentNegative
        )
        return self.add(negOther)
    }
    
    /// Multiply two MegaNumbers. If either is float, delegate to float multiply
    open func mul(_ other: MegaNumber) -> MegaNumber {
        if self.isFloat || other.isFloat {
            return mulFloat(other)
        }
        
        // Integer multiply
        let sign = (self.negative != other.negative)
        let product = MegaNumber.mulChunks(self.mantissa, other.mantissa)
        return MegaNumber(
            mantissa: product,
            exponent: [0],
            negative: sign,
            isFloat: false,
            exponentNegative: false
        )
    }
    
    /// Float multiplication using chunk-based arithmetic
    open func mulFloat(_ other: MegaNumber) -> MegaNumber {
        // Multiply mantissas
        let productMant = MegaNumber.mulChunks(self.mantissa, other.mantissa)
        // Add exponents
        let expA = exponentValue()
        let expB = other.exponentValue()
        let sumExp = expA + expB
        let newExponent = MegaNumber.intToChunks(sumExp)
        // Determine sign
        let newNegative = (self.negative != other.negative)
        // Create result
        let out = MegaNumber(
            mantissa: productMant,
            exponent: newExponent,
            negative: newNegative,
            isFloat: true,
            exponentNegative: (sumExp < 0)
        )
        out.normalize()
        return out
    }
    
    /// Divide two MegaNumbers. If either is float, delegate to float division
    open func div(_ other: MegaNumber) -> MegaNumber {
        // if other=0 => error
        if other.mantissa.count == 1 && other.mantissa[0] == 0 {
            fatalError("Division by zero")
        }
        // If float => delegate
        if self.isFloat || other.isFloat {
            return divFloat(other)
        }
        // integer division
        let sign = (self.negative != other.negative)
        let c = MegaNumber.compareAbs(self.mantissa, other.mantissa)
        if c < 0 {
            return MegaNumber(
                mantissa: [0],
                exponent: [0],
                negative: false,
                isFloat: false,
                exponentNegative: false
            )
        } else if c == 0 {
            return MegaNumber(
                mantissa: [1],
                exponent: [0],
                negative: sign,
                isFloat: false,
                exponentNegative: false
            )
        } else {
            let (q, _) = try! divChunks(self.mantissa, other.mantissa)
            return MegaNumber(
                mantissa: q,
                exponent: [0],
                negative: sign,
                isFloat: false,
                exponentNegative: false
            )
        }
    }
    
    /// Float division using chunk-based arithmetic
    open func divFloat(_ other: MegaNumber) -> MegaNumber {
        // Divide mantissas
        let quotientMant = try! divChunks(self.mantissa, other.mantissa).0
        // Subtract exponents
        let expA = exponentValue()
        let expB = other.exponentValue()
        let diffExp = expA - expB
        let newExponent = MegaNumber.intToChunks(diffExp)
        // Determine sign
        let newNegative = (self.negative != other.negative)
        // Create result
        let out = MegaNumber(
            mantissa: quotientMant,
            exponent: newExponent,
            negative: newNegative,
            isFloat: true,
            exponentNegative: (diffExp < 0)
        )
        out.normalize()
        return out
    }

    
    /// sqrt => integer or float
    open func sqrt() -> MegaNumber {
        // If negative => error
        if self.negative {
            fatalError("sqrt of negative not supported")
        }
        // if zero => zero
        if mantissa.count == 1 && mantissa[0] == 0 {
            return MegaNumber(
                mantissa: [0],
                exponent: [0],
                negative: false,
                isFloat: false,
                exponentNegative: false
            )
        }
        // if float => implement float sqrt manually
        if isFloat {
            // Manual chunk-based float sqrt
            return sqrtFloat()
        } else {
            // Integer sqrt
            return sqrtBigInt()
        }
    }
    
    /// Implement manual chunk-based float sqrt
    open func sqrtFloat() -> MegaNumber {
        // Factor out exponent's parity, do integer sqrt on mantissa, reapply half exponent
        var totalExp = exponentValue()
        var workMantissa = mantissa
        
        if totalExp % 2 != 0 {
            if totalExp > 0 {
                // Multiply mantissa by BASE to make exponent even
                workMantissa = MegaNumber.mulChunks(workMantissa, [MegaNumberConstants.base])
                totalExp -= 1
            } else {
                // Divide mantissa by BASE (right shift)
                workMantissa = shiftRight(workMantissa, 1)  // Simplistic
                totalExp += 1
            }
        }
        
        // Perform integer sqrt on adjustedMantissa
        let sqrtMantissa = try! sqrtChunks(workMantissa)
        let sqrtExp = totalExp / 2
        let newExponent = MegaNumber.intToChunks(sqrtExp)
        let newNegative = false  // sqrt is non-negative
        
        return MegaNumber(
            mantissa: sqrtMantissa,
            exponent: newExponent,
            negative: newNegative,
            isFloat: true,
            exponentNegative: (sqrtExp < 0)
        )
    }
    
    /// Compute exponent value as signed Int
    internal func exponentValue() -> Int {
        let raw = MegaNumber.chunksToInt(self.exponent)
        return self.exponentNegative ? -raw : raw
    }
    

    
    /// Compute integer sqrt of mantissa
    internal func sqrtBigInt(_ limbs: [Int]) -> [Int] {
        // Implement binary search for sqrt
        var low = [0]
        var high = limbs
        while true {
            let sum_lh = MegaNumber.addChunks(low, high)
            let (mid, _) = try! divChunks(sum_lh, [2])  // divide by 2
            let cLo = MegaNumber.compareAbs(mid, low)
            let cHi = MegaNumber.compareAbs(mid, high)
            if cLo == 0 || cHi == 0 {
                return mid
            }
            let midSq = MegaNumber.mulChunks(mid, mid)
            let cCmp = MegaNumber.compareAbs(midSq, limbs)
            if cCmp == 0 {
                return mid
            } else if cCmp < 0 {
                low = mid
            } else {
                high = mid
            }
        }
    }
    /// Compute integer sqrt of mantissa
    internal func sqrtBigInt() -> MegaNumber {
        // Implement binary search for sqrt
        var low = [0]
        var high = mantissa
        while true {
            let sum_lh = MegaNumber.addChunks(low, high)
            let (mid, _) = try! divChunks(sum_lh, [2])  // divide by 2
            let cLo = MegaNumber.compareAbs(mid, low)
            let cHi = MegaNumber.compareAbs(mid, high)
            if cLo == 0 || cHi == 0 {
                return MegaNumber(
                    mantissa: mid,
                    exponent: [0],
                    negative: false,
                    isFloat: false,
                    exponentNegative: false
                )
            }
            let midSq = MegaNumber.mulChunks(mid, mid)
            let cCmp = MegaNumber.compareAbs(midSq, mantissa)
            if cCmp == 0 {
                return MegaNumber(
                    mantissa: mid,
                    exponent: [0],
                    negative: false,
                    isFloat: false,
                    exponentNegative: false
                )
            } else if cCmp < 0 {
                low = mid
            } else {
                high = mid
            }
        }
    }
    
    // MARK: - Description
    public var description: String {
        return "<MegaNumber \(to_decimal_string())>"
    }
    
    /// Negate the MegaNumber (for subtraction)
    public func negate() -> MegaNumber {
        return MegaNumber(
            mantissa: mantissa,
            exponent: exponent,
            negative: !self.negative,
            isFloat: self.isFloat,
            exponentNegative: self.exponentNegative
        )
    }
}
