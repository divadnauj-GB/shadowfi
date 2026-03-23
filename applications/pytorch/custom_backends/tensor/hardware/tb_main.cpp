#include <verilated.h>
#include "Vsub_tensor_core.h"

#include "tcu_driver.hpp"
#include "tcu_reference.hpp"
#include "tcu_utils.hpp"

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);

    auto* dut = new Vsub_tensor_core;
    TcuDriver driver(dut);

    mat4f A = {{
        {1.2f,  2.3f,  3.4f,  4.5f},
        {5.1f,  6.2f,  7.3f,  8.4f},
        {9.5f, 10.6f, 11.7f, 12.8f},
        {13.9f, 14.1f, 15.2f, 16.3f}
    }};

    mat4f B = {{
        {0.5f,  1.0f,  1.5f,  2.0f},
        {2.5f,  3.0f,  3.5f,  4.0f},
        {4.5f,  5.0f,  5.5f,  6.0f},
        {6.5f,  7.0f,  7.5f,  8.0f}
    }};

    mat4f C = {{
        {1.0f,  0.5f,  0.25f, 0.0f},
        {0.0f,  1.0f,  0.5f,  0.25f},
        {0.25f, 0.0f,  1.0f,  0.5f},
        {0.5f,  0.25f, 0.0f,  1.0f}
    }};

    mat4f W_ref = matmul_add_ref(A, B, C);

    driver.load_inputs(A, B, C);
    driver.reset(4);
    driver.tick(30);

    mat4f W_hw = driver.read_W();

    print_mat("A", A);
    print_mat("B", B);
    print_mat("C", C);
    print_mat("HW RESULT", W_hw);
    print_mat("REF RESULT", W_ref);
    print_abs_error("ABS ERROR", W_hw, W_ref);

    delete dut;
    return 0;
}
