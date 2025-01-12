//
//  MegaNumberConstants.swift
//  BizarroMath
//
//  Created by Sydney Bach on 1/9/25.
//


// MegaNumberConstants.swift
import Foundation

struct MegaNumberConstants {
    static let globalChunkSize: Int = 64
    static let base: Int = 1 << MegaNumberConstants.globalChunkSize
    static let mask: Int = MegaNumberConstants.base - 1
}
