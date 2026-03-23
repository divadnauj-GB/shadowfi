#pragma once

#include "tcu_matrix.hpp"
#include "tcu_types.hpp"

mat4f matmul_add_ref(const mat4f& A, const mat4f& B, const mat4f& C);
Matrixf matmul_add_ref_big(const Matrixf& A, const Matrixf& B, const Matrixf& C);
