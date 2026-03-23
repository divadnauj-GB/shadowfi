#include "tcu_reference.hpp"

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
