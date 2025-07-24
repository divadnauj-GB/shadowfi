module tb_sfu;

  integer returnval;
  reg [128:0] stringi;

  integer fid_input_sin;
  integer fid_input_cos;
  integer fid_input_rsqrt;
  integer fid_input_log2;
  integer fid_input_ex2;
  integer fid_input_rcp;
  integer fid_input_sqrt;

  integer fid_output_sin;
  integer fid_output_cos;
  integer fid_output_rsqrt;
  integer fid_output_log2;
  integer fid_output_ex2;
  integer fid_output_rcp;
  integer fid_output_sqrt;

  reg i_clk;
  reg i_rst;

  reg [31:0] src1_i;
  reg [2:0] selop_i;
  wire [31:0] Result_o;

  reg [31:0] s_sfu_input;
  wire [31:0] s_rro_result;

  wire s_sel_phase;

  assign s_sel_phase = (selop_i == 3'b100) ? 1'b1 : 1'b0;

  always @ (selop_i or src1_i or s_rro_result) begin
    case (selop_i)
       3'b000 : s_sfu_input = s_rro_result;
       3'b001 : s_sfu_input = s_rro_result;
       3'b010 : s_sfu_input = src1_i;
       3'b011 : s_sfu_input = src1_i;
       3'b100 : s_sfu_input = s_rro_result;
       3'b101 : s_sfu_input = src1_i;
       3'b110 : s_sfu_input = src1_i;
       3'b111 : s_sfu_input = src1_i;
    endcase
 end


  rro UUT(.selec_phase(s_sel_phase),
          .\input ( src1_i ),
          .Result(s_rro_result));

  sfu DUT(.src1_i(s_sfu_input), 
          .selop_i(selop_i), 
          .Result_o(Result_o));


  always
  begin
    #10 i_clk = ~i_clk;
  end


  initial
  begin
    $dumpfile("tb_sfu.vcd");
    $dumpvars;
  end


  initial
  begin
    fid_input_sin = $fopen("./SFU_Input_data/input_sin.csv","r");
    fid_input_cos = $fopen("./SFU_Input_data/input_cos.csv","r");
    fid_input_rsqrt = $fopen("./SFU_Input_data/input_rsqrt.csv","r");
    fid_input_log2 = $fopen("./SFU_Input_data/input_log2.csv","r");
    fid_input_ex2 = $fopen("./SFU_Input_data/input_ex2.csv","r");
    fid_input_rcp = $fopen("./SFU_Input_data/input_rcp.csv","r");
    fid_input_sqrt = $fopen("./SFU_Input_data/input_sqrt.csv","r");

    fid_output_sin = $fopen("./output_sin.csv","w");
    fid_output_cos = $fopen("./output_cos.csv","w");
    fid_output_rsqrt = $fopen("./output_rsqrt.csv","w");
    fid_output_log2 = $fopen("./output_log2.csv","w");
    fid_output_ex2 = $fopen("./output_ex2.csv","w");
    fid_output_rcp = $fopen("./output_rcp.csv","w");
    fid_output_sqrt = $fopen("./output_sqrt.csv","w");

    i_clk = 0;
    i_rst = 0;
    #500 i_rst = 1;

    selop_i = 3'b000;
    returnval = $fscanf(fid_input_sin,"%s",stringi);
    $display("stringi = %s",stringi);
    while(!$feof(fid_input_sin))
    begin
      @(negedge i_clk);
      returnval = $fscanf(fid_input_sin,"%h",src1_i);
      $fwrite(fid_output_sin,"%h,%h\n",src1_i,Result_o);
    end

    selop_i = 3'b001;
    returnval = $fscanf(fid_input_cos,"%s",stringi);
    $display("stringi = %s",stringi);
    while(!$feof(fid_input_cos))
    begin
      @(negedge i_clk);
      returnval = $fscanf(fid_input_cos,"%h",src1_i);
      $fwrite(fid_output_cos,"%h,%h\n",src1_i,Result_o);
    end

    selop_i = 3'b010;
    returnval = $fscanf(fid_input_rsqrt,"%s",stringi);
    $display("stringi = %s",stringi);
    while(!$feof(fid_input_rsqrt))
    begin
      @(negedge i_clk);
      returnval = $fscanf(fid_input_rsqrt,"%h",src1_i);
      $fwrite(fid_output_rsqrt,"%h,%h\n",src1_i,Result_o);
    end

    selop_i = 3'b011;
    returnval = $fscanf(fid_input_log2,"%s",stringi);
    $display("stringi = %s",stringi);
    while(!$feof(fid_input_log2))
    begin
      @(negedge i_clk);
      returnval = $fscanf(fid_input_log2,"%h",src1_i);
      $fwrite(fid_output_log2,"%h,%h\n",src1_i,Result_o);
    end

    selop_i = 3'b100;
    returnval = $fscanf(fid_input_ex2,"%s",stringi);
    $display("stringi = %s",stringi);
    while(!$feof(fid_input_ex2))
    begin
      @(negedge i_clk);
      returnval = $fscanf(fid_input_ex2,"%h",src1_i);
      $fwrite(fid_output_ex2,"%h,%h\n",src1_i,Result_o);
    end

    selop_i = 3'b101;
    returnval = $fscanf(fid_input_rcp,"%s",stringi);
    $display("stringi = %s",stringi);
    while(!$feof(fid_input_rcp))
    begin
      @(negedge i_clk);
      returnval = $fscanf(fid_input_rcp,"%h",src1_i);
      $fwrite(fid_output_rcp,"%h,%h\n",src1_i,Result_o);
    end

    selop_i = 3'b110;
    returnval = $fscanf(fid_input_sqrt,"%s",stringi);
    $display("stringi = %s",stringi);
    while(!$feof(fid_input_sqrt))
    begin
      @(negedge i_clk);
      returnval = $fscanf(fid_input_sqrt,"%h",src1_i);
      $fwrite(fid_output_sqrt,"%h,%h\n",src1_i,Result_o);
    end



    $fclose(fid_input_sin);
    $fclose(fid_input_cos);
    $fclose(fid_input_rsqrt);
    $fclose(fid_input_log2);
    $fclose(fid_input_ex2);
    $fclose(fid_input_rcp);
    $fclose(fid_input_sqrt);

    $fclose(fid_output_sin);
    $fclose(fid_output_cos);
    $fclose(fid_output_rsqrt);
    $fclose(fid_output_log2);
    $fclose(fid_output_ex2);
    $fclose(fid_output_rcp);
    $fclose(fid_output_sqrt);
    $finish;
  end

endmodule
