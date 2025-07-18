module tb_sbtr_cntrl #(parameter integer CLK_PERIOD = 20) (TFEn, CLK, RST, EN, SI, DONE, SO);
  output SO;
  output TFEn, CLK, RST, EN, SI, DONE;

  reg TFEn, CLK, RST, EN, SI, DONE;
  reg enable=0;

  integer fi_input;
  integer returnval;

  integer components, target_component, sr_lenght, start_bit_pos, end_bit_pos;
  integer index;
  integer component_id;

  integer counter;
  integer timeout;
  reg [1:0] FI_Mode;

  always
  begin
    #(CLK_PERIOD/2) CLK=~CLK;
  end

  always@(posedge CLK, negedge RST)
  begin
    if (!RST)
    begin
      counter <= 0;
      TFEn <= 0;
    end
    else
    begin
      if (DONE)
      begin
        if(FI_Mode<2)
        begin
          TFEn <= 1;
        end
        else
        begin
          if (counter==timeout-1)
          begin
            TFEn <= 1;
          end
          else
          begin
            TFEn <= 0;
          end
        end
        if (counter<timeout)
        begin
          counter<=counter + 1;
        end
      end
    end
  end

  initial
  begin
    DONE=0;
    RST=0;
    CLK=0;
    enable=0;
    EN=0;
    SI=0;
    fi_input =  $fopen("fault_descriptor.txt","r");
    returnval = $fscanf(fi_input,"%d",FI_Mode);
    returnval = $fscanf(fi_input,"%d",components);
    returnval = $fscanf(fi_input,"%d",target_component);
    returnval = $fscanf(fi_input,"%d",sr_lenght);
    returnval = $fscanf(fi_input,"%d",timeout);
    returnval = $fscanf(fi_input,"%d",start_bit_pos);
    returnval = $fscanf(fi_input,"%d",end_bit_pos);
    #500;
    RST=1;
    #100;
    EN=1;

    for(index=0;index<sr_lenght;index=index+1)
      begin
        @(negedge CLK);
        returnval = $fscanf(fi_input,"%d",SI);
      end
    @(negedge CLK);
    EN=0;
    SI=0;
    DONE=1;
  end

endmodule
