#include <verilated.h>
#include "Vsub_tensor_core.h"

#include <array>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <cmath>

using std::array;
using std::cout;
using std::endl;

typedef array<array<float,4>,4> mat4;

static uint32_t float_to_u32(float x) {
    uint32_t out;
    std::memcpy(&out, &x, sizeof(uint32_t));
    return out;
}

static float u32_to_float(uint32_t x) {
    float out;
    std::memcpy(&out, &x, sizeof(float));
    return out;
}

static void pack4(WData* bus, const array<float,4>& v) {
    bus[0] = float_to_u32(v[0]);
    bus[1] = float_to_u32(v[1]);
    bus[2] = float_to_u32(v[2]);
    bus[3] = float_to_u32(v[3]);
}

static array<float,4> unpack4(const WData* bus) {
    return {
        u32_to_float(bus[0]),
        u32_to_float(bus[1]),
        u32_to_float(bus[2]),
        u32_to_float(bus[3])
    };
}

static mat4 matmul_ref(const mat4& A, const mat4& B, const mat4& C) {
    mat4 W{};

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

static void print_mat(const char* name, const mat4& M) {
    cout << name << endl;
    for (int i = 0; i < 4; ++i) {
        cout << "[ ";
        for (int j = 0; j < 4; ++j) {
            cout << std::fixed << std::setprecision(6) << M[i][j] << " ";
        }
        cout << "]" << endl;
    }
    cout << endl;
}

static void tick(Vsub_tensor_core* top) {
    top->clk = 0;
    top->eval();

    top->clk = 1;
    top->eval();
}

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);

    auto* top = new Vsub_tensor_core;

    top->clk = 0;
    top->rst = 1;

    mat4 A = {{
        {1.2f,  2.3f,  3.4f,  4.5f},
        {5.1f,  6.2f,  7.3f,  8.4f},
        {9.5f, 10.6f, 11.7f, 12.8f},
        {13.9f,14.1f, 15.2f, 16.3f}
    }};

    mat4 B = {{
        {0.5f,  1.0f,  1.5f,  2.0f},
        {2.5f,  3.0f,  3.5f,  4.0f},
        {4.5f,  5.0f,  5.5f,  6.0f},
        {6.5f,  7.0f,  7.5f,  8.0f}
    }};

    mat4 C = {{
        {1.0f,  0.5f,  0.25f, 0.0f},
        {0.0f,  1.0f,  0.5f,  0.25f},
        {0.25f, 0.0f,  1.0f,  0.5f},
        {0.5f,  0.25f, 0.0f,  1.0f}
    }};

    mat4 W_ref = matmul_ref(A, B, C);

    pack4(top->A_0X, A[0]);
    pack4(top->A_1X, A[1]);
    pack4(top->A_2X, A[2]);
    pack4(top->A_3X, A[3]);

    pack4(top->B_0X, B[0]);
    pack4(top->B_1X, B[1]);
    pack4(top->B_2X, B[2]);
    pack4(top->B_3X, B[3]);

    pack4(top->C_0X, C[0]);
    pack4(top->C_1X, C[1]);
    pack4(top->C_2X, C[2]);
    pack4(top->C_3X, C[3]);

    // reset
    for (int i = 0; i < 4; ++i) tick(top);
    top->rst = 0;

    // pipeline latency
    for (int i = 0; i < 30; ++i) tick(top);

    mat4 W_hw;

    W_hw[0] = unpack4(top->W_0X3);
    W_hw[1] = unpack4(top->W_1X3);
    W_hw[2] = unpack4(top->W_2X3);
    W_hw[3] = unpack4(top->W_3X3);

    print_mat("A", A);
    print_mat("B", B);
    print_mat("C", C);
    print_mat("HW RESULT", W_hw);
    print_mat("REF RESULT", W_ref);

    cout << "Error (abs):" << endl;
    for (int i = 0; i < 4; ++i) {
        cout << "[ ";
        for (int j = 0; j < 4; ++j) {
            float err = std::fabs(W_hw[i][j] - W_ref[i][j]);
            cout << std::fixed << std::setprecision(6) << err << " ";
        }
        cout << "]" << endl;
    }

    delete top;
    return 0;
}
