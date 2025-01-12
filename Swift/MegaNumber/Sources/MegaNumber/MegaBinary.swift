//
//  MegaBinary.swift
//  MegaNumber
//
//  Created by Sydney Renee on 1/9/25.
//

import Foundation

// MARK: - MegaBinary

public class MegaBinary: MegaNumber {
    /// Store the binary input as string for reference
    private var binaryString: String
    
    /// Construct from either a binary string (e.g. "1010") or from raw bytes.
    public init(_ value: Any) {
        // Force integer mode for MegaBinary
        self.binaryString = ""
        super.init(mantissa: [0], exponent: [0], negative: false, isFloat: false, exponentNegative: false)
        
        if let s = value as? String {
            // parse as binary string
            let stripped = s.hasPrefix("0b") ? String(s.dropFirst(2)) : s
            self.binaryString = stripped
            let chunked = parseBinaryString(stripped)
            self.mantissa = chunked
            normalize()
        } else if let bytesVal = value as? Data {
            // parse as bytes
            let binStr = bytesVal.map { String(format: "%08b", $0) }.joined()
            self.binaryString = binStr
            self.mantissa = parseBinaryString(binStr)
            normalize()
        } else if let byteArr = value as? [UInt8] {
            let binStr = byteArr.map { String(format: "%08b", $0) }.joined()
            self.binaryString = binStr
            self.mantissa = parseBinaryString(binStr)
            normalize()
        } else if let byteArr = value as? ArraySlice<UInt8> {
            let binStr = byteArr.map { String(format: "%08b", $0) }.joined()
            self.binaryString = binStr
            self.mantissa = parseBinaryString(binStr)
            normalize()
        } else {
            fatalError("Unsupported MegaBinary init type")
        }
    }
    
    /// Rebuild `binaryString` from current mantissa
    private func rebuildBinaryString() {
        if mantissa.count == 1 && mantissa[0] == 0 {
            self.binaryString = "0"
            return
        }
        // convert chunk-limbs => single large binary string
        // each chunk => 32 bits
        var bits = ""
        for i in (0..<mantissa.count).reversed() {
            let limb = mantissa[i]
            let chunkStr = String(limb, radix: 2)
            // pad up to GLOBAL_CHUNK_SIZE bits if not the highest chunk
            let padCount = (i == mantissa.count - 1) ? 0 : MegaNumberConstants.globalChunkSize - chunkStr.count
            if padCount > 0 {
                bits += String(repeating: "0", count: padCount) + chunkStr
            } else {
                bits += chunkStr
            }
        }
        // remove leading zeros
        bits = bits.drop { $0 == "0" }.isEmpty ? "0" : String(bits.drop { $0 == "0" })
        self.binaryString = bits
    }
    
    /// Parse a binary string => chunk-limb array
    fileprivate func parseBinaryString(_ s: String) -> [Int] {
            
    }
    
    /// Return current binary string representation
    public func to_string() -> String {
        rebuildBinaryString()
        return binaryString
    }
    
    /// Convert to raw bytes
    public func to_bytes() -> [UInt8] {
        rebuildBinaryString()
        let bitsCount = binaryString.count
        // pad up to multiple of 8
        let mod8 = bitsCount % 8
        let pad = mod8 == 0 ? 0 : 8 - mod8
        let padded = String(repeating: "0", count: pad) + binaryString
        var bytes: [UInt8] = []
        let chunkCount = padded.count / 8
        for i in 0..<chunkCount {
            let start = i*8
            let end = start + 8
            let slice = padded.padding(toLength: Int(end), withPad: <#T##StringProtocol#>, startingAt: Int(start))
            let val = UInt8(slice, radix: 2) ?? 0
            bytes.append(val)
        }
        return bytes
    }
    
    // MARK: - Arithmetic Overrides
    
    /// Add two MegaBinary. Returns MegaBinary
    public override func add(_ other: MegaNumber) -> MegaNumber {
        let sum = super.add(other)
        if other.isFloat {
            // If other is float, the result is float. Return MegaNumber
            return sum
        } else if let otherBinary = other as? MegaBinary {
            // Both are MegaBinary, return a new MegaBinary with sum's mantissa
            let sumBinaryStr = limbsToBinaryString(sum.mantissa)
            return MegaBinary(sumBinaryStr)
        } else {
            // Other is integer, but not MegaBinary. Convert sum's mantissa to binary string
            let sumBinaryStr = limbsToBinaryString(sum.mantissa)
            return MegaBinary(sumBinaryStr)
        }
    }
    
    /// Subtract two MegaBinary. Returns MegaBinary
    public override func sub(_ other: MegaNumber) -> MegaNumber {
        let dif = super.sub(other)
        if other.isFloat {
            // If other is float, the result is float. Return MegaNumber
            return dif
        } else if let otherBinary = other as? MegaBinary {
            // Both are MegaBinary, return a new MegaBinary with dif's mantissa
            let difBinaryStr = limbsToBinaryString(dif.mantissa)
            return MegaBinary(difBinaryStr)
        } else {
            // Other is integer, but not MegaBinary. Convert dif's mantissa to binary string
            let difBinaryStr = limbsToBinaryString(dif.mantissa)
            return MegaBinary(difBinaryStr)
        }
    }
    
    /// Multiply two MegaBinary. Returns MegaBinary
    public override func mul(_ other: MegaNumber) -> MegaNumber {
        let prod = super.mul(other)
        if other.isFloat {
            // If other is float, the result is float. Return MegaNumber
            return prod
        } else if let otherBinary = other as? MegaBinary {
            // Both are MegaBinary, return a new MegaBinary with prod's mantissa
            let prodBinaryStr = limbsToBinaryString(prod.mantissa)
            return MegaBinary(prodBinaryStr)
        } else {
            // Other is integer, but not MegaBinary. Convert prod's mantissa to binary string
            let prodBinaryStr = limbsToBinaryString(prod.mantissa)
            return MegaBinary(prodBinaryStr)
        }
    }
    
    /// Divide two MegaBinary. Returns MegaNumber or MegaFloat
    public override func div(_ other: MegaNumber) -> MegaNumber {
        let q = super.div(other)
        if other.isFloat {
            // If other is float, result is float
            return q
        } else if let otherBinary = other as? MegaBinary {
            // Both are MegaBinary, return a new MegaBinary with q's mantissa
            let qBinaryStr = limbsToBinaryString(q.mantissa)
            return MegaBinary(qBinaryStr)
        } else {
            // Other is integer, but not MegaBinary. Convert q's mantissa to binary string
            let qBinaryStr = limbsToBinaryString(q.mantissa)
            return MegaBinary(qBinaryStr)
        }
    }
    
    /// Convert chunk-limbs => binary string
    fileprivate func limbsToBinaryString(_ limbs: [Int]) -> String {
        if limbs.count == 1 && limbs[0] == 0 { return "0" }
        var bits = ""
        for i in (0..<limbs.count).reversed() {
            let limb = limbs[i]
            let chunkStr = String(limb, radix: 2)
            // pad up to GLOBAL_CHUNK_SIZE bits if not the highest chunk
            let padCount = (i == limbs.count - 1) ? 0 : MegaNumberConstants.globalChunkSize - chunkStr.count
            if padCount > 0 {
                bits += String(repeating: "0", count: padCount) + chunkStr
            } else {
                bits += chunkStr
            }
        }
        // remove leading zeros
        return bits.drop { $0 == "0" }.isEmpty ? "0" : String(bits.drop { $0 == "0" })
    }
    
    // MARK: - Description
    public override var description: String {
        return "<MegaBinary \(to_string())>"
    }
}
