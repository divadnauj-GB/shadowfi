library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity LUT_C2_exp is
	generic(
		word_bits	:natural:=10;
		bus_bits	:natural:=14;
		add_bits	:natural:=6
	);
	port(
		addr		:in std_logic_vector(add_bits-1 downto 0);
		data		:out std_logic_vector(bus_bits-1 downto 0)
	);
end entity;

architecture behav of LUT_C2_exp is
	type storage is array (0 to 2**add_bits-1) of std_logic_vector(word_bits-1 downto 0);
	constant rom:storage:=(
		"0111101110",
		"0111110100",
		"0111111001",
		"0111111110",
		"1000000100",
		"1000001010",
		"1000001111",
		"1000010101",
		"1000011011",
		"1000100001",
		"1000100111",
		"1000101101",
		"1000110011",
		"1000111001",
		"1000111111",
		"1001000101",
		"1001001100",
		"1001010010",
		"1001011001",
		"1001011111",
		"1001100110",
		"1001101100",
		"1001110011",
		"1001111010",
		"1010000001",
		"1010001000",
		"1010001111",
		"1010010110",
		"1010011101",
		"1010100101",
		"1010101100",
		"1010110100",
		"1010111011",
		"1011000011",
		"1011001010",
		"1011010010",
		"1011011010",
		"1011100010",
		"1011101010",
		"1011110010",
		"1011111010",
		"1100000011",
		"1100001011",
		"1100010100",
		"1100011100",
		"1100100101",
		"1100101110",
		"1100110110",
		"1100111111",
		"1101001000",
		"1101010010",
		"1101011011",
		"1101100100",
		"1101101110",
		"1101110111",
		"1110000001",
		"1110001011",
		"1110010101",
		"1110011111",
		"1110101001",
		"1110110011",
		"1110111101",
		"1111001000",
		"1111010010"
	);
begin
	data <= "00"&rom(to_integer(unsigned(addr)))&"00";
end architecture;