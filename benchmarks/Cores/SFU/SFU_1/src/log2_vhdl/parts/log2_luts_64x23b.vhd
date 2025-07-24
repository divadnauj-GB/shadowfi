-----------------------------------------------------------------------------	

library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;
	use work.log2_pkg.all;

	
entity log2_luts_64x23b is
	generic (SEG						: 		natural := 64);
	port 	  (i_lutA_addr				: in	std_logic_vector(4 downto 0); -- f_log2(SEG)-1 downto 0)
				i_lutB_addr				: in std_logic_vector(4 downto 0); -- f_log2(SEG)-1 downto 0)
				o_lutA					: out std_logic_vector(22 downto 0);
				o_lutB					: out std_logic_vector(22 downto 0));
end entity;

architecture rtl of log2_luts_64x23b is
signal s_lutA_addr	:integer;
signal s_lutB_addr  :integer;

begin

s_lutA_addr <= to_integer(unsigned(i_lutA_addr));
s_lutB_addr <= to_integer(unsigned(i_lutB_addr));

	luts: process(s_lutA_addr, s_lutB_addr) -- i_lutA_addr	: in	std_logic_vector(3 downto 0);
	begin
		case s_lutA_addr is
		when 0 => o_lutA	<= "00000000000000000000000";
		when 1 => o_lutA	<= "00000011010111110010111";
		when 2 => o_lutA	<= "00000110011001011010000";
		when 3 => o_lutA	<= "00001001000110100100001";
		when 4 => o_lutA	<= "00001011100000011011000";
		when 5 => o_lutA	<= "00001101101000000010010";
		when 6 => o_lutA	<= "00001111011110011000001";
		when 7 => o_lutA	<= "00010001000100010110001";
		when 8 => o_lutA	<= "00010010011010110001011";
		when 9 => o_lutA	<= "00010011100010011010110";
		when 10=> o_lutA	<= "00010100011100000000001";
		when 11=> o_lutA	<= "00010101001000001011101";
		when 12=> o_lutA	<= "00010101100111100100111";
		when 13=> o_lutA	<= "00010101111010110000100";
		when 14=> o_lutA	<= "00010110000010010001000";
		when 15=> o_lutA	<= "00010101111110100110100";
		when 16 => o_lutA	<= "00010101110000001111000";
		when 17 => o_lutA	<= "00010101010111100110111";
		when 18 => o_lutA	<= "00010100110101001000100";
		when 19 => o_lutA	<= "00010100001001001100111";
		when 20 => o_lutA	<= "00010011010100001011101";
		when 21 => o_lutA	<= "00010010010110011010111";
		when 22 => o_lutA	<= "00010001010000001111100";
		when 23 => o_lutA	<= "00010000000001111101010";
		when 24 => o_lutA	<= "00001110101011110110110";
		when 25 => o_lutA	<= "00001101001110001110000";
		when 26=> o_lutA	<= "00001011101001010011011";
		when 27=> o_lutA	<= "00001001111101010111001";
		when 28=> o_lutA	<= "00001000001010101000010";
		when 29=> o_lutA	<= "00000110010001010101001";
		when 30=> o_lutA	<= "00000100010001101011011";
		when 31=> o_lutA	<= "00000010001011111000000";
		when others => o_lutA <= "00000000000000000000000";
		end case;
		
		case s_lutB_addr is
		when 0 => o_lutB	<= "00000001101110111011100";
		when 1 => o_lutB	<= "00000100111011001111000";
		when 2 => o_lutB	<= "00000111110010011110000";
		when 3 => o_lutB	<= "00001010010101110101101";
		when 4 => o_lutB	<= "00001100100110011100101";
		when 5 => o_lutB	<= "00001110100101010011101";
		when 6 => o_lutB	<= "00010000010011010110110";
		when 7 => o_lutB	<= "00010001110001011100111";
		when 8 => o_lutB	<= "00010011000000011001011";
		when 9 => o_lutB	<= "00010100000000111011010";
		when 10=> o_lutB	<= "00010100110011101110100";
		when 11=> o_lutB	<= "00010101011001011100010";
		when 12=> o_lutB	<= "00010101110010101010010";
		when 13=> o_lutB	<= "00010101111111111100001";
		when 14=> o_lutB	<= "00010110000001110011010";
		when 15=> o_lutB	<= "00010101111000101110101";
		when 16 => o_lutB	<= "00010101100101001011010";
		when 17 => o_lutB	<= "00010101000111100100111";
		when 18 => o_lutB	<= "00010100100000010100111";
		when 19 => o_lutB	<= "00010011101111110011101";
		when 20 => o_lutB	<= "00010010110110010111111";
		when 21 => o_lutB	<= "00010001110100010111010";
		when 22 => o_lutB	<= "00010000101010000110000";
		when 23 => o_lutB	<= "00001111010111110111011";
		when 24 => o_lutB	<= "00001101111101111101101";
		when 25 => o_lutB	<= "00001100011100101001111";
		when 26=> o_lutB	<= "00001010110100001100100";
		when 27=> o_lutB	<= "00001001000100110101001";
		when 28=> o_lutB	<= "00000111001110110010011";
		when 29=> o_lutB	<= "00000101010010010010010";
		when 30=> o_lutB	<= "00000011001111100010001";
		when 31=> o_lutB	<= "00000001000110101110101";
		when others => o_lutB <= "00000000000000000000000";
		end case;
		
	end process;
end rtl;
