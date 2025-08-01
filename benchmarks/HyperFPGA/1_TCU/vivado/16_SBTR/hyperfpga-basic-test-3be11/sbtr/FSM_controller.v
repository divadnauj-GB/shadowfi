module FSM_controller(clk,rst,val_input, clk2, re_i, we, load_input, load_result);

    input clk;
    input rst;
    input val_input;
    output clk2;
    output reg re_i;
    output reg we;
    output reg load_input;
    output reg load_result;

    parameter DEPTH_INPUT = 48-1;
    parameter DEPTH_OUTPUT = 16-1;
    parameter COMPUTE_DEPTH = 12;
    parameter FREQ_DIV = 1;

    parameter IDLE = 2'b00, RUN = 2'b01, DUMMY = 2'b10;

    reg [1:0] state, next_state;

    integer counter48;
    integer counter16;
    integer counter12;

    integer delay;

    reg clk1, clk2;

    reg valid_pipe_1;
    reg valid_pipe_2;

    reg finish_48;
    reg finish_12;
    reg finish_16;
    reg finish_48_1;

    reg c16_start;

    integer freq_div;

    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            state <= IDLE;
        end else begin
            state <= next_state;
        end
    end
    

    always @(*) begin
        case (state)
            IDLE: begin
                if (load_input) begin
                    next_state = DUMMY;
                end else begin
                    next_state = IDLE;
                end
            end
            DUMMY: begin
                next_state = RUN;
            end
            RUN: begin
                if(counter48==0 && counter16==0 && counter12==0)  begin
                    next_state = IDLE;
                end else begin
                    next_state = RUN;
                end
            end
            default: begin
                next_state = IDLE;
            end
        endcase
    end


    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            freq_div <= 0;
            clk1 <= 0;
        end else begin
            if (freq_div == (FREQ_DIV-1)) begin
                if(FREQ_DIV==1) begin
                    clk1 <= ~clk1;
                end else begin
                    clk1 <= 1'b1;
                end
                freq_div <= 0;
            end else begin
                clk1 <= 1'b0;
                freq_div <= freq_div + 1;
            end
        end
    end

    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            clk2 <= 0;
        end else begin
            clk2 <= clk1;
        end
    end

    



    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            counter48 <= 0;
            finish_48 <= 0;
        end else begin
            if (counter48 == 0) begin
                if (val_input==1'b1) begin
                    counter48 <= counter48 + 1;
                    finish_48 <= 1'b0;
                end
            end else begin
                if (val_input==1'b1) begin
                    if (counter48 == DEPTH_INPUT) begin
                        counter48 <= 0;
                        finish_48 <= 1'b1;
                    end else begin
                        counter48 <= counter48 + 1;
                        finish_48 <= 1'b0;
                    end
                end
            end
        end
    end


    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            counter12 <= 0;
            finish_12 <= 0;
        end else begin
            if (counter12 == 0) begin
                if (load_input) begin
                    counter12 <= counter12 + 1;
                    finish_12 <= 1'b0;
                end
            end else begin
                if (clk2==1'b1) begin
                    if (counter12 == COMPUTE_DEPTH) begin
                        counter12 <= 0;
                        finish_12 <= 1'b1;
                    end else begin
                        counter12 <= counter12 + 1;
                        finish_12 <= 1'b0;
                    end
                end
            end
        end
    end


    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            counter16 <= 0;
            finish_16 <= 0;
        end else begin
            if (counter16 == 0) begin
                if (c16_start) begin
                    counter16 <= counter16 + 1;
                    finish_16 <= 1'b0;
                end
            end else begin
                if (counter16 == DEPTH_OUTPUT) begin
                    counter16 <= 0;
                    finish_16 <= 1'b1;
                end else begin
                    counter16 <= counter16 + 1;
                    finish_16 <= 1'b0;
                end
            end
        end
    end

    always @(posedge clk or negedge rst)  begin
        if (!rst) begin
            delay <= 0;
        end else begin
            if ((counter48==DEPTH_INPUT && val_input) || (delay==2) ) begin
                delay <= 0;
            end else begin
                if (clk1) begin
                    delay <= delay + 1;
                end
            end
        end
    end



    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            load_input <= 1'b0;
        end else begin
            if((state==IDLE) && (valid_pipe_1==1'b1) && (delay==2)) begin
                load_input <= 1'b1;
            end else begin
                load_input <= 1'b0;
            end
        end
    end
    
    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            load_result <= 1'b0;
        end else begin
            if((state==IDLE) && (valid_pipe_2==1'b1) && (delay==2)) begin
                load_result <= 1'b1;
            end else begin
                load_result <= 1'b0;
            end
        end
    end

    reg tmp;
    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            c16_start <= 1'b0;
            finish_48_1 <= 1'b0;
            tmp <= 1'b0;
        end else begin
            c16_start <= load_result;
            finish_48_1 <= finish_48;
            if (load_input) begin
                tmp <= 1'b1;
            end else begin
                if ((finish_48==1'b0 && finish_48_1==1'b1) || (finish_48==1'b1 && finish_48_1==1'b0)) begin
                    tmp <= 1'b0;
                end
            end
        end
    end

    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            valid_pipe_1 <= 1'b0;
        end else begin
            if((state==IDLE) && (finish_48==1'b1)) begin
                if (tmp) begin
                    valid_pipe_1 <= 1'b0;
                end else begin
                    valid_pipe_1 <= 1'b1;
                end
            end
        end
    end

    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            valid_pipe_2 <= 1'b0;
        end else begin
            //if((counter48==0) && (counter12==0) && (counter16==0) && (finish_12==1'b1 && clk2)) begin
            if((state==IDLE)) begin
                if (load_input) begin
                    valid_pipe_2 <= 1'b1;
                end else if(!load_input && load_result)  begin
                    valid_pipe_2 <= 1'b0;
                end
            end
        end
    end

    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            we <= 1'b0;
        end else begin
            if (load_result==1'b1) begin
                we <= 1'b1;
            end else begin
                if (counter16==DEPTH_OUTPUT) begin
                    we <= 1'b0;
                end
            end 
        end
    end

    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            re_i <= 1'b1;
        end else begin
            if (counter48==DEPTH_INPUT && val_input) begin
                re_i <= 1'b0;
            end else if (delay == 2) begin
                re_i <= 1'b1;
            end
        end
    end


endmodule
