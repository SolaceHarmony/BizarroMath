//
//  MegaNumberTest.swift
//  MegaNumberTest
//
//  Created by Sydney Bach on 1/9/25.
//

import Testing
@testable import MegaNumber

@Suite

struct MegaNumberTests {
        
        // MARK: - Addition Tests
        
        @Test
    func testAddition_withPositiveNumbers() async throws {
            let num1 = await MegaNumberFactory.createMegaNumber(mantissa: [1, 2, 3],
                                                          isNegative: false,
                                                          isFloat: false)
        let num2 = await MegaNumberFactory.createMegaNumber(mantissa: [4, 5, 6],
                                                          isNegative: false,
                                                          isFloat: false)
            let expectedSum: [UInt64] = [5, 7, 9]

        let sum = try await num1.add(num2)

            #expect(sum.mantissa.map { $0.asUInt64 } == expectedSum)
        }

        @Test
    func testAddition_withZero() async throws {
        let num1 = await MegaNumberFactory.createMegaNumber(mantissa: [0],
                                                          isNegative: false,
                                                          isFloat: false)
        let num2 = await MegaNumberFactory.createMegaNumber(mantissa: [4, 5, 6],
                                                          isNegative: false,
                                                          isFloat: false)
            let expectedSum: [UInt64] = [4, 5, 6]

        let sum = try await num1.add(num2)

            #expect(sum.mantissa.map { $0.asUInt64 } == expectedSum)
        }

        @Test
    func testAddition_overflow() async throws {
            // 1. Setup
            let maxChunk = UInt64(UInt8.max) // 255
            // Configure both numbers for an 8-bit chunk size to induce overflow at 256.
        let num1 = await MegaNumberFactory.createMegaNumber(
                mantissa: [maxChunk],
                isNegative: false,
                isFloat: false,
                chunkSize: 8
            )
        let num2 = await MegaNumberFactory.createMegaNumber(
                mantissa: [1],
                isNegative: false,
                isFloat: false,
                chunkSize: 8
            )
            
            // 2. Define expected outcome (255 + 1 = 256 => [0, 1])
            let expectedSum: [UInt64] = [0, 1]
            
            // 3. Invoke
        let sum = try await num1.add(num2)
            
            // 4. Check
            #expect(sum.mantissa.map { $0.asUInt64 } == expectedSum)
        }

        // MARK: - Subtraction Tests

        @Test
    func testSubtraction_withPositiveNumbers() async throws {
        let num1 = await MegaNumberFactory.createMegaNumber(mantissa: [5, 7, 9],
                                                          isNegative: false,
                                                          isFloat: false)
        let num2 = await MegaNumberFactory.createMegaNumber(mantissa: [4, 5, 6],
                                                          isNegative: false,
                                                          isFloat: false)
            let expectedDifference: [UInt64] = [1, 2, 3]

        let difference = try await num1.subtract(num2)

            #expect(difference.mantissa.map { $0.asUInt64 } == expectedDifference)
        }

        @Test
    func testSubtraction_resultingInZero() async throws {
        let num1 = await MegaNumberFactory.createMegaNumber(mantissa: [4, 5, 6],
                                                          isNegative: false,
                                                          isFloat: false)
        let num2 = await MegaNumberFactory.createMegaNumber(mantissa: [4, 5, 6],
                                                          isNegative: false,
                                                          isFloat: false)
            let expectedDifference: [UInt64] = [0]

        let difference = try await num1.subtract(num2)

            #expect(difference.mantissa.map { $0.asUInt64 } == expectedDifference)
        }

        @Test
    func testSubtraction_negativeResult() async throws {
        let num1 = await MegaNumberFactory.createMegaNumber(mantissa: [3, 2, 1],
                                                          isNegative: false,
                                                          isFloat: false)
        let num2 = await MegaNumberFactory.createMegaNumber(mantissa: [4, 5, 6],
                                                          isNegative: false,
                                                          isFloat: false)
            // In your HPC logic, 123 < 654 => difference ~ (654 - 123) => 531
            // So HPC might produce some reversed-limb representation.
            // Let's assume you want [1, 3, 5] in decimal, sign is negative
            let expectedDifference: [UInt64] = [1, 3, 5]

        let difference = try await num1.subtract(num2)

            #expect(difference.mantissa.map { $0.asUInt64 } == expectedDifference)
            #expect(difference.isNegative == true)
        }

        // MARK: - Multiplication Tests

        @Test
    func testMultiplication_withPositiveNumbers() async throws {
        let num1 = await MegaNumberFactory.createMegaNumber(mantissa: [2],
                                                          isNegative: false,
                                                          isFloat: false)
        let num2 = await MegaNumberFactory.createMegaNumber(mantissa: [3],
                                                          isNegative: false,
                                                          isFloat: false)
            let expectedProduct: [UInt64] = [6]

        let product = try await num1.multiply(by: num2)

            #expect(product.mantissa.map { $0.asUInt64 } == expectedProduct)
        }

        @Test
    func testMultiplication_withZero() async throws {
        let num1 = await MegaNumberFactory.createMegaNumber(mantissa: [0],
                                                          isNegative: false,
                                                          isFloat: false)
        let num2 = await MegaNumberFactory.createMegaNumber(mantissa: [3, 4, 5],
                                                          isNegative: false,
                                                          isFloat: false)
            let expectedProduct: [UInt64] = [0]

        let product = try await num1.multiply(by: num2)

            #expect(product.mantissa.map { $0.asUInt64 } == expectedProduct)
        }

        @Test
    func testMultiplication_largeNumbers() async throws {
            // Force chunkSize=8 => base=256
        let num1 = await MegaNumberFactory.createMegaNumber(
                mantissa: [2, 3, 4],
                isNegative: false,
                isFloat: false,
                chunkSize: 8
            )
        let num2 = await MegaNumberFactory.createMegaNumber(
                mantissa: [5, 6, 7],
                isNegative: false,
                isFloat: false,
                chunkSize: 8
            )
            
            // HPC expansions in base=256 might match the "expected"
            let expectedProduct: [UInt64] = [10, 28, 46, 28, 19]

        let product = try await num1.multiply(by: num2)
            
            // Debugging log
            print("HPC final =>", product.mantissa.map { String($0.asUInt64, radix:16) })
            
            #expect(product.mantissa.map { $0.asUInt64 } == expectedProduct)
        }

        // MARK: - Division Tests

        @Test
    func testDivision_basic() async throws {
        let dividend = await MegaNumberFactory.createMegaNumber(mantissa: [10],
                                                              isNegative: false,
                                                              isFloat: false)
        let divisor = await MegaNumberFactory.createMegaNumber(mantissa: [2],
                                                             isNegative: false,
                                                             isFloat: false)
            
            let expectedQuotient: [UInt64] = [5]
            let expectedRemainder: [UInt64] = [0]
            
            // HPC-based chunk-limb division
            let (quotient, remainder) = try MegaNumberClass.divideChunkLists(
                dividend.mantissa,
                divisor.mantissa,
                chunkSize: dividend.chunkSize,
                mask: dividend.mask
            )
            
            #expect(quotient.map { $0.asUInt64 } == expectedQuotient)
            #expect(remainder.map { $0.asUInt64 } == expectedRemainder)
        }
    }
