#pragma once

#include "tcu_types.hpp"

class Vsub_tensor_core;

class TcuDriver {
public:
    explicit TcuDriver(Vsub_tensor_core* dut);

    void reset(int cycles = 4);
    void tick();
    void tick(int cycles);

    void load_A(const mat4f& A);
    void load_B(const mat4f& B);
    void load_C(const mat4f& C);

    void load_inputs(const mat4f& A, const mat4f& B, const mat4f& C);

    mat4f read_W() const;

private:
    Vsub_tensor_core* dut_;
};
