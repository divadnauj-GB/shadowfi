module phase_select(selop_i, selec_phase_o);

input [2:0] selop_i;
wire [2:0] selop_i;
output selec_phase_o;
wire selec_phase_o;

assign selec_phase_o = (selop_i == 3'b100) ? 1'b1 : 1'b0;

endmodule