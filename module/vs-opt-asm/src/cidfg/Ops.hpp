//===- StandaloneOps.h - Standalone dialect ops -----------------*- C++ -*-===//
//
// This file is licensed under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#ifndef __VESYLA_IROPT_CIDFG_OPS_HPP__
#define __VESYLA_IROPT_CIDFG_OPS_HPP__

#include "mlir/Bytecode/BytecodeOpInterface.h"
#include "mlir/IR/Attributes.h"
#include "mlir/IR/BuiltinAttributes.h"
#include "mlir/IR/BuiltinTypes.h"
#include "mlir/IR/Dialect.h"
#include "mlir/IR/OpDefinition.h"
#include "mlir/Interfaces/InferTypeOpInterface.h"
#include "mlir/Interfaces/SideEffectInterfaces.h"

namespace vesyla {
namespace cidfg {
class IntegerType;
}
} // namespace vesyla

#include "cidfg/Types.hpp"

#define GET_OP_CLASSES
#include "cidfg/Ops.hpp.inc"

#endif // __VESYLA_IROPT_CIDFG_OPS_HPP__
