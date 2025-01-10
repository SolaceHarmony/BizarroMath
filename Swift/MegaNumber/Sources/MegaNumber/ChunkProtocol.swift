import Foundation

/// Protocol defining the requirements for a chunk type
public protocol ChunkProtocol: BinaryInteger, Comparable, CustomStringConvertible {
    /// The size of the chunk in bits
    static var bitSize: Int { get }
    
    /// The maximum value of the chunk type
    static var maxValue: Self { get }
    
    /// Initialize from UInt64 for uniformity
    init(_ value: UInt64)
    
    /// Retrieve the value as UInt64 for operations
    var asUInt64: UInt64 { get }
}

// Extend unsigned integers to conform to ChunkProtocol
extension UInt8: ChunkProtocol {
    public static var bitSize: Int { return 8 }
    public static var maxValue: UInt8 { return UInt8.max }
    
    public init(_ value: UInt64) {
        self = UInt8(truncatingIfNeeded: value)
    }
    
    public var asUInt64: UInt64 { return UInt64(self) }
}

extension UInt16: ChunkProtocol {
    public static var bitSize: Int { return 16 }
    public static var maxValue: UInt16 { return UInt16.max }
    
    public init(_ value: UInt64) {
        self = UInt16(truncatingIfNeeded: value)
    }
    
    public var asUInt64: UInt64 { return UInt64(self) }
}

extension UInt32: ChunkProtocol {
    public static var bitSize: Int { return 32 }
    public static var maxValue: UInt32 { return UInt32.max }
    
    public init(_ value: UInt64) {
        self = UInt32(truncatingIfNeeded: value)
    }
    
    public var asUInt64: UInt64 { return UInt64(self) }
}

extension UInt64: ChunkProtocol {
    public static var bitSize: Int { return 64 }
    public static var maxValue: UInt64 { return UInt64.max }
    
    public init(_ value: UInt64) {
        self = value
    }
    
    public var asUInt64: UInt64 { return self }
}