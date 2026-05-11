#include "tcu_fi_driver.hpp"

#include "Vsub_tensor_core_fi.h"  // verilated with --prefix Vsub_tensor_core_fi
#include "tcu_utils.hpp"

#include <stdexcept>

TcuFiDriver::TcuFiDriver(Vsub_tensor_core_fi* dut, FiHwParams hw_params, int tile_latency)
    : dut_(dut), hw_params_(hw_params), tile_latency_(tile_latency), fi_ctrl_(0) {
    // Start with RST asserted (active-low = 0) so the SR is in a known-clear
    // state from the very first eval().
    fi_set_ctrl(0);
}

// =============================================================================
// Main computation clock (mirrors TcuDriver)
// =============================================================================

void TcuFiDriver::tick() {
    dut_->clk = 0;
    dut_->eval();
    dut_->clk = 1;
    dut_->eval();
}

void TcuFiDriver::tick(int cycles) {
    for (int i = 0; i < cycles; ++i) tick();
}

void TcuFiDriver::reset(int cycles) {
    // Hold RST high (active-high on the main pipeline) for the requested number
    // of main clock cycles, then release.  This clears the floating-point
    // pipeline registers inside each dot_unit_core.
    dut_->clk = 0;
    dut_->rst = 1;
    tick(cycles);
    dut_->rst = 0;
}

// =============================================================================
// Matrix load / read (mirrors TcuDriver)
// =============================================================================

void TcuFiDriver::load_A(const mat4f& A) {
    // Each A_iX bus carries one full row of A as four consecutive 32-bit floats.
    pack4(dut_->A_0X, A[0]);
    pack4(dut_->A_1X, A[1]);
    pack4(dut_->A_2X, A[2]);
    pack4(dut_->A_3X, A[3]);
}

void TcuFiDriver::load_B(const mat4f& B) {
    // Each B_iX bus carries one full row of B as four consecutive 32-bit floats.
    pack4(dut_->B_0X, B[0]);
    pack4(dut_->B_1X, B[1]);
    pack4(dut_->B_2X, B[2]);
    pack4(dut_->B_3X, B[3]);
}

void TcuFiDriver::load_C(const mat4f& C) {
    // The hardware dot-unit computes one output element W[row][col] and needs
    // the corresponding accumulator value C[row][col].  Each C_iX bus feeds
    // column i of C to the four dot units in that column.  The matrix must
    // therefore be transposed when packing: C_iX[j] = C[j][i].
    vec4f c0 = {C[0][0], C[1][0], C[2][0], C[3][0]};
    vec4f c1 = {C[0][1], C[1][1], C[2][1], C[3][1]};
    vec4f c2 = {C[0][2], C[1][2], C[2][2], C[3][2]};
    vec4f c3 = {C[0][3], C[1][3], C[2][3], C[3][3]};

    pack4(dut_->C_0X, c0);
    pack4(dut_->C_1X, c1);
    pack4(dut_->C_2X, c2);
    pack4(dut_->C_3X, c3);
}

void TcuFiDriver::load_inputs(const mat4f& A, const mat4f& B, const mat4f& C) {
    load_A(A);
    load_B(B);
    load_C(C);
}

mat4f TcuFiDriver::read_W() const {
    // W_iX3 carries one full row of the result as four floats packed into 128 bits.
    mat4f W{};
    W[0] = unpack4(dut_->W_0X3);
    W[1] = unpack4(dut_->W_1X3);
    W[2] = unpack4(dut_->W_2X3);
    W[3] = unpack4(dut_->W_3X3);
    return W;
}

mat4f TcuFiDriver::run_tile(const mat4f& A, const mat4f& B, const mat4f& C) {
    // Golden path through the FI model: no fault is armed, so any difference
    // from TcuDriver reflects only floating-point rounding differences (if any).
    load_inputs(A, B, C);
    tick(tile_latency_);
    return read_W();
}

// =============================================================================
// SR clock and control helpers
// =============================================================================

void TcuFiDriver::fi_set_ctrl(uint8_t ctrl) {
    // Keep a local shadow so individual bits can be toggled without reading
    // back the DUT port (Verilated ports are write-only from the driver side).
    fi_ctrl_ = ctrl;
    dut_->i_FI_CONTROL_PORT = ctrl;
    dut_->eval();
}

void TcuFiDriver::fi_sr_tick() {
    // The shift register inside fpadd_3_pipe_sbtr is posedge-triggered:
    //   always @(posedge i_CLK)  SR <= {i_SI, SR[WIDTH-1:1]};
    //
    // Drive CLK low first so the next rising edge is clean, then drive high
    // to clock the current i_SI value into the MSB of the SR.  All other
    // i_FI_CONTROL_PORT bits are preserved from fi_ctrl_.
    dut_->i_FI_CONTROL_PORT = fi_ctrl_ & ~FI_CTRL_CLK;  // CLK = 0
    dut_->eval();
    dut_->i_FI_CONTROL_PORT = fi_ctrl_ | FI_CTRL_CLK;   // CLK = 1 → latch i_SI
    dut_->eval();
    // CLK is left high; the next fi_sr_tick() call will bring it low first,
    // ensuring a proper falling→rising edge for the subsequent bit.
}

// =============================================================================
// FI configuration and arming
// =============================================================================

void TcuFiDriver::fi_reset() {
    // RST is active-low on the shift register:
    //   always @(posedge CLK, negedge RST)  if (!RST) SR <= 0;
    //
    // Step 1: assert RST=0 (everything else 0 as well, including TFEn).
    fi_set_ctrl(0);

    // Step 2: pulse the SR clock a few times while reset is asserted to
    // guarantee the register is cleared regardless of its previous state.
    for (int i = 0; i < 4; ++i) fi_sr_tick();

    // Step 3: release RST.  The SR is now all-zeros and ready to be loaded.
    fi_set_ctrl(FI_CTRL_RST);
}

void TcuFiDriver::fi_configure(const FaultConfig& cfg) {
    // Build the flat bitstream from the structured FaultConfig and clock it
    // into the SR one bit at a time.
    const auto bits = build_sr_bitstream(cfg, hw_params_);

    fi_reset();

    // Assert EN=1 so the SR captures i_SI on every rising SR CLK edge.
    // RST remains deasserted (=1) throughout.
    fi_set_ctrl(FI_CTRL_RST | FI_CTRL_EN);

    for (uint8_t b : bits) {
        dut_->i_SI = b;
        dut_->eval();       // set i_SI before the clock edge
        fi_sr_tick();       // rising edge latches the bit into SR[MSB]
    }

    // Deassert EN so the SR is no longer sensitive to i_SI.
    // TFEn remains low — the fault is configured but not yet active.
    dut_->i_SI = 0;
    fi_set_ctrl(FI_CTRL_RST);
}

void TcuFiDriver::fi_arm() {
    // TFEn is the i_en_super_sabouter input of every saboteur.  Setting it
    // high combinationally routes the faulted value to the downstream logic.
    fi_set_ctrl(fi_ctrl_ | FI_CTRL_TFEN);
}

void TcuFiDriver::fi_disarm() {
    fi_set_ctrl(fi_ctrl_ & ~FI_CTRL_TFEN);
}

// =============================================================================
// High-level fault injection tile run
// =============================================================================

mat4f TcuFiDriver::run_tile_fi(const mat4f& A, const mat4f& B, const mat4f& C,
                                const FaultConfig& cfg) {
    // Program the SR before loading the inputs so the configuration is settled
    // when the pipeline starts processing data.
    fi_configure(cfg);
    load_inputs(A, B, C);

    if (cfg.mode == FaultMode::BIT_FLIP) {
        // BIT_FLIP: TFEn is only asserted for one clock cycle.
        // fault_cycle selects which pipeline stage is hit: cycle 1 injects
        // into the earliest stage, cycle tile_latency into the output stage.
        if (cfg.fault_cycle < 1 || cfg.fault_cycle > tile_latency_) {
            throw std::invalid_argument(
                "fault_cycle must be in [1, tile_latency]"
            );
        }

        tick(cfg.fault_cycle - 1);  // let data flow until the target stage
        fi_arm();                   // invert the enabled nodes for one cycle
        tick(1);
        fi_disarm();
        tick(tile_latency_ - cfg.fault_cycle);  // drain the rest of the pipeline

    } else {
        // STUCK_AT: TFEn is held high for the entire tile execution so the
        // forced value propagates through every stage of the pipeline.
        fi_arm();
        tick(tile_latency_);
        fi_disarm();
    }

    return read_W();
}
