#pragma once

/*
 * tcu_fi_types.hpp
 *
 * Types shared between the FI driver and the Python binding.
 * Defines the fault configuration structure, the hardware parameters
 * needed to program the shift register, and the bitstream builder.
 *
 * Hardware context
 * ----------------
 * The FI-instrumented RTL (sub_tensor_core_fi_sbtr.v) embeds saboteur cells
 * inside the floating-point adder of d_unit0 (adder0 of dot_unit_core_0).
 * Each saboteur targets one internal signal bit and can force it to 0, force
 * it to 1, or invert it.  A chain of shift registers loads per-bit enable
 * vectors and the fault mode into the DUT.  A separate trigger signal (TFEn)
 * activates the saboteurs once the shift register is programmed.
 *
 * i_FI_CONTROL_PORT bit assignment (4-bit bus into the DUT)
 * ---------------------------------------------------------
 *   [0]  EN    — shift register enable: while high, SR captures i_SI on each
 *                rising edge of the SR clock
 *   [1]  TFEn  — trigger fault enable: combinationally activates all enabled
 *                saboteurs while asserted; independent of the SR clock
 *   [2]  RST   — shift register reset, active-low: clears the entire SR when
 *                driven low
 *   [3]  CLK   — shift register clock: independent of the main DUT clock
 */

#include <cstdint>
#include <vector>

// Bit masks for i_FI_CONTROL_PORT (see field description above).
constexpr uint8_t FI_CTRL_EN   = (1u << 0);
constexpr uint8_t FI_CTRL_TFEN = (1u << 1);
constexpr uint8_t FI_CTRL_RST  = (1u << 2);
constexpr uint8_t FI_CTRL_CLK  = (1u << 3);

/*
 * FiHwParams — shift register geometry for one FI-instrumented RTL variant.
 *
 * These values are NOT hardcoded in the driver so that the same driver can be
 * used with RTL variants that instrument different pipeline stages or have a
 * different number of saboteur nodes.
 *
 * SR layout convention (fixed by the saboteur toolchain):
 *
 *   SR[sr_length-1]          ctrl[1]  — MSB of the 2-bit fault mode
 *   SR[sr_length-2]          ctrl[0]  — LSB of the 2-bit fault mode
 *   SR[sr_length-3 : 0]      per-saboteur enables, one bit per node
 *
 * The two ctrl bits together encode the fault mode (see FaultMode below).
 * sr_nodes() and sr_ctrl_offset() derive these values from sr_length so
 * callers only need to supply the single total-length figure.
 */
struct FiHwParams {
    int sr_length;  // total number of bits in the shift register chain

    // Number of independently addressable saboteur nodes (= sr_length - 2).
    int sr_nodes()       const { return sr_length - 2; }

    // Index of the first ctrl bit inside the SR (= sr_length - 2).
    int sr_ctrl_offset() const { return sr_length - 2; }
};

/*
 * FaultMode — operation of each enabled saboteur cell.
 *
 * The 2-bit value maps directly to the ctrl[1:0] field stored in the top two
 * bits of the shift register:
 *
 *   STUCK_AT_0 (0b00) : output = 0           regardless of the natural value
 *   STUCK_AT_1 (0b01) : output = 1           regardless of the natural value
 *   BIT_FLIP   (0b10) : output = ~input      one transient inversion
 *
 * For STUCK_AT faults TFEn stays high for the entire tile execution.
 * For BIT_FLIP TFEn is pulsed high for exactly one clock cycle (fault_cycle).
 */
enum class FaultMode : uint8_t {
    STUCK_AT_0 = 0b00,
    STUCK_AT_1 = 0b01,
    BIT_FLIP   = 0b10,
};

/*
 * FaultConfig — complete specification of one fault injection experiment.
 *
 * target_nodes  Indices of the saboteur nodes to arm (0 .. FiHwParams::sr_nodes()-1).
 *               Each index corresponds to one internal signal bit in the
 *               instrumented adder.  An empty list means no fault is injected
 *               (useful to verify the FI model matches the golden model).
 *
 * fault_cycle   Only used for BIT_FLIP: the tile pipeline cycle [1, tile_latency]
 *               at which TFEn is asserted for one clock.  Earlier cycles
 *               affect earlier pipeline stages; later cycles affect the output
 *               register.  Ignored for STUCK_AT faults.
 */
struct FaultConfig {
    FaultMode        mode         = FaultMode::STUCK_AT_0;
    std::vector<int> target_nodes;
    int              fault_cycle  = 6;
};

/*
 * build_sr_bitstream — encode a FaultConfig into the serial bitstream for the SR.
 *
 * The shift register shifts right on every rising SR clock edge:
 *
 *   SR <= {i_SI, SR[sr_length-1 : 1]}
 *
 * This means the FIRST bit shifted in lands at SR[0], the LAST bit shifted in
 * lands at SR[sr_length-1].  Given the SR layout, the loading order must be:
 *
 *   1st  bit → SR[0]              enable for saboteur node 0
 *   2nd  bit → SR[1]              enable for saboteur node 1
 *   ...
 *   Nth  bit → SR[sr_nodes-1]     enable for saboteur node sr_nodes-1
 *   N+1  bit → SR[sr_length-2]    ctrl[0]  (FaultMode LSB)
 *   N+2  bit → SR[sr_length-1]    ctrl[1]  (FaultMode MSB)
 *
 * Returns a vector of sr_length bits in the order they must be clocked in.
 */
std::vector<uint8_t> build_sr_bitstream(const FaultConfig& cfg, const FiHwParams& params);
