module sfu_controller(clk, rst,selop_i, valid_i, start_o, stall_i, data_i, data_o,selop_o);
input clk;
wire clk;
input rst;
wire rst;
input [2:0] selop_i;
wire [2:0] selop_i;
input valid_i;
wire valid_i;
input stall_i;
wire stall_i;
output start_o;
reg start_o;
input [31:0] data_i;
wire [31:0] data_i;
output [31:0] data_o;
reg [31:0] data_o;
output [2:0] selop_o;
reg [2:0] selop_o;


always @(posedge clk or negedge rst) begin
    if (!rst) begin
        start_o <= 1'b0;
        data_o <= 32'b0;
        selop_o <= 3'b0;
    end else begin
        if (valid_i && stall_i) begin
            start_o <= 1'b1;
            data_o <= data_i;
            selop_o <= selop_i;
        end else begin
            start_o <= 1'b0;
        end
    end
end




endmodule