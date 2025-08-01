module sfu_input_sel ( selop_i, rro_input, src_i, sfu_input );
    

input [2:0]  selop_i;
input [31:0] rro_input;
input [31:0] src_i;
output [31:0] sfu_input;
wire [2:0]  selop_i;
wire [31:0] rro_input;
wire [31:0] src_i;
reg [31:0] sfu_input;

always @(*) begin
    case (selop_i)
       3'b000 : sfu_input = rro_input;
       3'b001 : sfu_input = rro_input;
       3'b010 : sfu_input = src_i;
       3'b011 : sfu_input = src_i;
       3'b100 : sfu_input = rro_input;
       3'b101 : sfu_input = src_i;
       3'b110 : sfu_input = src_i;
       3'b111 : sfu_input = src_i;
    endcase
end

endmodule