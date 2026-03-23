#include "tcu_tiled.hpp"

#include "tcu_driver.hpp"
#include "tcu_types.hpp"

#include <algorithm>
#include <stdexcept>

namespace {

std::size_t round_up(std::size_t x, std::size_t multiple) {
    return ((x + multiple - 1) / multiple) * multiple;
}

Matrixf pad_matrix(const Matrixf& M, std::size_t padded_rows, std::size_t padded_cols) {
    Matrixf out(padded_rows, padded_cols, 0.0f);
    for (std::size_t i = 0; i < M.rows(); ++i) {
        for (std::size_t j = 0; j < M.cols(); ++j) {
            out(i, j) = M(i, j);
        }
    }
    return out;
}

mat4f load_tile_4x4(const Matrixf& M, std::size_t row0, std::size_t col0) {
    mat4f tile{};
    for (std::size_t i = 0; i < 4; ++i) {
        for (std::size_t j = 0; j < 4; ++j) {
            tile[i][j] = M(row0 + i, col0 + j);
        }
    }
    return tile;
}

void store_tile_4x4(Matrixf& M, const mat4f& tile, std::size_t row0, std::size_t col0) {
    for (std::size_t i = 0; i < 4; ++i) {
        for (std::size_t j = 0; j < 4; ++j) {
            M(row0 + i, col0 + j) = tile[i][j];
        }
    }
}

Matrixf crop_matrix(const Matrixf& M, std::size_t rows, std::size_t cols) {
    Matrixf out(rows, cols, 0.0f);
    for (std::size_t i = 0; i < rows; ++i) {
        for (std::size_t j = 0; j < cols; ++j) {
            out(i, j) = M(i, j);
        }
    }
    return out;
}

}  // namespace

Matrixf matmul_add_tiled(
    TcuDriver& driver,
    const Matrixf& A,
    const Matrixf& B,
    const Matrixf& C,
    std::size_t tile
) {
    if (tile != 4) {
        throw std::invalid_argument("Current hardware supports only 4x4 tiles");
    }

    if (A.cols() != B.rows()) {
        throw std::invalid_argument("A.cols() must equal B.rows()");
    }

    if (A.rows() != C.rows() || B.cols() != C.cols()) {
        throw std::invalid_argument("C must have shape (A.rows(), B.cols())");
    }

    const std::size_t M = A.rows();
    const std::size_t K = A.cols();
    const std::size_t N = B.cols();

    const std::size_t Mp = round_up(M, tile);
    const std::size_t Kp = round_up(K, tile);
    const std::size_t Np = round_up(N, tile);

    Matrixf Ap = pad_matrix(A, Mp, Kp);
    Matrixf Bp = pad_matrix(B, Kp, Np);
    Matrixf Cp = pad_matrix(C, Mp, Np);

    Matrixf Out = Cp;

    for (std::size_t i = 0; i < Mp; i += tile) {
        for (std::size_t j = 0; j < Np; j += tile) {
            // Start with the incoming C tile
            mat4f accum = load_tile_4x4(Out, i, j);

            for (std::size_t k = 0; k < Kp; k += tile) {
                const mat4f At = load_tile_4x4(Ap, i, k);
                const mat4f Bt = load_tile_4x4(Bp, k, j);

                // Hardware computes: At @ Bt + accum
                accum = driver.run_tile(At, Bt, accum);
            }

            store_tile_4x4(Out, accum, i, j);
        }
    }

    return crop_matrix(Out, M, N);
}
