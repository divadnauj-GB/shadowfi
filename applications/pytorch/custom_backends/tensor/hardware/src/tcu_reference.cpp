#include "tcu_reference.hpp"

#include <stdexcept>

mat4f matmul_add_ref(const mat4f& A, const mat4f& B, const mat4f& C) {
    mat4f W{};
    for (int i = 0; i < 4; ++i) {
        for (int j = 0; j < 4; ++j) {
            float acc = 0.0f;
            for (int k = 0; k < 4; ++k) {
                acc += A[i][k] * B[k][j];
            }
            W[i][j] = acc + C[i][j];
        }
    }
    return W;
}

Matrixf matmul_add_ref_big(const Matrixf& A, const Matrixf& B, const Matrixf& C) {
    if (A.cols() != B.rows()) {
        throw std::invalid_argument("A.cols() must equal B.rows()");
    }
    if (A.rows() != C.rows() || B.cols() != C.cols()) {
        throw std::invalid_argument("C must have shape (A.rows(), B.cols())");
    }

    Matrixf W(A.rows(), B.cols(), 0.0f);

    for (std::size_t i = 0; i < A.rows(); ++i) {
        for (std::size_t j = 0; j < B.cols(); ++j) {
            float acc = C(i, j);
            for (std::size_t k = 0; k < A.cols(); ++k) {
                acc += A(i, k) * B(k, j);
            }
            W(i, j) = acc;
        }
    }
    return W;
}
