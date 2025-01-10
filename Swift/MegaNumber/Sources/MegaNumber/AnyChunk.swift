import Foundation

/// Type-erased Chunk to handle different chunk sizes uniformly
public struct AnyChunk: Comparable, CustomStringConvertible {
    private let _asUInt64: () -> UInt64
    private let _description: () -> String
    
    public var asUInt64: UInt64 { return _asUInt64() }
    public var description: String { return _description() }
    
    public static func == (lhs: AnyChunk, rhs: AnyChunk) -> Bool {
        return lhs.asUInt64 == rhs.asUInt64
    }
    
    public static func < (lhs: AnyChunk, rhs: AnyChunk) -> Bool {
        return lhs.asUInt64 < rhs.asUInt64
    }
    
    /// Initialize with any ChunkProtocol conforming type
    /// - Parameter chunk: A chunk conforming to ChunkProtocol
    public init<ChunkType: ChunkProtocol>(_ chunk: ChunkType) {
        _asUInt64 = { chunk.asUInt64 }
        _description = { "\(chunk)" }
    }
}