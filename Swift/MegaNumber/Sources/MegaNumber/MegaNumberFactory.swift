//
//  MegaNumberFactory.swift
//  MegaNumber
//
//  Created by Sydney Bach on 1/9/25.
//

import Foundation

/// Factory class to create MegaNumberClass instances with optimal chunk sizes based on hardware
public class MegaNumberFactory {
    /// Create a MegaNumberClass instance
    /// - Parameters:
    ///   - mantissa: Mantissa values as UInt64
    ///   - exponent: Exponent values as UInt64
    ///   - isNegative: Sign flag
    ///   - isFloat: Float flag
    ///   - exponentNegative: Exponent negative flag
    /// - Returns: A configured MegaNumberClass instance
    public static func createMegaNumber(
        mantissa: [UInt64] = [0],
        exponent: [UInt64] = [0],
        isNegative: Bool = false,
        isFloat: Bool = false,
        exponentNegative: Bool = false
    ) -> MegaNumberClass {
        let architecture = HardwareArchitecture.detectArchitecture()
        var chunkSize: Int
        
        switch architecture {
        case .cpu(let bits), .gpu(let bits), .metal(let bits), .neural(let bits):
            chunkSize = bits
        }
        
        // Validate chunk size to be within acceptable range
        guard [8, 16, 32, 64].contains(chunkSize) else {
            fatalError("Unsupported chunk size: \(chunkSize) bits. Supported sizes are 8, 16, 32, 64.")
        }
        
        // Set the global chunk size
        MegaNumberClass.currentChunkSize = chunkSize
        
        // Instantiate with the desired chunk size
        let mantissaChunks = mantissa.map { AnyChunk(UInt64($0)) }
        let exponentChunks = exponent.map { AnyChunk(UInt64($0)) }
        
        return MegaNumberClass(
            mantissa: mantissaChunks,
            exponent: exponentChunks,
            isNegative: isNegative,
            isFloat: isFloat,
            exponentNegative: exponentNegative
        )
    }
}
