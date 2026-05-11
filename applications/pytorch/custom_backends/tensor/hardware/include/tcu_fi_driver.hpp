#pragma once

/*
 * tcu_fi_driver.hpp
 *
 * TcuFiDriver drives the FI-instrumented Verilated model of sub_tensor_core.
 *
 * It mirrors TcuDriver's golden interface (tick / reset / load / read / run_tile)
 * so it can be used as a drop-in replacement for correctness testing, and adds
 * four FI-specific methods that control the saboteur shift register and its
 * trigger.
 *
 * Two operating modes
 * -------------------
 * 1. Automated (one call):
 *       run_tile_fi(A, B, C, cfg)
 *    Internally: configure SR → arm → run → disarm → read.
 *
 * 2. Manual (granular control):
 *       fi_configure(cfg)   load the SR with the desired fault
 *       fi_arm()            assert TFEn (fault becomes active)
 *       run_tile(A, B, C)   execute without per-tile reconfiguration
 *       fi_disarm()         deassert TFEn
 *    Useful when the same fault must persist across multiple tiles or when
 *    fault activation needs to be timed externally.
 *
 * Clock domains
 * -------------
 * The DUT has two independent clock domains:
 *   - Main computation clock : driven via dut_->clk, advanced by tick()
 *   - SR configuration clock : driven via i_FI_CONTROL_PORT[3], advanced
 *     by fi_sr_tick() exclusively during fi_configure / fi_reset.
 * Both are driven directly from software — no hardware clock generator is
 * involved in the Verilated simulation.
 *
 * Verilated model prefix
 * ----------------------
 * The FI model is verilated with --prefix Vsub_tensor_core_fi so its class
 * name differs from the golden model (Vsub_tensor_core).  This allows both
 * to be linked into the same shared library without symbol collisions.
 */

#include "tcu_fi_types.hpp"
#include "tcu_types.hpp"
#include "tcu_matrix.hpp"

class Vsub_tensor_core_fi;

class TcuFiDriver {
public:
    // hw_params must match the SR geometry of the specific FI-instrumented RTL
    // being driven (e.g. FiHwParams{1534} for fpadd_3_pipe_sbtr).
    TcuFiDriver(Vsub_tensor_core_fi* dut, FiHwParams hw_params, int tile_latency = 12);

    const FiHwParams& hw_params() const { return hw_params_; }

    // -------------------------------------------------------------------------
    // Main computation interface (mirrors TcuDriver)
    // -------------------------------------------------------------------------

    // Advance the main DUT clock by one cycle (low→eval→high→eval).
    void tick();
    void tick(int cycles);

    // Assert rst for `cycles` main clock cycles, then deassert.
    void reset(int cycles = 4);

    // Load matrix rows A, columns B, and columns C onto the DUT input buses.
    // C is transposed internally to column-major to match the hardware port layout.
    void load_A(const mat4f& A);
    void load_B(const mat4f& B);
    void load_C(const mat4f& C);
    void load_inputs(const mat4f& A, const mat4f& B, const mat4f& C);

    // Read the result matrix W from the DUT output buses.
    mat4f read_W() const;

    // Load inputs, advance tile_latency cycles, and read W back.
    // No fault is active — this provides a golden reference through the FI model.
    mat4f run_tile(const mat4f& A, const mat4f& B, const mat4f& C);

    int  tile_latency() const         { return tile_latency_; }
    void set_tile_latency(int cycles) { tile_latency_ = cycles; }

    // -------------------------------------------------------------------------
    // FI-specific interface
    // -------------------------------------------------------------------------

    // Reset the SR chain: drive RST low, pulse the SR clock several times to
    // flush any stale state, then release RST.  Called automatically at the
    // start of fi_configure.
    void fi_reset();

    // Program the shift register with the fault described by cfg:
    //   1. fi_reset() — clears the SR
    //   2. Assert EN=1, then clock in sr_length bits (LSB-first, see tcu_fi_types.hpp)
    //   3. Deassert EN
    // Does NOT activate the fault; call fi_arm() afterwards.
    void fi_configure(const FaultConfig& cfg);

    // Assert TFEn (i_FI_CONTROL_PORT[1] = 1).
    // Saboteurs become active combinationally on the next eval().
    void fi_arm();

    // Deassert TFEn (i_FI_CONTROL_PORT[1] = 0).
    // Saboteurs are immediately disabled regardless of pipeline state.
    void fi_disarm();

    // High-level fault injection run that handles timing automatically:
    //   STUCK_AT  : arm before the tile, disarm after tick(tile_latency)
    //   BIT_FLIP  : tick(fault_cycle-1) without fault, pulse TFEn for one
    //               cycle, then tick the remaining cycles
    mat4f run_tile_fi(const mat4f& A, const mat4f& B, const mat4f& C,
                      const FaultConfig& cfg);

private:
    Vsub_tensor_core_fi* dut_;
    FiHwParams           hw_params_;
    int                  tile_latency_;
    uint8_t              fi_ctrl_ = 0;  // shadow of the live i_FI_CONTROL_PORT value

    // Write ctrl to i_FI_CONTROL_PORT and call eval() to propagate combinationally.
    void fi_set_ctrl(uint8_t ctrl);

    // Pulse the SR clock once (CLK low→eval→high→eval).
    // Only affects the SR domain; the main DUT clock is not touched.
    void fi_sr_tick();
};
