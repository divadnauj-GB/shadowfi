module clock_div(clk, rst, clk_out);
    input clk;
    input rst;
    output reg clk_out;

    parameter DIVISOR = 10; //2; // Change this value to set the division factor

    reg [31:0] counter;

    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            counter <= 0;
            clk_out <= 0;
        end else begin
            if (counter == DIVISOR - 1) begin
                clk_out <= 1;
                counter <= 0;
            end else begin
                clk_out <= 0;
                counter <= counter + 1;
            end
        end
    end

endmodule