#include <verilated.h>
#include "Vsub_tensor_core.h"

#include "tcu_driver.hpp"
#include "tcu_matrix.hpp"
#include "tcu_reference.hpp"
#include "tcu_tiled.hpp"

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>

static void print_matrix(const char* name, const Matrixf& M) {
    std::cout << name << "\n";
    for (std::size_t i = 0; i < M.rows(); ++i) {
        std::cout << "[ ";
        for (std::size_t j = 0; j < M.cols(); ++j) {
            std::cout << std::fixed << std::setprecision(8) << M(i, j) << " ";
        }
        std::cout << "]\n";
    }
    std::cout << "\n";
}

static float max_abs_error(const Matrixf& A, const Matrixf& B) {
    float err = 0.0f;
    for (std::size_t i = 0; i < A.rows(); ++i) {
        for (std::size_t j = 0; j < A.cols(); ++j) {
            err = std::max(err, std::fabs(A(i, j) - B(i, j)));
        }
    }
    return err;
}

static void print_diff_matrix(const Matrixf& hw, const Matrixf& sw) {
    std::cout << "ABS ERROR\n";
    for (std::size_t i = 0; i < hw.rows(); ++i) {
        std::cout << "[ ";
        for (std::size_t j = 0; j < hw.cols(); ++j) {
            std::cout << std::fixed << std::setprecision(8)
                      << std::fabs(hw(i, j) - sw(i, j)) << " ";
        }
        std::cout << "]\n";
    }
    std::cout << "\n";
}

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);

    auto* dut = new Vsub_tensor_core;

    TcuDriver driver(dut, 12);
    driver.reset(4);

    constexpr std::size_t M = 9;
    constexpr std::size_t K = 10;
    constexpr std::size_t N = 11;

    Matrixf A(M, K, 0.0f);
    Matrixf B(K, N, 0.0f);
    Matrixf C(M, N, 0.0f);

    for (std::size_t i = 0; i < M; ++i) {
        for (std::size_t j = 0; j < K; ++j) {
            float sign = ((i + j) % 2 == 0) ? 1.0f : -1.0f;
            A(i, j) = sign * (0.11f * static_cast<float>(i + 1) + 0.07f * static_cast<float>(j + 1));
        }
    }

    for (std::size_t i = 0; i < K; ++i) {
        for (std::size_t j = 0; j < N; ++j) {
            float sign = ((i * 3 + j) % 3 == 0) ? -1.0f : 1.0f;
            B(i, j) = sign * (0.05f * static_cast<float>(i + 1) + 0.09f * static_cast<float>(j + 1));
        }
    }

    for (std::size_t i = 0; i < M; ++i) {
        for (std::size_t j = 0; j < N; ++j) {
            C(i, j) = 0.013f * static_cast<float>(i + 1) + 0.021f * static_cast<float>(j + 1);
        }
    }

    Matrixf hw = matmul_add_tiled(driver, A, B, C, 4);
    Matrixf sw = matmul_add_ref_big(A, B, C);

    print_matrix("HW", hw);
    print_matrix("SW", sw);
    print_diff_matrix(hw, sw);

    float err = max_abs_error(hw, sw);
    std::cout << "Max abs error: " << std::fixed << std::setprecision(10) << err << "\n";

    const float tol = 1e-4f;
    if (err <= tol) {
        std::cout << "RESULT: PASS\n";
    } else {
        std::cout << "RESULT: FAIL\n";
    }

    delete dut;
    return 0;
}
