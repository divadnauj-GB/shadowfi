module tb_tcu;

  integer returnval;
  reg [128:0] stringi;

  integer fid_input_data;

  integer fid_output_data;

  reg i_clk;
  reg i_rst;
  reg s_start_i;
  wire s_underflow_o;
  wire s_overflow_o;


  reg [127:0] s_TC0_A_0X ;
  reg [127:0] s_TC0_A_1X ;
  reg [127:0] s_TC0_A_2X ;
  reg [127:0] s_TC0_A_3X ;
  reg [127:0] s_TC1_A_0X ;
  reg [127:0] s_TC1_A_1X ;
  reg [127:0] s_TC1_A_2X ;
  reg [127:0] s_TC1_A_3X ;
  reg [127:0] s_TC0_B_0X ;
  reg [127:0] s_TC0_B_1X ;
  reg [127:0] s_TC0_B_2X ;
  reg [127:0] s_TC0_B_3X ;
  reg [127:0] s_TC1_B_0X ;
  reg [127:0] s_TC1_B_1X ;
  reg [127:0] s_TC1_B_2X ;
  reg [127:0] s_TC1_B_3X ;
  reg [127:0] s_TC0_C_0X ;
  reg [127:0] s_TC0_C_1X ;
  reg [127:0] s_TC0_C_2X ;
  reg [127:0] s_TC0_C_3X ;
  reg [127:0] s_TC1_C_0X ;
  reg [127:0] s_TC1_C_1X ;
  reg [127:0] s_TC1_C_2X ;
  reg [127:0] s_TC1_C_3X ;

  wire [127:0] s_TC0_W_0X3 ;
  wire [127:0] s_TC0_W_1X3 ;
  wire [127:0] s_TC0_W_2X3 ;
  wire [127:0] s_TC0_W_3X3 ;
  wire [127:0] s_TC1_W_0X3 ;
  wire [127:0] s_TC1_W_1X3 ;
  wire [127:0] s_TC1_W_2X3 ;
  wire [127:0] s_TC1_W_3X3 ;


  reg [31:0] A0;
  reg [31:0] A1;
  reg [31:0] A2;
  reg [31:0] A3;
  reg [31:0] B0;
  reg [31:0] B1;
  reg [31:0] B2;
  reg [31:0] B3;
  reg [31:0] C0;
  reg [31:0] D0;

  sub_tensor_core DUT(.clk(i_clk),
               .rst(i_rst),
               .A_0X(s_TC0_A_0X),
               .A_1X(s_TC0_A_1X),
               .A_2X(s_TC0_A_2X),
               .A_3X(s_TC0_A_3X),
               .B_0X(s_TC0_B_0X),
               .B_1X(s_TC0_B_1X),
               .B_2X(s_TC0_B_2X),
               .B_3X(s_TC0_B_3X),
               .C_0X(s_TC0_C_0X),
               .C_1X(s_TC0_C_1X),
               .C_2X(s_TC0_C_2X),
               .C_3X(s_TC0_C_3X),
               .W_0X3(s_TC0_W_0X3),
               .W_1X3(s_TC0_W_1X3),
               .W_2X3(s_TC0_W_2X3),
               .W_3X3(s_TC0_W_3X3));



  always
  begin
    #10 i_clk = ~i_clk;
  end


  initial
  begin
    $dumpfile("tb_tcu.vcd");
    $dumpvars;
  end


  initial
  begin
    fid_input_data = $fopen("./values_dot_product.csv","r");

    fid_output_data = $fopen("./output_dot_product.csv","w");

    i_clk = 0;
    i_rst = 1;
    #500 i_rst = 0;

    while(!$feof(fid_input_data))
    begin
      returnval = $fscanf(fid_input_data,"%h,%h,%h,%h,%h,%h,%h,%h,%h,%h",A0,A1,A2,A3,B0,B1,B2,B3,C0,D0);
      s_TC0_A_0X = {A3,A2,A1,A0};
      s_TC0_A_1X = {A3,A2,A1,A0};
      s_TC0_A_2X = {A3,A2,A1,A0};
      s_TC0_A_3X = {A3,A2,A1,A0};

      s_TC0_B_0X = {B0,B0,B0,B0};
      s_TC0_B_1X = {B1,B1,B1,B1};
      s_TC0_B_2X = {B2,B2,B2,B2};
      s_TC0_B_3X = {B3,B3,B3,B3};

      s_TC0_C_0X = {C0,C0,C0,C0};
      s_TC0_C_1X = {C0,C0,C0,C0};
      s_TC0_C_2X = {C0,C0,C0,C0};
      s_TC0_C_3X = {C0,C0,C0,C0};
      
      repeat (12) @(negedge i_clk);

      $fwrite(fid_output_data,"%h,%h,%h,%h,",s_TC0_W_0X3[127:96],s_TC0_W_0X3[95:64],s_TC0_W_0X3[63:32],s_TC0_W_0X3[31:0]);
      $fwrite(fid_output_data,"%h,%h,%h,%h,",s_TC0_W_1X3[127:96],s_TC0_W_1X3[95:64],s_TC0_W_1X3[63:32],s_TC0_W_1X3[31:0]);
      $fwrite(fid_output_data,"%h,%h,%h,%h,",s_TC0_W_2X3[127:96],s_TC0_W_2X3[95:64],s_TC0_W_2X3[63:32],s_TC0_W_2X3[31:0]);
      $fwrite(fid_output_data,"%h,%h,%h,%h\n",s_TC0_W_3X3[127:96],s_TC0_W_3X3[95:64],s_TC0_W_3X3[63:32],s_TC0_W_3X3[31:0]);

      $fwrite(fid_output_data,"%h,%h,%h,%h,",D0,D0,D0,D0);
      $fwrite(fid_output_data,"%h,%h,%h,%h,",D0,D0,D0,D0);
      $fwrite(fid_output_data,"%h,%h,%h,%h,",D0,D0,D0,D0);
      $fwrite(fid_output_data,"%h,%h,%h,%h\n",D0,D0,D0,D0);
    end


    $fclose(fid_input_data);
    $fclose(fid_output_data);
    $finish;
  end

endmodule
