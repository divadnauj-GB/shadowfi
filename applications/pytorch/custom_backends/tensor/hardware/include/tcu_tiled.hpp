#pragma once

#include "tcu_matrix.hpp"

class TcuDriver;

Matrixf matmul_add_tiled(
    TcuDriver& driver,
    const Matrixf& A,
    const Matrixf& B,
    const Matrixf& C,
    std::size_t tile = 4
);
