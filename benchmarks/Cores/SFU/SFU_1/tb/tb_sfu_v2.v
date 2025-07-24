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
  reg s_start_i;
  wire s_stall_o;
  reg [31:0] src1_i;
  reg [2:0] selop_i;
  wire [31:0] Result_o;

  reg [31:0] s_sfu_input;
  wire [31:0] s_rro_result;

  reg clk2;
  reg clk3;

  integer counter;
  integer counter2;

  wire re_i;
  wire we_i;
  reg valid_i;

  always @(posedge i_clk or negedge i_rst)
  begin
    if (!i_rst) begin
      clk2 <= 1'b0;
      counter <= 0;
    end else begin
      if (counter == 10) begin
        counter <= 0;
        clk2 <= 1'b1;
      end else begin
        counter <= counter + 1;
        clk2 <= 1'b0;
      end
    end
  end

  always @(posedge i_clk or negedge i_rst)
  begin
    if (!i_rst) begin
      clk3 <= 1'b0;
    end else begin
      clk3 <= clk2;
    end
  end


  
  always @(posedge i_clk or negedge i_rst)
  begin
    if (!i_rst) begin
      valid_i <= 1'b0;
    end else begin
      if (counter2 < 100) begin        
        valid_i <= 1'b0;
      end else if ((counter2 >= 500)&&(counter2<600)) begin
        valid_i <= 1'b0;
      end else begin
        valid_i <= re_i;
      end
      counter2 <= counter2 + 1;
    end
  end


  sfu_controller sfu_controller(
          .clk(i_clk), 
          .rst(i_rst), 
          .clk2(clk2), 
          .clk3(clk3), 
          .stall(s_stall_o), 
          .validi(valid_i), 
          .selop(selop_i), 
          .re_i(re_i), 
          .start(s_start_i), 
          .we(we_i));

  sfu DUT(
          .clk_i(clk2), 
          .rst_n(i_rst), 
          .start_i(s_start_i),
          .src1_i(src1_i), 
          .selop_i(selop_i), 
          .Result_o(Result_o), 
          .stall_o(s_stall_o));

          

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
    fid_input_sin = $fopen("./SFU_input_data/input_cordic.csv","r");
    fid_input_cos = $fopen("./SFU_input_data/input_cordic.csv","r");
    fid_input_rsqrt = $fopen("./SFU_input_data/input_rsqrt.csv","r");
    fid_input_log2 = $fopen("./SFU_input_data/input_log2.csv","r");
    fid_input_ex2 = $fopen("./SFU_input_data/input_ex2.csv","r");

    fid_output_sin = $fopen("./output_sin.csv","w");
    fid_output_cos = $fopen("./output_cos.csv","w");
    fid_output_rsqrt = $fopen("./output_rsqrt.csv","w");
    fid_output_log2 = $fopen("./output_log2.csv","w");
    fid_output_ex2 = $fopen("./output_ex2.csv","w");

    i_clk = 0;
    i_rst = 0;
    #500 i_rst = 1;

    selop_i = 3'b000;
    returnval = $fscanf(fid_input_sin,"%s",stringi);
    $display("stringi = %s",stringi);
    while(!$feof(fid_input_sin))
    begin
      returnval = $fscanf(fid_input_sin,"%h",src1_i);
      @(negedge i_clk);      
      //s_start_i = 1;
      //@(negedge i_clk);
      //s_start_i = 0;
      @(negedge i_clk iff re_i==1'b1);
      $fwrite(fid_output_sin,"%h,%h\n",src1_i,Result_o);
    end
    /*
    selop_i = 3'b001;
    returnval = $fscanf(fid_input_cos,"%s",stringi);
    $display("stringi = %s",stringi);
    while(!$feof(fid_input_cos))
    begin
      @(negedge i_clk);
      returnval = $fscanf(fid_input_cos,"%h",src1_i);
      s_start_i = 1;
      @(negedge i_clk);
      s_start_i = 0;
      @(negedge i_clk iff s_stall_o==0);
      $fwrite(fid_output_cos,"%h,%h\n",src1_i,Result_o);
    end

    selop_i = 3'b010;
    returnval = $fscanf(fid_input_rsqrt,"%s",stringi);
    $display("stringi = %s",stringi);
    while(!$feof(fid_input_rsqrt))
    begin
      @(negedge i_clk);
      returnval = $fscanf(fid_input_rsqrt,"%h",src1_i);
      s_start_i = 1;
      @(negedge i_clk);
      s_start_i = 0;
      $fwrite(fid_output_rsqrt,"%h,%h\n",src1_i,Result_o);
    end

    selop_i = 3'b011;
    returnval = $fscanf(fid_input_log2,"%s",stringi);
    $display("stringi = %s",stringi);
    while(!$feof(fid_input_log2))
    begin
      @(negedge i_clk);
      returnval = $fscanf(fid_input_log2,"%h",src1_i);
      s_start_i = 1;
      @(negedge i_clk);
      s_start_i = 0;
      $fwrite(fid_output_log2,"%h,%h\n",src1_i,Result_o);
    end

    selop_i = 3'b100;
    returnval = $fscanf(fid_input_ex2,"%s",stringi);
    $display("stringi = %s",stringi);
    while(!$feof(fid_input_ex2))
    begin
      @(negedge i_clk);
      returnval = $fscanf(fid_input_ex2,"%h",src1_i);
      s_start_i = 1;
      @(negedge i_clk);
      s_start_i = 0;
      $fwrite(fid_output_ex2,"%h,%h\n",src1_i,Result_o);
    end
    */


    $fclose(fid_input_sin);
    $fclose(fid_input_cos);
    $fclose(fid_input_rsqrt);
    $fclose(fid_input_log2);
    $fclose(fid_input_ex2);

    $fclose(fid_output_sin);
    $fclose(fid_output_cos);
    $fclose(fid_output_rsqrt);
    $fclose(fid_output_log2);
    $fclose(fid_output_ex2);
    $finish;
  end

endmodule
