#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include "Vsub_tensor_core.h"
#include "tcu_driver.hpp"
#include "tcu_matrix.hpp"
#include "tcu_reference.hpp"
#include "tcu_tiled.hpp"

#include <memory>
#include <stdexcept>
#include <string>

namespace py = pybind11;

namespace {

Matrixf numpy_to_matrix(
    const py::array_t<float, py::array::c_style | py::array::forcecast>& arr
) {
    auto buf = arr.request();

    if (buf.ndim != 2) {
        throw std::invalid_argument("Expected a 2D float32 NumPy array");
    }

    const auto rows = static_cast<std::size_t>(buf.shape[0]);
    const auto cols = static_cast<std::size_t>(buf.shape[1]);

    Matrixf out(rows, cols, 0.0f);
    const float* ptr = static_cast<const float*>(buf.ptr);

    for (std::size_t i = 0; i < rows; ++i) {
        for (std::size_t j = 0; j < cols; ++j) {
            out(i, j) = ptr[i * cols + j];
        }
    }

    return out;
}

py::array_t<float> matrix_to_numpy(const Matrixf& M) {
    py::array_t<float> out({static_cast<py::ssize_t>(M.rows()),
                            static_cast<py::ssize_t>(M.cols())});

    auto buf = out.request();
    float* ptr = static_cast<float*>(buf.ptr);

    for (std::size_t i = 0; i < M.rows(); ++i) {
        for (std::size_t j = 0; j < M.cols(); ++j) {
            ptr[i * M.cols() + j] = M(i, j);
        }
    }

    return out;
}

void validate_shapes(const Matrixf& A, const Matrixf& B, const Matrixf& C) {
    if (A.cols() != B.rows()) {
        throw std::invalid_argument(
            "Invalid shapes: A.shape=(M,K), B.shape=(K,N) required"
        );
    }
    if (C.rows() != A.rows() || C.cols() != B.cols()) {
        throw std::invalid_argument(
            "Invalid shapes: C must have shape (A.rows(), B.cols())"
        );
    }
}

class TcuHardware {
public:
    explicit TcuHardware(int tile_latency = 12)
        : dut_(std::make_unique<Vsub_tensor_core>()),
          driver_(dut_.get(), tile_latency) {
        driver_.reset(4);
    }

    py::array_t<float> matmul(
        const py::array_t<float, py::array::c_style | py::array::forcecast>& A_in,
        const py::array_t<float, py::array::c_style | py::array::forcecast>& B_in,
        const py::array_t<float, py::array::c_style | py::array::forcecast>& C_in
    ) {
        Matrixf A = numpy_to_matrix(A_in);
        Matrixf B = numpy_to_matrix(B_in);
        Matrixf C = numpy_to_matrix(C_in);

        validate_shapes(A, B, C);

        driver_.reset(4);

        Matrixf out;
        {
            py::gil_scoped_release release;
            out = matmul_add_tiled(driver_, A, B, C, 4);
        }

        return matrix_to_numpy(out);
    }

    int tile_latency() const {
        return driver_.tile_latency();
    }

    void set_tile_latency(int cycles) {
        driver_.set_tile_latency(cycles);
    }

private:
    std::unique_ptr<Vsub_tensor_core> dut_;
    TcuDriver driver_;
};

py::array_t<float> matmul_ref_py(
    const py::array_t<float, py::array::c_style | py::array::forcecast>& A_in,
    const py::array_t<float, py::array::c_style | py::array::forcecast>& B_in,
    const py::array_t<float, py::array::c_style | py::array::forcecast>& C_in
) {
    Matrixf A = numpy_to_matrix(A_in);
    Matrixf B = numpy_to_matrix(B_in);
    Matrixf C = numpy_to_matrix(C_in);

    validate_shapes(A, B, C);
    return matrix_to_numpy(matmul_add_ref_big(A, B, C));
}

py::array_t<float> matmul_hw_py(
    const py::array_t<float, py::array::c_style | py::array::forcecast>& A_in,
    const py::array_t<float, py::array::c_style | py::array::forcecast>& B_in,
    const py::array_t<float, py::array::c_style | py::array::forcecast>& C_in,
    int tile_latency = 12
) {
    TcuHardware hw(tile_latency);
    return hw.matmul(A_in, B_in, C_in);
}

}  // namespace

PYBIND11_MODULE(tcu_hw, m) {
    m.doc() = "pybind11 wrapper for Verilated sub_tensor_core tiled matmul";

    m.def("matmul_ref", &matmul_ref_py,
          py::arg("A"), py::arg("B"), py::arg("C"),
          "Software reference: A @ B + C");

    m.def("matmul_hw", &matmul_hw_py,
          py::arg("A"), py::arg("B"), py::arg("C"),
          py::arg("tile_latency") = 12,
          "Hardware tiled matmul: A @ B + C");

    py::class_<TcuHardware>(m, "TcuHardware")
        .def(py::init<int>(), py::arg("tile_latency") = 12)
        .def("matmul", &TcuHardware::matmul,
             py::arg("A"), py::arg("B"), py::arg("C"))
        .def_property("tile_latency",
                      &TcuHardware::tile_latency,
                      &TcuHardware::set_tile_latency);
}
