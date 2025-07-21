
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use ieee.std_logic_textio.all; -- require for writing/reading std_logic etc

entity sfu_tb is
end entity sfu_tb;


architecture verification of sfu_tb is 
file f_input_cordic  : text;
file f_input_rsqrt  : text;
file f_input_log2  : text;
file f_input_ex2   : text;

file f_output_sin : text;
file f_output_cos: text;
file f_output_rsqrt : text;
file f_output_log2 : text;
file f_output_ex2 : text;


signal s_clk_i	  :std_logic :='0';
signal s_rst_n	  :std_logic :='0';
signal s_start_i  :std_logic :='0';
signal s_src1_i	  :std_logic_vector(31 downto 0) :=(others=>'0');
signal s_selop_i  :std_logic_vector(2 downto 0) :=(others=>'0');
signal s_Result_o :std_logic_vector(31 downto 0);
signal s_stall_o  :std_logic;

signal lsfr_input  :std_logic_vector(31 downto 0):=X"00000001";
signal lsfr_op	   :std_logic_vector(3 downto 0) :="1000";

begin 
DUT: entity work.sfu
	port map(clk_i	  => s_clk_i,	 
	         rst_n	  => s_rst_n,	 
	         start_i  => s_start_i, 
	         src1_i	  => s_src1_i,	 
	         selop_i  => s_selop_i, 
	         Result_o => s_Result_o,
	         stall_o  => s_stall_o); 
	
clk_gen: process
		begin
			wait for 50 ns;
			s_clk_i <= not s_clk_i;
		end process;
	
rst_gen: process
		begin
			wait for 500 ns;
			s_rst_n <= '1';
			wait;
		end process;	

gata_gen:process
    variable v_i_line   : line;	-- read lines one by one from f_input
    variable v_o_line   : line; -- write lines one by one to f_output
    variable v_x	  : std_logic_vector(31 downto 0); -- valor de entrada
    variable v_comma		: character;

    variable v_character: character;
    variable hex_val    : std_logic_vector(3 downto 0);
    variable offset     : integer;

  begin

  -- open files
  file_open(f_input_cordic, "input_cordic.csv", read_mode);
  file_open(f_input_rsqrt , "input_rsqrt.csv", read_mode);
  file_open(f_input_log2  , "input_log2.csv", read_mode);
  file_open(f_input_ex2   , "input_ex2.csv", read_mode);
  
  file_open(f_output_sin, "output_sin.csv", write_mode); 
  file_open(f_output_cos, "output_cos.csv", write_mode); 
  file_open(f_output_rsqrt , "output_rsqrt.csv", write_mode); 
  file_open(f_output_log2  , "output_log2.csv", write_mode); 
  file_open(f_output_ex2   , "output_ex2.csv", write_mode); 

	wait on s_clk_i until s_rst_n='1';
  --========================SIN=============================================	
  -- encabezado de texto
  write(v_o_line, string'("Input,Sin"));
  writeline(f_output_sin, v_o_line);
  -----------------------------------------------------------------------------
  readline(f_input_cordic, v_i_line);		-- se omite linea de encabezado
  while not endfile(f_input_cordic) loop
  	readline(f_input_cordic, v_i_line);  	
	-- lectura de hexadecimal
    offset := 0;
    while offset < v_x'left loop
      read(v_i_line, v_character);
      case v_character is
        when '0' => hex_val := "0000";
	      when '1' => hex_val := "0001";
	      when '2' => hex_val := "0010";
	      when '3' => hex_val := "0011";
	      when '4' => hex_val := "0100";
	      when '5' => hex_val := "0101";
	      when '6' => hex_val := "0110";
	      when '7' => hex_val := "0111";
	      when '8' => hex_val := "1000";
	      when '9' => hex_val := "1001";
	      when 'A' | 'a' => hex_val := "1010";
	      when 'B' | 'b' => hex_val := "1011";
	      when 'C' | 'c' => hex_val := "1100";
	      when 'D' | 'd' => hex_val := "1101";
	      when 'E' | 'e' => hex_val := "1110";
	      when 'F' | 'f' => hex_val := "1111";
	      when others 	=>	hex_val := "XXXX";
	       assert false report "Found non-hex character '" & v_character & "'";
      end case;
      v_x(v_x'left - offset downto v_x'left-offset-3) := hex_val;
      offset := offset + 4;
    end loop;

    -- iniciar calculo
	s_selop_i <= "000";
    s_src1_i <= v_x;
	s_start_i <= '1';
	wait until falling_edge(s_clk_i);
	s_start_i <= '0';
	wait on s_clk_i until s_stall_o='0';    
    -- escribir resultados
    hwrite(v_o_line, s_src1_i);
    write(v_o_line, string'(","));
    hwrite(v_o_line, s_Result_o);
    writeline(f_output_sin, v_o_line);
	wait until falling_edge(s_clk_i);
  end  loop;
  --file_close(f_output_sin);
  file_close(f_input_cordic);
  file_open(f_input_cordic, "input_cordic.csv", read_mode);
  --========================COS=============================================
   -- encabezado de texto
  write(v_o_line, string'("Input,cos"));
  writeline(f_output_cos, v_o_line);
  -----------------------------------------------------------------------------
  readline(f_input_cordic, v_i_line);		-- se omite linea de encabezado
  while not endfile(f_input_cordic) loop
  	readline(f_input_cordic, v_i_line);  	
	-- lectura de hexadecimal
    offset := 0;
    while offset < v_x'left loop
      read(v_i_line, v_character);
      case v_character is
        when '0' => hex_val := "0000";
	      when '1' => hex_val := "0001";
	      when '2' => hex_val := "0010";
	      when '3' => hex_val := "0011";
	      when '4' => hex_val := "0100";
	      when '5' => hex_val := "0101";
	      when '6' => hex_val := "0110";
	      when '7' => hex_val := "0111";
	      when '8' => hex_val := "1000";
	      when '9' => hex_val := "1001";
	      when 'A' | 'a' => hex_val := "1010";
	      when 'B' | 'b' => hex_val := "1011";
	      when 'C' | 'c' => hex_val := "1100";
	      when 'D' | 'd' => hex_val := "1101";
	      when 'E' | 'e' => hex_val := "1110";
	      when 'F' | 'f' => hex_val := "1111";
	      when others 	=>	hex_val := "XXXX";
	       assert false report "Found non-hex character '" & v_character & "'";
      end case;
      v_x(v_x'left - offset downto v_x'left-offset-3) := hex_val;
      offset := offset + 4;
    end loop;

    -- iniciar calculo
	s_selop_i <= "001";
    s_src1_i <= v_x;
	s_start_i <= '1';
	wait until falling_edge(s_clk_i);
	s_start_i <= '0';
	wait on s_clk_i until s_stall_o='0';    
    -- escribir resultados
    hwrite(v_o_line, s_src1_i);
    write(v_o_line, string'(","));
    hwrite(v_o_line, s_Result_o);
    writeline(f_output_cos, v_o_line);
	wait until falling_edge(s_clk_i);
  end  loop;
  
  --=======================RSQRT=============================================
  -- encabezado de texto
  write(v_o_line, string'("Input,rsqrt"));
  writeline(f_output_rsqrt, v_o_line);
  -----------------------------------------------------------------------------
  readline(f_input_rsqrt, v_i_line);		-- se omite linea de encabezado
  while not endfile(f_input_rsqrt) loop
  	readline(f_input_rsqrt, v_i_line);  	
	-- lectura de hexadecimal
    offset := 0;
    while offset < v_x'left loop
      read(v_i_line, v_character);
      case v_character is
        when '0' => hex_val := "0000";
	      when '1' => hex_val := "0001";
	      when '2' => hex_val := "0010";
	      when '3' => hex_val := "0011";
	      when '4' => hex_val := "0100";
	      when '5' => hex_val := "0101";
	      when '6' => hex_val := "0110";
	      when '7' => hex_val := "0111";
	      when '8' => hex_val := "1000";
	      when '9' => hex_val := "1001";
	      when 'A' | 'a' => hex_val := "1010";
	      when 'B' | 'b' => hex_val := "1011";
	      when 'C' | 'c' => hex_val := "1100";
	      when 'D' | 'd' => hex_val := "1101";
	      when 'E' | 'e' => hex_val := "1110";
	      when 'F' | 'f' => hex_val := "1111";
	      when others 	=>	hex_val := "XXXX";
	       assert false report "Found non-hex character '" & v_character & "'";
      end case;
      v_x(v_x'left - offset downto v_x'left-offset-3) := hex_val;
      offset := offset + 4;
    end loop;

    -- iniciar calculo
	s_selop_i <= "010";
    s_src1_i <= v_x;
	s_start_i <= '1';
	wait until falling_edge(s_clk_i);
	s_start_i <= '0';
	wait on s_clk_i until s_stall_o='0';    
    -- escribir resultados
    hwrite(v_o_line, s_src1_i);
    write(v_o_line, string'(","));
    hwrite(v_o_line, s_Result_o);
    writeline(f_output_rsqrt, v_o_line);
	wait until falling_edge(s_clk_i);
  end  loop;
  --========================LOG2=============================================
    -- encabezado de texto
  write(v_o_line, string'("Input,log2"));
  writeline(f_output_log2, v_o_line);
  -----------------------------------------------------------------------------
  readline(f_input_log2, v_i_line);		-- se omite linea de encabezado
  while not endfile(f_input_log2) loop
  	readline(f_input_log2, v_i_line);  	
	-- lectura de hexadecimal
    offset := 0;
    while offset < v_x'left loop
      read(v_i_line, v_character);
      case v_character is
        when '0' => hex_val := "0000";
	      when '1' => hex_val := "0001";
	      when '2' => hex_val := "0010";
	      when '3' => hex_val := "0011";
	      when '4' => hex_val := "0100";
	      when '5' => hex_val := "0101";
	      when '6' => hex_val := "0110";
	      when '7' => hex_val := "0111";
	      when '8' => hex_val := "1000";
	      when '9' => hex_val := "1001";
	      when 'A' | 'a' => hex_val := "1010";
	      when 'B' | 'b' => hex_val := "1011";
	      when 'C' | 'c' => hex_val := "1100";
	      when 'D' | 'd' => hex_val := "1101";
	      when 'E' | 'e' => hex_val := "1110";
	      when 'F' | 'f' => hex_val := "1111";
	      when others 	=>	hex_val := "XXXX";
	       assert false report "Found non-hex character '" & v_character & "'";
      end case;
      v_x(v_x'left - offset downto v_x'left-offset-3) := hex_val;
      offset := offset + 4;
    end loop;

    -- iniciar calculo
	s_selop_i <= "011";
    s_src1_i <= v_x;
	s_start_i <= '1';
	wait until falling_edge(s_clk_i);
	s_start_i <= '0';
	wait on s_clk_i until s_stall_o='0';    
    -- escribir resultados
    hwrite(v_o_line, s_src1_i);
    write(v_o_line, string'(","));
    hwrite(v_o_line, s_Result_o);
    writeline(f_output_log2, v_o_line);
	wait until falling_edge(s_clk_i);
  end  loop;
  --========================EX22=============================================
    -- encabezado de texto
  write(v_o_line, string'("Input,ex2"));
  writeline(f_output_ex2, v_o_line);
  -----------------------------------------------------------------------------
  readline(f_input_ex2, v_i_line);		-- se omite linea de encabezado
  while not endfile(f_input_ex2) loop
  	readline(f_input_ex2, v_i_line);  	
	-- lectura de hexadecimal
    offset := 0;
    while offset < v_x'left loop
      read(v_i_line, v_character);
      case v_character is
        when '0' => hex_val := "0000";
	      when '1' => hex_val := "0001";
	      when '2' => hex_val := "0010";
	      when '3' => hex_val := "0011";
	      when '4' => hex_val := "0100";
	      when '5' => hex_val := "0101";
	      when '6' => hex_val := "0110";
	      when '7' => hex_val := "0111";
	      when '8' => hex_val := "1000";
	      when '9' => hex_val := "1001";
	      when 'A' | 'a' => hex_val := "1010";
	      when 'B' | 'b' => hex_val := "1011";
	      when 'C' | 'c' => hex_val := "1100";
	      when 'D' | 'd' => hex_val := "1101";
	      when 'E' | 'e' => hex_val := "1110";
	      when 'F' | 'f' => hex_val := "1111";
	      when others 	=>	hex_val := "XXXX";
	       assert false report "Found non-hex character '" & v_character & "'";
      end case;
      v_x(v_x'left - offset downto v_x'left-offset-3) := hex_val;
      offset := offset + 4;
    end loop;

    -- iniciar calculo
	s_selop_i <= "100";
    s_src1_i <= v_x;
	s_start_i <= '1';
	wait until falling_edge(s_clk_i);
	s_start_i <= '0';
	wait on s_clk_i until s_stall_o='0';    
    -- escribir resultados
    hwrite(v_o_line, s_src1_i);
    write(v_o_line, string'(","));
    hwrite(v_o_line, s_Result_o);
    writeline(f_output_ex2, v_o_line);
	wait until falling_edge(s_clk_i);
  end  loop;
  -----------------------------------------------------------------------------
  -- close  files
  file_close(f_input_cordic);
  file_close(f_input_rsqrt );
  file_close(f_input_log2  );
  file_close(f_input_ex2   );
  
  file_close(f_output_sin );
  file_close(f_output_cos );
  file_close(f_output_rsqrt);
  file_close(f_output_log2 );
  file_close(f_output_ex2  );
  
  
  for i in 0 to 20000 loop

	s_selop_i <= lsfr_op(2 downto 0);
    s_src1_i <= lsfr_input;
	s_start_i <= '1';
	wait until falling_edge(s_clk_i);
	s_start_i <= '0';
	wait on s_clk_i until s_stall_o='0'; 	
	wait until falling_edge(s_clk_i);
	lsfr_input(30 downto 0) <=lsfr_input(31 downto 1);
	lsfr_input(31) <= lsfr_input(0) xor lsfr_input(5)xor lsfr_input(12)xor lsfr_input(15)xor lsfr_input(22)xor lsfr_input(24);
	lsfr_op(2 downto 0) <= lsfr_op(3 downto 1);
	lsfr_op(3) <= lsfr_op(0) xor lsfr_op(2);
  end loop;
  
  wait;
  end process;

	
end verification;