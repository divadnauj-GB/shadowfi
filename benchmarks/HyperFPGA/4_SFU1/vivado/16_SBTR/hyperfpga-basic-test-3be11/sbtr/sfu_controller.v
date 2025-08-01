module sfu_controller(clk,rst,clk2,clk3,stall,validi,selop,re_i, start, we);

input clk;
input rst;
input clk2;
input clk3;
input stall;
input validi;
input [2:0] selop;
output re_i;
output start;
output we;

reg start;

reg en_ff;
reg en_ff2;
wire we;

wire we_wire;
wire rd_en1;
wire re_i;
wire clk;
wire rst;
wire clk2;
wire clk3;
wire stall;
wire validi;
wire [2:0] selop;

reg rd_en_flop;


always @(posedge clk or negedge rst) begin
    if (!rst) begin
        rd_en_flop <= 1'b0;
    end else begin
        rd_en_flop <= re_i;
    end
end


always @(posedge clk or negedge rst) begin
    if (!rst) begin
        en_ff <= 1'b0;
    end else begin
        if((selop == 3'b000) || (selop == 3'b001)) begin
            if (rd_en_flop==1'b1) begin
                en_ff <= validi;
            end
        end
    end
end


always @(posedge clk or negedge rst) begin
    if (!rst) begin
        en_ff2 <= 1'b0;
    end else begin
       if((en_ff == 1'b1) && (clk2 == 1'b1)) begin
            en_ff2 <= (~stall);
        end
    end
end

assign we_wire = clk2 & en_ff2;
assign rd_en1 = (en_ff == 1'b1) ? we_wire : clk2;

always @(posedge clk or negedge rst) begin
    if (!rst) begin
        start <= 1'b0;
    end else begin
        if(clk3 == 1'b1) begin
            start <= validi;
        end
    end
end
//assign we = (selop == 3'b000 || selop == 3'b001) ? we_wire : (start & clk3);
assign we = (selop == 3'b000) ? we_wire : (selop == 3'b001) ? we_wire : (start & clk3);

assign re_i = (selop == 3'b000) ? rd_en1 : (selop == 3'b001) ? rd_en1: clk2;
//assign re_i = (selop == 3'b000 || selop == 3'b001) ? rd_en1 : clk2;


endmodule