#include "tcu_fi_types.hpp"

#include <stdexcept>

/*
 * build_sr_bitstream
 *
 * Translates a FaultConfig into the ordered bit sequence that must be clocked
 * into the shift register one bit at a time via i_SI.
 *
 * SR shift direction (from shift_register.v):
 *
 *   always @(posedge CLK)
 *       SR <= {i_SI, SR[WIDTH-1 : 1]};   // right-shift; new bit enters MSB
 *
 * After sr_length clock cycles the mapping from shift order to SR position is:
 *
 *   1st clocked bit → SR[0]               (first in, lowest index)
 *   2nd clocked bit → SR[1]
 *   ...
 *   sr_length-th clocked bit → SR[sr_length-1]   (last in, highest index)
 *
 * Given the SR layout in FiHwParams, the required sequence is:
 *
 *   bits[0 .. sr_nodes-1]   : enable for saboteurs 0 .. sr_nodes-1
 *   bits[sr_length-2]       : ctrl[0] — FaultMode LSB
 *   bits[sr_length-1]       : ctrl[1] — FaultMode MSB
 */
std::vector<uint8_t> build_sr_bitstream(const FaultConfig& cfg, const FiHwParams& params) {
    std::vector<uint8_t> bits(params.sr_length, 0);

    // Enable the requested saboteur nodes.
    const int max_node = params.sr_nodes() - 1;
    for (int node : cfg.target_nodes) {
        if (node < 0 || node > max_node) {
            throw std::out_of_range(
                "FaultConfig target_node " + std::to_string(node) +
                " out of range [0, " + std::to_string(max_node) + "]"
            );
        }
        bits[node] = 1;
    }

    // Write the 2-bit fault mode into the top two positions of the bitstream.
    // These become SR[sr_length-2] (ctrl[0]) and SR[sr_length-1] (ctrl[1]).
    const int ctrl_off = params.sr_ctrl_offset();
    const auto mode    = static_cast<uint8_t>(cfg.mode);
    bits[ctrl_off]     = (mode >> 0) & 1u;  // ctrl[0]  (LSB of FaultMode)
    bits[ctrl_off + 1] = (mode >> 1) & 1u;  // ctrl[1]  (MSB of FaultMode)

    return bits;
}
