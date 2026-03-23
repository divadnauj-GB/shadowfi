#pragma once

#include "tcu_types.hpp"

class Vsub_tensor_core;

class TcuDriver {
public:
    explicit TcuDriver(Vsub_tensor_core* dut, int tile_latency = 30);

    void reset(int cycles = 4);
    void tick();
    void tick(int cycles);

    void load_A(const mat4f& A);
    void load_B(const mat4f& B);
    void load_C(const mat4f& C);
    void load_inputs(const mat4f& A, const mat4f& B, const mat4f& C);

    mat4f read_W() const;

    mat4f run_tile(const mat4f& A, const mat4f& B, const mat4f& C);

    int tile_latency() const { return tile_latency_; }
    void set_tile_latency(int cycles) { tile_latency_ = cycles; }

private:
    Vsub_tensor_core* dut_;
    int tile_latency_;
};
