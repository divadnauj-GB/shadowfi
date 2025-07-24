-- FULL ADDER
-- universidad Pedagogica y Tecnologica de Colombia.
-- Facultad de ingenieria.
-- Escuela de ingenieria Electronica - extension Tunja.
-- Semillero de investigacion DDA y PDI
-- Autor: Cristhian Fernando Moreno Manrique


-------------------------------------------------------

LIBRARY ieee;
USE ieee.std_logic_1164.all;
-------------------------------------------------------


entity FA is

	port(
		i_term1	:in std_logic;
		i_term2	:in std_logic;
		i_cin		:in std_logic;	
		o_sum		:out std_logic;
		o_cout	:out std_logic
	);
	
end entity;
-------------------------------------------------------				

architecture main of FA is
	signal s_xor: std_logic;
begin	
	s_xor		<= i_term1 xor i_term2;
	o_cout	<= (i_term1 and i_term2) or (i_cin and s_xor);
	o_sum 	<=  s_xor xor i_cin;
	
----	option 2:
--	o_cout	<= (i_term1 and i_term2) or (i_term1 and i_cin) or (i_term2 and i_cin);
--	o_sum 	<= i_term1 xor i_term2 xor i_cin;
	
end main;
-------------------------------------------------------