-----------------------------------------------------------------------------	
-- constantes en complemento a dos

library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;
	use work.log2_pkg.all;

	
entity exp2_luts_64x23b is
	generic (SEG						: 		natural := 64);
	port 	  (i_lutA_addr				: in	std_logic_vector(4 downto 0); -- f_log2(SEG)-1 downto 0)
				i_lutB_addr				: in std_logic_vector(4 downto 0); -- f_log2(SEG)-1 downto 0)
				o_lutA					: out std_logic_vector(22 downto 0);
				o_lutB					: out std_logic_vector(22 downto 0));
end entity;


architecture arch of exp2_luts_64x23b is

signal s_lutA_addr :integer;
signal s_lutB_addr :integer;

begin
	s_lutA_addr <=to_integer(unsigned(i_lutA_addr));
	s_lutB_addr <=to_integer(unsigned(i_lutB_addr));
	
	luts: process(s_lutA_addr, s_lutB_addr) -- i_lutA_addr	: in	std_logic_vector(3 downto 0);
	begin
		case s_lutA_addr is
		when 0 => o_lutA	<= "00000000000000000000000";
		when 1 => o_lutA	<= "11111101100110100110011";
		when 2 => o_lutA	<= "11111011010101001101110";
		when 3 => o_lutA	<= "11111001001011110110111";
		when 4 => o_lutA	<= "11110111001010101101001";
		when 5 => o_lutA	<= "11110101010001111011110";
		when 6 => o_lutA	<= "11110011100001101110110";
		when 7 => o_lutA	<= "11110001111010010010000";
		when 8 => o_lutA	<= "11110000011011110001111";
		when 9 => o_lutA	<= "11101111000110011010110";
		when 10=> o_lutA	<= "11101101111010011001101";
		when 11=> o_lutA	<= "11101100110111111011011";
		when 12=> o_lutA	<= "11101011111111001101100";
		when 13=> o_lutA	<= "11101011010000011101110";
		when 14=> o_lutA	<= "11101010101011111010000";
		when 15=> o_lutA	<= "11101010010001110000100";
		when 16 => o_lutA	<= "11101010000010001111111";
		when 17 => o_lutA	<= "11101001111101100111001";
		when 18 => o_lutA	<= "11101010000100000101011";
		when 19 => o_lutA	<= "11101010010101111010001";
		when 20 => o_lutA	<= "11101010110011010101100";
		when 21 => o_lutA	<= "11101011011100100111100";
		when 22 => o_lutA	<= "11101100010010000001000";
		when 23 => o_lutA	<= "11101101010011110010111";
		when 24 => o_lutA	<= "11101110100010001110011";
		when 25 => o_lutA	<= "11101111111101100101011";
		when 26=> o_lutA	<= "11110001100110001001111";
		when 27=> o_lutA	<= "11110011011100001110100";
		when 28=> o_lutA	<= "11110101100000000110001";
		when 29=> o_lutA	<= "11110111110010000100000";
		when 30=> o_lutA	<= "11111010010010011100000";
		when 31=> o_lutA	<= "11111101000001100010010";
		when others => o_lutA <= "00000000000000000000000";
		end case;
		
		case s_lutB_addr is
		when 0 => o_lutB	<= "11111110110010001111111";
		when 1 => o_lutB	<= "11111100011100111010100";
		when 2 => o_lutB	<= "11111010001111100001011";
		when 3 => o_lutB	<= "11111000001010001111101";
		when 4 => o_lutB	<= "11110110001101010000101";
		when 5 => o_lutB	<= "11110100011000110000000";
		when 6 => o_lutB	<= "11110010101100111001101";
		when 7 => o_lutB	<= "11110001001001111001101";
		when 8 => o_lutB	<= "11101111101111111100011";
		when 9 => o_lutB	<= "11101110011111001110101";
		when 10=> o_lutB	<= "11101101010111111101010";
		when 11=> o_lutB	<= "11101100011010010101101";
		when 12=> o_lutB	<= "11101011100110100101000";
		when 13=> o_lutB	<= "11101010111100111001100";
		when 14=> o_lutB	<= "11101010011101100001001";
		when 15=> o_lutB	<= "11101010001000101010001";
		when 16 => o_lutB	<= "11101001111110100011101";
		when 17 => o_lutB	<= "11101001111111011100011";
		when 18 => o_lutB	<= "11101010001011100011111";
		when 19 => o_lutB	<= "11101010100011001010000";
		when 20 => o_lutB	<= "11101011000110011110101";
		when 21 => o_lutB	<= "11101011110101110010010";
		when 22 => o_lutB	<= "11101100110001010101110";
		when 23 => o_lutB	<= "11101101111001011010010";
		when 24 => o_lutB	<= "11101111001110010001010";
		when 25 => o_lutB	<= "11110000110000001100110";
		when 26=> o_lutB	<= "11110010011111011111000";
		when 27=> o_lutB	<= "11110100011100011010110";
		when 28=> o_lutB	<= "11110110100111010011000";
		when 29=> o_lutB	<= "11111001000000011011100";
		when 30=> o_lutB	<= "11111011101000001000001";
		when 31=> o_lutB	<= "11111110011110101101010";
		when others => o_lutB <= "00000000000000000000000";
		end case;
		
	end process;
end arch;
