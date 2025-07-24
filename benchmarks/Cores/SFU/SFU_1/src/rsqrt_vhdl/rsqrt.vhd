library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.log2_pkg.all;

entity rsqrt is
port(
	i_x		:in	std_logic_vector(31 downto 0);
	o_rsqrt	:out std_logic_vector(31 downto 0)
);
end entity rsqrt;

architecture oper of rsqrt is
constant K	:unsigned(31 downto 0) := X"5F375A86"; --X"5F3759DF";
signal Y	:std_logic_vector(31 downto 0);
signal X2	:std_logic_vector(31 downto 0);

signal mult1, mult2, mult3, mult4, resta :std_logic_vector(31 downto 0);
signal w_case_en	: std_logic;
signal w_ieeecase	: std_logic_vector(i_x'left downto 0);

begin

Y <= std_logic_vector(K-unsigned('0'&i_x(31 downto 1)));
X2 <= i_x(31)&std_logic_vector(unsigned(i_x(30 downto 23))-1)&i_x(22 downto 0);

FP1: entity work.multFP
	port map(
	entrada_x  => X"3fc00000",
	entrada_y  => Y,
	salida     => mult1
	);
	
FP2: entity work.multFP
	port map(
	entrada_x  => Y,
	entrada_y  => Y,
	salida     => mult2
	);
	
FP3: entity work.multFP
	port map(
	entrada_x  => Y,
	entrada_y  => X2,
	salida     => mult3
	);
	
FP4: entity work.multFP
	port map(
	entrada_x  => mult2,
	entrada_y  => mult3,
	salida     => mult4
	);

SUB: entity work.suma_resta
	port map(
	operando1  => unsigned(mult1),
	operando2  => unsigned(mult4),
	operacion  => "0010",
	std_logic_vector(resultado)  => resta
	);
	
IEEECASE: entity work.rsqrt_ieee
	port map(
	i_data		=> i_x,
	o_case 		=> w_ieeecase,
	o_case_en	=> w_case_en
	);

with w_case_en select
	o_rsqrt <=  resta 		when '0',
				w_ieeecase 	when '1',
				resta		when others;
	
end oper;