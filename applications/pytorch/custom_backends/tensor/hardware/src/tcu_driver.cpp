#include "tcu_driver.hpp"

#include "Vsub_tensor_core.h"
#include "tcu_utils.hpp"

TcuDriver::TcuDriver(Vsub_tensor_core* dut, int tile_latency)
    : dut_(dut), tile_latency_(tile_latency) {}

void TcuDriver::tick() {
    dut_->clk = 0;
    dut_->eval();

    dut_->clk = 1;
    dut_->eval();
}

void TcuDriver::tick(int cycles) {
    for (int i = 0; i < cycles; ++i) {
        tick();
    }
}

void TcuDriver::reset(int cycles) {
    dut_->clk = 0;
    dut_->rst = 1;
    tick(cycles);
    dut_->rst = 0;
}

void TcuDriver::load_A(const mat4f& A) {
    pack4(dut_->A_0X, A[0]);
    pack4(dut_->A_1X, A[1]);
    pack4(dut_->A_2X, A[2]);
    pack4(dut_->A_3X, A[3]);
}

void TcuDriver::load_B(const mat4f& B) {
    pack4(dut_->B_0X, B[0]);
    pack4(dut_->B_1X, B[1]);
    pack4(dut_->B_2X, B[2]);
    pack4(dut_->B_3X, B[3]);
}

void TcuDriver::load_C(const mat4f& C) {
    pack4(dut_->C_0X, C[0]);
    pack4(dut_->C_1X, C[1]);
    pack4(dut_->C_2X, C[2]);
    pack4(dut_->C_3X, C[3]);
}

void TcuDriver::load_inputs(const mat4f& A, const mat4f& B, const mat4f& C) {
    load_A(A);
    load_B(B);
    load_C(C);
}

mat4f TcuDriver::read_W() const {
    mat4f W{};
    W[0] = unpack4(dut_->W_0X3);
    W[1] = unpack4(dut_->W_1X3);
    W[2] = unpack4(dut_->W_2X3);
    W[3] = unpack4(dut_->W_3X3);
    return W;
}

mat4f TcuDriver::run_tile(const mat4f& A, const mat4f& B, const mat4f& C) {
    load_inputs(A, B, C);
    tick(tile_latency_);
    return read_W();
}
