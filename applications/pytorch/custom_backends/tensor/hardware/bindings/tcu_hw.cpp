/*
 * bindings/tcu_hw.cpp
 *
 * pybind11 module "tcu_hw" — single Python entry point for both the golden
 * and the FI-instrumented hardware simulations.
 *
 * Two Verilated models are compiled into this shared library:
 *
 *   Golden (obj_dir/)    : Vsub_tensor_core      — no fault injection
 *   FI     (obj_dir_fi/) : Vsub_tensor_core_fi   — saboteur cells in d_unit0
 *
 * Using different Verilator --prefix values prevents the two generated classes
 * from colliding at link time.
 *
 * Python API summary
 * ------------------
 * Types (fault injection only):
 *   FaultMode     — STUCK_AT_0 | STUCK_AT_1 | BIT_FLIP
 *   FaultConfig   — {mode, target_nodes, fault_cycle}
 *
 * Classes:
 *   TcuHardware(tile_latency=12)
 *       .matmul(A, B, C)                — golden hardware run
 *       .tile_latency                   — property (get/set)
 *
 *   TcuFiHardware(sr_length=1534, tile_latency=12)
 *       .matmul(A, B, C)                — golden path through FI model
 *       .matmul_fi(A, B, C, cfg)        — automated FI (configure + arm per tile)
 *       .fi_configure(cfg)              — load shift register
 *       .fi_arm()                       — assert TFEn
 *       .fi_disarm()                    — deassert TFEn
 *       .fi_reset_sr()                  — clear shift register
 *       .tile_latency / .sr_length / .sr_nodes   — properties
 *
 * Module-level:
 *   matmul_ref(A, B, C)                         — software reference
 *   matmul_hw(A, B, C, tile_latency=12)         — stateless golden run
 *   matmul_fi_hw(A, B, C, cfg, sr_length=1534,
 *                tile_latency=12)               — stateless FI run
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>           // automatic std::vector<int> ↔ Python list

// Golden model — class name Vsub_tensor_core, header from obj_dir/
#include "Vsub_tensor_core.h"
#include "tcu_driver.hpp"
#include "tcu_tiled.hpp"

// FI model — class name Vsub_tensor_core_fi, header from obj_dir_fi/
#include "Vsub_tensor_core_fi.h"
#include "tcu_fi_driver.hpp"
#include "tcu_fi_types.hpp"

#include "tcu_matrix.hpp"
#include "tcu_reference.hpp"

#include <memory>
#include <stdexcept>
#include <string>

namespace py = pybind11;

namespace {

// =============================================================================
// Shared NumPy ↔ Matrixf conversion helpers
// =============================================================================

// Convert a 2-D C-contiguous float32 NumPy array to an internal Matrixf.
Matrixf numpy_to_matrix(
    const py::array_t<float, py::array::c_style | py::array::forcecast>& arr
) {
    auto buf = arr.request();
    if (buf.ndim != 2)
        throw std::invalid_argument("Expected a 2D float32 NumPy array");

    const auto rows = static_cast<std::size_t>(buf.shape[0]);
    const auto cols = static_cast<std::size_t>(buf.shape[1]);
    Matrixf out(rows, cols, 0.0f);
    const float* ptr = static_cast<const float*>(buf.ptr);
    for (std::size_t i = 0; i < rows; ++i)
        for (std::size_t j = 0; j < cols; ++j)
            out(i, j) = ptr[i * cols + j];
    return out;
}

// Convert an internal Matrixf to a 2-D float32 NumPy array (row-major).
py::array_t<float> matrix_to_numpy(const Matrixf& M) {
    py::array_t<float> out({static_cast<py::ssize_t>(M.rows()),
                            static_cast<py::ssize_t>(M.cols())});
    auto buf = out.request();
    float* ptr = static_cast<float*>(buf.ptr);
    for (std::size_t i = 0; i < M.rows(); ++i)
        for (std::size_t j = 0; j < M.cols(); ++j)
            ptr[i * M.cols() + j] = M(i, j);
    return out;
}

// Validate that A (M×K), B (K×N), and C (M×N) have compatible shapes for GEMM.
void validate_shapes(const Matrixf& A, const Matrixf& B, const Matrixf& C) {
    if (A.cols() != B.rows())
        throw std::invalid_argument("A.cols() must equal B.rows()");
    if (C.rows() != A.rows() || C.cols() != B.cols())
        throw std::invalid_argument("C must have shape (A.rows(), B.cols())");
}

// =============================================================================
// TcuHardware — golden model wrapper
// =============================================================================

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
        // Release the GIL while the simulation runs so other Python threads
        // are not blocked during long tiled operations.
        { py::gil_scoped_release _; out = matmul_add_tiled(driver_, A, B, C, 4); }
        return matrix_to_numpy(out);
    }

    int  tile_latency() const         { return driver_.tile_latency(); }
    void set_tile_latency(int cycles) { driver_.set_tile_latency(cycles); }

private:
    std::unique_ptr<Vsub_tensor_core> dut_;
    TcuDriver driver_;
};

// =============================================================================
// fi_tiled — tiled GEMM helpers typed to TcuFiDriver
//
// tcu_tiled.hpp / tcu_tiled.cpp are typed to TcuDriver so they cannot be
// reused here directly.  These local helpers duplicate the same pad→tile→crop
// logic but dispatch through TcuFiDriver::run_tile or run_tile_fi.
// =============================================================================

namespace fi_tiled {

// Round x up to the nearest multiple of m.
std::size_t rup(std::size_t x, std::size_t m) { return ((x + m - 1) / m) * m; }

// Zero-pad M to (pr × pc).  Extra rows/columns become 0 so they contribute
// nothing to the dot product when folded into a tile.
Matrixf pad(const Matrixf& M, std::size_t pr, std::size_t pc) {
    Matrixf o(pr, pc, 0.f);
    for (std::size_t i = 0; i < M.rows(); ++i)
        for (std::size_t j = 0; j < M.cols(); ++j)
            o(i, j) = M(i, j);
    return o;
}

// Extract the top-left (r × c) sub-matrix, discarding the padding added above.
Matrixf crop(const Matrixf& M, std::size_t r, std::size_t c) {
    Matrixf o(r, c, 0.f);
    for (std::size_t i = 0; i < r; ++i)
        for (std::size_t j = 0; j < c; ++j)
            o(i, j) = M(i, j);
    return o;
}

// Copy a 4×4 tile from M starting at row r0, column c0.
mat4f load(const Matrixf& M, std::size_t r0, std::size_t c0) {
    mat4f t{};
    for (std::size_t i = 0; i < 4; ++i)
        for (std::size_t j = 0; j < 4; ++j)
            t[i][j] = M(r0 + i, c0 + j);
    return t;
}

// Write a 4×4 tile back into M at row r0, column c0.
void store(Matrixf& M, const mat4f& t, std::size_t r0, std::size_t c0) {
    for (std::size_t i = 0; i < 4; ++i)
        for (std::size_t j = 0; j < 4; ++j)
            M(r0 + i, c0 + j) = t[i][j];
}

// Tiled GEMM without fault injection (uses run_tile — no FI active).
// Used by TcuFiHardware::matmul to provide a golden baseline through the FI model.
Matrixf run_golden(TcuFiDriver& drv,
                   const Matrixf& A, const Matrixf& B, const Matrixf& C) {
    const std::size_t M = A.rows(), K = A.cols(), N = B.cols();
    const std::size_t Mp = rup(M,4), Kp = rup(K,4), Np = rup(N,4);
    Matrixf Ap = pad(A, Mp, Kp), Bp = pad(B, Kp, Np), Cp = pad(C, Mp, Np);
    Matrixf Out(Mp, Np, 0.f);
    for (std::size_t i = 0; i < Mp; i += 4)
        for (std::size_t j = 0; j < Np; j += 4) {
            mat4f acc = load(Cp, i, j);
            for (std::size_t k = 0; k < Kp; k += 4)
                acc = drv.run_tile(load(Ap,i,k), load(Bp,k,j), acc);
            store(Out, acc, i, j);
        }
    return crop(Out, M, N);
}

// Tiled GEMM with fault injection applied to every tile (uses run_tile_fi).
// The shift register is reprogrammed and TFEn is managed by run_tile_fi on
// each individual tile, so the same fault is injected consistently throughout
// the entire matrix operation.
Matrixf run_fi(TcuFiDriver& drv,
               const Matrixf& A, const Matrixf& B, const Matrixf& C,
               const FaultConfig& cfg) {
    const std::size_t M = A.rows(), K = A.cols(), N = B.cols();
    const std::size_t Mp = rup(M,4), Kp = rup(K,4), Np = rup(N,4);
    Matrixf Ap = pad(A, Mp, Kp), Bp = pad(B, Kp, Np), Cp = pad(C, Mp, Np);
    Matrixf Out(Mp, Np, 0.f);
    for (std::size_t i = 0; i < Mp; i += 4)
        for (std::size_t j = 0; j < Np; j += 4) {
            mat4f acc = load(Cp, i, j);
            for (std::size_t k = 0; k < Kp; k += 4)
                acc = drv.run_tile_fi(load(Ap,i,k), load(Bp,k,j), acc, cfg);
            store(Out, acc, i, j);
        }
    return crop(Out, M, N);
}

}  // namespace fi_tiled

// =============================================================================
// TcuFiHardware — FI-instrumented model wrapper
// =============================================================================

class TcuFiHardware {
public:
    // sr_length must match the shift register width of the FI-instrumented RTL
    // (1534 for fpadd_3_pipe_sbtr, the only currently instrumented stage).
    explicit TcuFiHardware(int sr_length = 1534, int tile_latency = 12)
        : dut_(std::make_unique<Vsub_tensor_core_fi>()),
          driver_(dut_.get(), FiHwParams{sr_length}, tile_latency) {
        driver_.reset(4);
    }

    // ---- Golden path through the FI model (no fault active) ----------------

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
        { py::gil_scoped_release _; out = fi_tiled::run_golden(driver_, A, B, C); }
        return matrix_to_numpy(out);
    }

    // ---- Automated FI path (configure + arm per tile) ----------------------

    py::array_t<float> matmul_fi(
        const py::array_t<float, py::array::c_style | py::array::forcecast>& A_in,
        const py::array_t<float, py::array::c_style | py::array::forcecast>& B_in,
        const py::array_t<float, py::array::c_style | py::array::forcecast>& C_in,
        const FaultConfig& cfg
    ) {
        Matrixf A = numpy_to_matrix(A_in);
        Matrixf B = numpy_to_matrix(B_in);
        Matrixf C = numpy_to_matrix(C_in);
        validate_shapes(A, B, C);
        driver_.reset(4);
        Matrixf out;
        { py::gil_scoped_release _; out = fi_tiled::run_fi(driver_, A, B, C, cfg); }
        return matrix_to_numpy(out);
    }

    // ---- Manual FI control (exposed to Python for granular use) ------------

    // Load the shift register with the fault described by cfg.
    // Does not activate the fault; call fi_arm() afterwards.
    void fi_configure(const FaultConfig& cfg) { driver_.fi_configure(cfg); }

    // Assert TFEn: saboteurs become active on the next computation tick.
    // The fault remains active until fi_disarm() is called.
    void fi_arm()      { driver_.fi_arm();    }

    // Deassert TFEn: saboteurs are disabled immediately.
    void fi_disarm()   { driver_.fi_disarm(); }

    // Reset the shift register to all-zeros (clears any previously loaded config).
    void fi_reset_sr() { driver_.fi_reset();  }

    // ---- Properties --------------------------------------------------------

    int  tile_latency() const         { return driver_.tile_latency();          }
    void set_tile_latency(int cycles) { driver_.set_tile_latency(cycles);       }

    // Total SR bits (saboteur enables + 2 ctrl bits).
    int sr_length() const { return driver_.hw_params().sr_length; }

    // Number of independently addressable saboteur nodes (= sr_length - 2).
    int sr_nodes()  const { return driver_.hw_params().sr_nodes(); }

private:
    std::unique_ptr<Vsub_tensor_core_fi> dut_;
    TcuFiDriver driver_;
};

// =============================================================================
// Module-level stateless convenience functions
// =============================================================================

// Pure software reference (no Verilated model): A @ B + C in float32.
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

// Stateless golden hardware run: creates a fresh TcuHardware, executes, discards.
py::array_t<float> matmul_hw_py(
    const py::array_t<float, py::array::c_style | py::array::forcecast>& A_in,
    const py::array_t<float, py::array::c_style | py::array::forcecast>& B_in,
    const py::array_t<float, py::array::c_style | py::array::forcecast>& C_in,
    int tile_latency = 12
) {
    TcuHardware hw(tile_latency);
    return hw.matmul(A_in, B_in, C_in);
}

// Stateless FI hardware run: creates a fresh TcuFiHardware, executes with the
// given fault config, discards.  Convenient for one-shot experiments.
py::array_t<float> matmul_fi_hw_py(
    const py::array_t<float, py::array::c_style | py::array::forcecast>& A_in,
    const py::array_t<float, py::array::c_style | py::array::forcecast>& B_in,
    const py::array_t<float, py::array::c_style | py::array::forcecast>& C_in,
    const FaultConfig& cfg,
    int sr_length    = 1534,
    int tile_latency = 12
) {
    TcuFiHardware hw(sr_length, tile_latency);
    return hw.matmul_fi(A_in, B_in, C_in, cfg);
}

}  // namespace

// =============================================================================
// Module registration
// =============================================================================

PYBIND11_MODULE(tcu_hw, m) {
    m.doc() = "TCU hardware backend: golden simulation and fault-injection simulation";

    // ---- Fault injection types ----

    py::enum_<FaultMode>(m, "FaultMode",
        "Fault injection mode applied to every enabled saboteur node.\n\n"
        "  STUCK_AT_0 : force the node output to 0 for the entire tile\n"
        "  STUCK_AT_1 : force the node output to 1 for the entire tile\n"
        "  BIT_FLIP   : invert the node output for exactly one clock cycle\n"
        "               (controlled by FaultConfig.fault_cycle)")
        .value("STUCK_AT_0", FaultMode::STUCK_AT_0)
        .value("STUCK_AT_1", FaultMode::STUCK_AT_1)
        .value("BIT_FLIP",   FaultMode::BIT_FLIP)
        .export_values();

    py::class_<FaultConfig>(m, "FaultConfig",
        "Complete specification of one fault injection experiment.\n\n"
        "Attributes\n"
        "----------\n"
        "mode         : FaultMode\n"
        "    Fault type applied to every node listed in target_nodes.\n"
        "target_nodes : list[int]\n"
        "    Indices of saboteur nodes to arm (0 .. sr_nodes-1).\n"
        "    An empty list means no fault is injected (useful as a baseline).\n"
        "fault_cycle  : int\n"
        "    Pipeline cycle at which TFEn is pulsed (BIT_FLIP only).\n"
        "    Range: [1, tile_latency].  Ignored for STUCK_AT modes.")
        .def(py::init<>())
        .def(py::init([](FaultMode mode, std::vector<int> nodes, int fc) {
                FaultConfig c;
                c.mode         = mode;
                c.target_nodes = std::move(nodes);
                c.fault_cycle  = fc;
                return c;
             }),
             py::arg("mode"), py::arg("target_nodes"), py::arg("fault_cycle") = 6)
        .def_readwrite("mode",         &FaultConfig::mode)
        .def_readwrite("target_nodes", &FaultConfig::target_nodes)
        .def_readwrite("fault_cycle",  &FaultConfig::fault_cycle)
        .def("__repr__", [](const FaultConfig& c) {
            return "<FaultConfig mode=" + std::to_string(static_cast<int>(c.mode)) +
                   " nodes=" + std::to_string(c.target_nodes.size()) +
                   " fault_cycle=" + std::to_string(c.fault_cycle) + ">";
        });

    // ---- TcuHardware — golden ----

    py::class_<TcuHardware>(m, "TcuHardware",
        "Cycle-accurate simulation of the golden TCU (no fault injection).\n\n"
        "Wraps the Verilated model from obj_dir/ (prefix Vsub_tensor_core).")
        .def(py::init<int>(), py::arg("tile_latency") = 12)
        .def("matmul", &TcuHardware::matmul,
             py::arg("A"), py::arg("B"), py::arg("C"),
             "Compute A @ B + C on the golden hardware model.\n"
             "Inputs must be 2-D float32 NumPy arrays.")
        .def_property("tile_latency",
                      &TcuHardware::tile_latency,
                      &TcuHardware::set_tile_latency,
                      "Clock cycles per 4×4 tile computation.");

    // ---- TcuFiHardware — FI model ----

    py::class_<TcuFiHardware>(m, "TcuFiHardware",
        "Cycle-accurate simulation of the FI-instrumented TCU.\n\n"
        "Wraps the Verilated model from obj_dir_fi/ (prefix Vsub_tensor_core_fi).\n"
        "Only d_unit0 is instrumented: faults affect the W[0][0] output element.\n\n"
        "Two usage patterns\n"
        "------------------\n"
        "Automated — fault applied automatically to every tile:\n"
        "    hw = TcuFiHardware()\n"
        "    out = hw.matmul_fi(A, B, C, cfg)\n\n"
        "Manual — granular control from Python:\n"
        "    hw.fi_configure(cfg)   # program the shift register\n"
        "    hw.fi_arm()            # assert TFEn (fault becomes active)\n"
        "    out = hw.matmul(A, B, C)\n"
        "    hw.fi_disarm()         # deassert TFEn")
        .def(py::init<int, int>(),
             py::arg("sr_length")    = 1534,
             py::arg("tile_latency") = 12)
        .def("matmul", &TcuFiHardware::matmul,
             py::arg("A"), py::arg("B"), py::arg("C"),
             "Run A @ B + C with no fault active.\n"
             "Useful as a within-model golden baseline.")
        .def("matmul_fi", &TcuFiHardware::matmul_fi,
             py::arg("A"), py::arg("B"), py::arg("C"), py::arg("cfg"),
             "Run A @ B + C with the specified fault applied to every tile.\n"
             "The shift register is configured and TFEn is managed automatically.")
        .def("fi_configure", &TcuFiHardware::fi_configure,
             py::arg("cfg"),
             "Load the shift register with the fault configuration.\n"
             "The fault is NOT active after this call; invoke fi_arm() to activate it.")
        .def("fi_arm", &TcuFiHardware::fi_arm,
             "Assert TFEn: saboteurs become active on the next computation cycle.\n"
             "The fault remains active until fi_disarm() is called.")
        .def("fi_disarm", &TcuFiHardware::fi_disarm,
             "Deassert TFEn: saboteurs are disabled immediately.")
        .def("fi_reset_sr", &TcuFiHardware::fi_reset_sr,
             "Reset the shift register to all-zeros,\n"
             "clearing any previously loaded fault configuration.")
        .def_property("tile_latency",
                      &TcuFiHardware::tile_latency,
                      &TcuFiHardware::set_tile_latency,
                      "Clock cycles per 4×4 tile computation.")
        .def_property_readonly("sr_length", &TcuFiHardware::sr_length,
                               "Total shift register length (saboteur enables + 2 ctrl bits).")
        .def_property_readonly("sr_nodes",  &TcuFiHardware::sr_nodes,
                               "Number of independently addressable saboteur nodes.");

    // ---- Module-level convenience functions ----

    m.def("matmul_ref", &matmul_ref_py,
          py::arg("A"), py::arg("B"), py::arg("C"),
          "Software reference: A @ B + C (no hardware simulation).");

    m.def("matmul_hw", &matmul_hw_py,
          py::arg("A"), py::arg("B"), py::arg("C"),
          py::arg("tile_latency") = 12,
          "Stateless golden hardware matmul.\n"
          "Creates a fresh TcuHardware instance for each call.");

    m.def("matmul_fi_hw", &matmul_fi_hw_py,
          py::arg("A"), py::arg("B"), py::arg("C"), py::arg("cfg"),
          py::arg("sr_length") = 1534, py::arg("tile_latency") = 12,
          "Stateless FI hardware matmul.\n"
          "Creates a fresh TcuFiHardware instance for each call.");
}
