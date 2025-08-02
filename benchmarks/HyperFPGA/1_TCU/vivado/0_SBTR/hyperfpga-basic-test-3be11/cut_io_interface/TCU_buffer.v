
module TCU_buffer (clk, rst, valid_data, TCU_ABC_input, TCU_D_output, TCU_enable, result_valid,
    TC0_A_0X, TC0_A_1X, TC0_A_2X, TC0_A_3X,
    TC0_B_0X, TC0_B_1X, TC0_B_2X, TC0_B_3X,
    TC0_C_0X, TC0_C_1X, TC0_C_2X, TC0_C_3X,
    TC0_W_0X3, TC0_W_1X3, TC0_W_2X3, TC0_W_3X3, 
    TC1_A_0X, TC1_A_1X, TC1_A_2X, TC1_A_3X,
    TC1_B_0X, TC1_B_1X, TC1_B_2X, TC1_B_3X,
    TC1_C_0X, TC1_C_1X, TC1_C_2X, TC1_C_3X,
    TC1_W_0X3, TC1_W_1X3, TC1_W_2X3, TC1_W_3X3
);
    input clk;
    wire clk;
    input rst;
    wire rst;
    input valid_data;
    wire valid_data;
    input [31:0] TCU_ABC_input;
    wire [31:0] TCU_ABC_input;

    output [31:0] TCU_D_output;
    wire [31:0] TCU_D_output;


    
    output [127:0] TC0_A_0X;
    wire [127:0] TC0_A_0X;
    output [127:0] TC0_A_1X;
    wire [127:0] TC0_A_1X;
    output [127:0] TC0_A_2X;
    wire [127:0] TC0_A_2X;
    output [127:0] TC0_A_3X;
    wire [127:0] TC0_A_3X;

    output [127:0] TC0_B_0X;
    wire [127:0] TC0_B_0X;
    output [127:0] TC0_B_1X;
    wire [127:0] TC0_B_1X;
    output [127:0] TC0_B_2X;
    wire [127:0] TC0_B_2X;
    output [127:0] TC0_B_3X;
    wire [127:0] TC0_B_3X;

    output [127:0] TC0_C_0X;
    wire [127:0] TC0_C_0X;
    output [127:0] TC0_C_1X;
    wire [127:0] TC0_C_1X;
    output [127:0] TC0_C_2X;
    wire [127:0] TC0_C_2X;
    output [127:0] TC0_C_3X;
    wire [127:0] TC0_C_3X;

    output [127:0] TC1_A_0X;
    wire [127:0] TC1_A_0X;
    output [127:0] TC1_A_1X;
    wire [127:0] TC1_A_1X;
    output [127:0] TC1_A_2X;
    wire [127:0] TC1_A_2X;
    output [127:0] TC1_A_3X;
    wire [127:0] TC1_A_3X;

    output [127:0] TC1_B_0X;
    wire [127:0] TC1_B_0X;
    output [127:0] TC1_B_1X;
    wire [127:0] TC1_B_1X;
    output [127:0] TC1_B_2X;
    wire [127:0] TC1_B_2X;
    output [127:0] TC1_B_3X;
    wire [127:0] TC1_B_3X;

    output [127:0] TC1_C_0X;
    wire [127:0] TC1_C_0X;
    output [127:0] TC1_C_1X;
    wire [127:0] TC1_C_1X;
    output [127:0] TC1_C_2X;
    wire [127:0] TC1_C_2X;
    output [127:0] TC1_C_3X;
    wire [127:0] TC1_C_3X;

    input [127:0] TC0_W_0X3;
    wire [127:0] TC0_W_0X3;
    input [127:0] TC0_W_1X3;
    wire [127:0] TC0_W_1X3;
    input [127:0] TC0_W_2X3;
    wire [127:0] TC0_W_2X3;
    input [127:0] TC0_W_3X3;
    wire [127:0] TC0_W_3X3;

    input [127:0] TC1_W_0X3;
    wire [127:0] TC1_W_0X3;
    input [127:0] TC1_W_1X3;
    wire [127:0] TC1_W_1X3;
    input [127:0] TC1_W_2X3;
    wire [127:0] TC1_W_2X3;
    input [127:0] TC1_W_3X3;
    wire [127:0] TC1_W_3X3;

    output TCU_enable;
    reg TCU_enable;

    input result_valid;
    wire result_valid;

    // Buffer to hold the data
    reg [31:0] input_buffer [0:95];
    reg [31:0] output_buffer [0:31];

    reg [4:0] index_out; 

    integer shift_in_cnt; 


    integer jj;
    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            for (jj = 0; jj < (96); jj = jj + 1) begin
                input_buffer[jj] <= 0;
            end
        end else if(valid_data) begin
            input_buffer[0] <= TCU_ABC_input;
            for (jj = 1; jj < (96); jj = jj + 1) begin
                input_buffer[jj] <= input_buffer[jj-1];
            end
        end
    end

    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            shift_in_cnt <= 0;
        end else if (valid_data) begin
            if (shift_in_cnt == 95) begin
                TCU_enable <= 1;
                shift_in_cnt <= 0;
            end else begin
                TCU_enable <= 0;
                shift_in_cnt <= shift_in_cnt + 1;
            end 
        end
    end



    assign TC0_A_0X[31:0] = input_buffer[0];
    assign TC0_A_0X[63:32] = input_buffer[1];
    assign TC0_A_0X[95:64] = input_buffer[2];
    assign TC0_A_0X[127:96] = input_buffer[3];
    assign TC0_A_1X[31:0] = input_buffer[4];
    assign TC0_A_1X[63:32] = input_buffer[5];
    assign TC0_A_1X[95:64] = input_buffer[6];
    assign TC0_A_1X[127:96] = input_buffer[7];
    assign TC0_A_2X[31:0] = input_buffer[8];
    assign TC0_A_2X[63:32] = input_buffer[9];
    assign TC0_A_2X[95:64] = input_buffer[10];
    assign TC0_A_2X[127:96] = input_buffer[11];
    assign TC0_A_3X[31:0] = input_buffer[12];
    assign TC0_A_3X[63:32] = input_buffer[13];
    assign TC0_A_3X[95:64] = input_buffer[14];
    assign TC0_A_3X[127:96] = input_buffer[15];
    assign TC0_B_0X[31:0] = input_buffer[16];
    assign TC0_B_0X[63:32] = input_buffer[17];
    assign TC0_B_0X[95:64] = input_buffer[18];
    assign TC0_B_0X[127:96] = input_buffer[19];
    assign TC0_B_1X[31:0] = input_buffer[20];
    assign TC0_B_1X[63:32] = input_buffer[21];
    assign TC0_B_1X[95:64] = input_buffer[22];
    assign TC0_B_1X[127:96] = input_buffer[23];
    assign TC0_B_2X[31:0] = input_buffer[24];
    assign TC0_B_2X[63:32] = input_buffer[25];
    assign TC0_B_2X[95:64] = input_buffer[26];
    assign TC0_B_2X[127:96] = input_buffer[27];
    assign TC0_B_3X[31:0] = input_buffer[28];
    assign TC0_B_3X[63:32] = input_buffer[29];
    assign TC0_B_3X[95:64] = input_buffer[30];
    assign TC0_B_3X[127:96] = input_buffer[31];
    assign TC0_C_0X[31:0] = input_buffer[32];
    assign TC0_C_0X[63:32] = input_buffer[33];
    assign TC0_C_0X[95:64] = input_buffer[34];
    assign TC0_C_0X[127:96] = input_buffer[35];
    assign TC0_C_1X[31:0] = input_buffer[36];
    assign TC0_C_1X[63:32] = input_buffer[37];
    assign TC0_C_1X[95:64] = input_buffer[38];
    assign TC0_C_1X[127:96] = input_buffer[39];
    assign TC0_C_2X[31:0] = input_buffer[40];
    assign TC0_C_2X[63:32] = input_buffer[41];
    assign TC0_C_2X[95:64] = input_buffer[42];
    assign TC0_C_2X[127:96] = input_buffer[43];
    assign TC0_C_3X[31:0] = input_buffer[44];
    assign TC0_C_3X[63:32] = input_buffer[45];
    assign TC0_C_3X[95:64] = input_buffer[46];
    assign TC0_C_3X[127:96] = input_buffer[47];
    assign TC1_A_0X[31:0] = input_buffer[48];
    assign TC1_A_0X[63:32] = input_buffer[49];
    assign TC1_A_0X[95:64] = input_buffer[50];
    assign TC1_A_0X[127:96] = input_buffer[51];
    assign TC1_A_1X[31:0] = input_buffer[52];
    assign TC1_A_1X[63:32] = input_buffer[53];
    assign TC1_A_1X[95:64] = input_buffer[54];
    assign TC1_A_1X[127:96] = input_buffer[55];
    assign TC1_A_2X[31:0] = input_buffer[56];
    assign TC1_A_2X[63:32] = input_buffer[57];
    assign TC1_A_2X[95:64] = input_buffer[58];
    assign TC1_A_2X[127:96] = input_buffer[59]; 
    assign TC1_A_3X[31:0] = input_buffer[60];
    assign TC1_A_3X[63:32] = input_buffer[61];
    assign TC1_A_3X[95:64] = input_buffer[62];
    assign TC1_A_3X[127:96] = input_buffer[63];
    assign TC1_B_0X[31:0] = input_buffer[64];
    assign TC1_B_0X[63:32] = input_buffer[65];
    assign TC1_B_0X[95:64] = input_buffer[66];
    assign TC1_B_0X[127:96] = input_buffer[67];
    assign TC1_B_1X[31:0] = input_buffer[68];
    assign TC1_B_1X[63:32] = input_buffer[69];
    assign TC1_B_1X[95:64] = input_buffer[70];
    assign TC1_B_1X[127:96] = input_buffer[71];
    assign TC1_B_2X[31:0] = input_buffer[72];
    assign TC1_B_2X[63:32] = input_buffer[73];
    assign TC1_B_2X[95:64] = input_buffer[74];
    assign TC1_B_2X[127:96] = input_buffer[75];
    assign TC1_B_3X[31:0] = input_buffer[76];
    assign TC1_B_3X[63:32] = input_buffer[77];
    assign TC1_B_3X[95:64] = input_buffer[78];
    assign TC1_B_3X[127:96] = input_buffer[79];
    assign TC1_C_0X[31:0] = input_buffer[80];
    assign TC1_C_0X[63:32] = input_buffer[81];
    assign TC1_C_0X[95:64] = input_buffer[82];
    assign TC1_C_0X[127:96] = input_buffer[83];
    assign TC1_C_1X[31:0] = input_buffer[84];
    assign TC1_C_1X[63:32] = input_buffer[85];
    assign TC1_C_1X[95:64] = input_buffer[86];
    assign TC1_C_1X[127:96] = input_buffer[87];
    assign TC1_C_2X[31:0] = input_buffer[88];
    assign TC1_C_2X[63:32] = input_buffer[89];
    assign TC1_C_2X[95:64] = input_buffer[90];
    assign TC1_C_2X[127:96] = input_buffer[91];
    assign TC1_C_3X[31:0] = input_buffer[92];
    assign TC1_C_3X[63:32] = input_buffer[93];
    assign TC1_C_3X[95:64] = input_buffer[94];
    assign TC1_C_3X[127:96] = input_buffer[95];


    integer ii;
    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            for (ii = 0; ii < (32); ii = ii + 1) begin
                output_buffer[ii] <= 0;
            end
        end else begin
            output_buffer[0] <= TC0_W_0X3[31:0];
            output_buffer[1] <= TC0_W_0X3[63:32];
            output_buffer[2] <= TC0_W_0X3[95:64]; 
            output_buffer[3] <= TC0_W_0X3[127:96];
            output_buffer[4] <= TC0_W_1X3[31:0];
            output_buffer[5] <= TC0_W_1X3[63:32];
            output_buffer[6] <= TC0_W_1X3[95:64];
            output_buffer[7] <= TC0_W_1X3[127:96];
            output_buffer[8] <= TC0_W_2X3[31:0];
            output_buffer[9] <= TC0_W_2X3[63:32];
            output_buffer[10] <= TC0_W_2X3[95:64];
            output_buffer[11] <= TC0_W_2X3[127:96];
            output_buffer[12] <= TC0_W_3X3[31:0];
            output_buffer[13] <= TC0_W_3X3[63:32];
            output_buffer[14] <= TC0_W_3X3[95:64];
            output_buffer[15] <= TC0_W_3X3[127:96];
            output_buffer[16] <= TC1_W_0X3[31:0];
            output_buffer[17] <= TC1_W_0X3[63:32];
            output_buffer[18] <= TC1_W_0X3[95:64];
            output_buffer[19] <= TC1_W_0X3[127:96];
            output_buffer[20] <= TC1_W_1X3[31:0];
            output_buffer[21] <= TC1_W_1X3[63:32];
            output_buffer[22] <= TC1_W_1X3[95:64];
            output_buffer[23] <= TC1_W_1X3[127:96];
            output_buffer[24] <= TC1_W_2X3[31:0];
            output_buffer[25] <= TC1_W_2X3[63:32];
            output_buffer[26] <= TC1_W_2X3[95:64];
            output_buffer[27] <= TC1_W_2X3[127:96];
            output_buffer[28] <= TC1_W_3X3[31:0];
            output_buffer[29] <= TC1_W_3X3[63:32];
            output_buffer[30] <= TC1_W_3X3[95:64];
            output_buffer[31] <= TC1_W_3X3[127:96];
        end
    end


    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            index_out <= 0;
        end else if (result_valid) begin
            index_out <= index_out + 1;
        end
    end

    assign TCU_D_output[31:0] = output_buffer[index_out];

endmodule
