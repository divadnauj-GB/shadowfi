module input_buffer(clk, rst, enable, data_in, data_out);
  parameter DATA_WIDTH = 32;
  parameter DEPTH = 48;
  
  input clk;
  input rst;
  input enable;
  input [DATA_WIDTH-1:0] data_in;
  output [DEPTH*DATA_WIDTH-1:0] data_out;

  reg [DATA_WIDTH-1:0] buffer [0:DEPTH-1];

  integer i;
  always @(posedge clk or negedge rst) begin
    if (!rst) begin
        for (i = 0; i < DEPTH; i = i + 1) begin
          buffer[i] <= 0;
        end
    end else if (enable) begin
        for (i = 0; i < DEPTH-1; i = i + 1) begin
          buffer[i] <= buffer[i+1];
        end
        buffer[DEPTH-1] <= data_in;
    end
  end


  generate
    genvar idx;
    for (idx = 0; idx < DEPTH; idx = idx + 1) begin : load_buffer
        assign data_out[idx*DATA_WIDTH+DATA_WIDTH-1:idx*DATA_WIDTH] = buffer[idx];
    end
  endgenerate



endmodule


module pipe_1_register(clk, rst, enable, data_in, data_out);
  parameter DATA_WIDTH = 32;
  parameter DEPTH = 48;
  
  input clk;
  input rst;
  input enable;
  input [DEPTH*DATA_WIDTH-1:0] data_in;
  output [DEPTH*DATA_WIDTH-1:0] data_out;

  reg [DEPTH*DATA_WIDTH-1:0] buffer ;

  always @(posedge clk or negedge rst) begin
    if (!rst) begin
        buffer <= 0;
    end else if (enable) begin
        buffer <= data_in;
    end
  end

  assign data_out = buffer;


endmodule