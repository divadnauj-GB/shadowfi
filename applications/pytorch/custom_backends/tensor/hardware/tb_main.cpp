#include <verilated.h>
#include "Vsub_tensor_core.h"

#include "tcu_driver.hpp"
#include "tcu_matrix.hpp"
#include "tcu_reference.hpp"
#include "tcu_tiled.hpp"

#include <cmath>
#include <iomanip>
#include <iostream>

static void print_matrix(const char* name, const Matrixf& M) {
    std::cout << name << "\n";
    for (std::size_t i = 0; i < M.rows(); ++i) {
        std::cout << "[ ";
        for (std::size_t j = 0; j < M.cols(); ++j) {
            std::cout << std::fixed << std::setprecision(4) << M(i, j) << " ";
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

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);

    auto* dut = new Vsub_tensor_core;
    TcuDriver driver(dut, 30);

    driver.reset(4);

    Matrixf A(8, 8, 0.0f);
    Matrixf B(8, 8, 0.0f);
    Matrixf C(8, 8, 0.0f);

    for (std::size_t i = 0; i < 8; ++i) {
        for (std::size_t j = 0; j < 8; ++j) {
            A(i, j) = 0.1f * static_cast<float>(i + 1) + static_cast<float>(j);
            B(i, j) = 0.2f * static_cast<float>(j + 1) - 0.05f * static_cast<float>(i);
            C(i, j) = (i == j) ? 1.0f : 0.25f;
        }
    }

    Matrixf hw = matmul_add_tiled(driver, A, B, C, 4);
    Matrixf sw = matmul_add_ref_big(A, B, C);

    print_matrix("HW", hw);
    print_matrix("SW", sw);
    std::cout << "Max abs error: " << max_abs_error(hw, sw) << "\n";

    delete dut;
    return 0;
}
