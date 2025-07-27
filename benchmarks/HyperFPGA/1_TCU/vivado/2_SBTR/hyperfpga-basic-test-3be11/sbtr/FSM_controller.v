module FSM_controller(clk,rst,val_input, load_result, shift_out);

    input clk;
    input rst;
    input val_input;
    output reg load_result;
    output reg shift_out;

    parameter DEPTH_INPUT = 48;
    parameter DEPTH_OUTPUT = 16;
    parameter COMPUTE_DEPTH = 32;

    parameter LOAD_INPUT = 2'b00, COMPUTE = 2'b01, SHIFTOUT = 2'b10;
    reg [1:0] state, next_state;

    integer counter;

    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            state <= LOAD_INPUT;
        end else begin
            state <= next_state;
        end
    end

    always @(*) begin
        case (state)
            LOAD_INPUT: begin
                load_result = 0;
                shift_out = 0;
                if(counter==DEPTH_INPUT) begin
                    next_state = COMPUTE;
                end else begin
                    next_state = LOAD_INPUT;
                end
            end
            COMPUTE: begin
                if(counter==COMPUTE_DEPTH) begin
                    next_state = SHIFTOUT;
                    load_result = 1;
                    shift_out = 0;
                end else begin
                    next_state = COMPUTE;
                    load_result = 0;
                    shift_out = 0;
                end
            end
            SHIFTOUT: begin
                if(counter==DEPTH_OUTPUT) begin
                    next_state = LOAD_INPUT;
                    load_result = 0;
                    shift_out = 0;
                end else begin
                    next_state = SHIFTOUT;
                    load_result = 0;
                    shift_out = 1;
                end
            end
            default: begin
                next_state = LOAD_INPUT;
            end
        endcase
    end


    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            counter <= 0;
        end else begin
            case (state)
                LOAD_INPUT: begin
                    if(counter == DEPTH_INPUT) begin
                        counter <= 0;
                    end else begin
                        if(val_input==1) begin
                            counter <= counter + 1;
                        end
                    end
                end
                COMPUTE: begin
                    if(counter == COMPUTE_DEPTH) begin
                        counter <= 0;
                    end else begin
                        counter <= counter + 1;
                    end
                end
                SHIFTOUT: begin
                    if(counter == DEPTH_OUTPUT) begin
                        counter <= 0;
                    end else begin
                        counter <= counter + 1;
                    end
                end
                default: begin
                    counter <= 0;
                end
            endcase
        end
    end

endmodule