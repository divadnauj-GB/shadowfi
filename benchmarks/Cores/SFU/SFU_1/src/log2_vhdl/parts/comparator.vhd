-- Nombre de archivo	: comparator.vhd
--	Titulo				: comparador de magnitud configurable
-----------------------------------------------------------------------------	
-- Descripcion			: compara dos datos de entrada segun el modo seleccionado
--
-- 	WIDE				: numero de bits de los numeros a comparar
--		MODO				: 2 -> i_data1 < i_data2
--							  1 -> i_data1 > i_data2
--							  0 -> i_data1 = i_data2
--
-- 	i_term1			: Numero 1
-- 	i_term2			: Numero 2
-- 	o_result			: Resultado
--
-----------------------------------------------------------------------------	
-- Universidad Pedagogica y Tecnologica de Colombia.
-- Facultad de ingenieria.
-- Escuela de ingenieria Electronica - extension Tunja.
-- 
-- Autor: Cristhian Fernando Moreno Manrique
-- Marzo 2020
-----------------------------------------------------------------------------	
library ieee;
	use ieee.std_logic_1164.all;
	

entity comparator is 

	generic (WIDE		: 		natural:=	8;
				MODO		: 		natural:=	0);
	port	  (i_data1	: in	std_logic_vector(WIDE-1 downto 0);
				i_data2	: in 	std_logic_vector(WIDE-1 downto 0);
				o_result	: out std_logic);	
end entity;
-----------------------------------------------------------------------------	

architecture main of comparator is
	
begin	
	
	EQ: if (MODO = 0) generate
		o_result <= '1' when (i_data1 = i_data2) else '0';
	end generate;
	
	HG: if (MODO = 1) generate
		o_result <= '1' when (i_data1 > i_data2) else '0';
	end generate;
	
	LW: if (MODO > 1) generate
		o_result <= '1' when (i_data1 < i_data2) else '0';
	end generate;
	
end main;
-----------------------------------------------------------------------------	