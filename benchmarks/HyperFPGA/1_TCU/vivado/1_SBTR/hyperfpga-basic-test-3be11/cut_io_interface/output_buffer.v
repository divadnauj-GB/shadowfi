module output_buffer(clk,rst,load,shift,input_data, output_data);
    parameter DATA_WIDTH = 32;
    parameter DEPTH = 16;
    
    input clk;
    input rst;
    input load;
    input shift;
    input [DEPTH*DATA_WIDTH-1:0] input_data;
    output [DATA_WIDTH-1:0] output_data;
    
    reg [DATA_WIDTH-1:0] buffer [0:DEPTH-1];
    
    generate
        genvar idx;
        for (idx = 0; idx < DEPTH; idx = idx + 1) begin : load_buffer
            always @(posedge clk or negedge rst) begin
                if (!rst) begin
                    buffer[idx] <= 0;
                end else if (load) begin
                        buffer[idx] <= input_data[idx*DATA_WIDTH+DATA_WIDTH-1:idx*DATA_WIDTH];
                end else if (shift) begin
                    if(idx<DEPTH-1) begin
                        buffer[idx] <= buffer[idx+1];
                    end else begin
                        buffer[idx] <= {DATA_WIDTH{1'b0}};
                    end
                end
            end
        end
    endgenerate

    assign output_data = buffer[0];

endmodule