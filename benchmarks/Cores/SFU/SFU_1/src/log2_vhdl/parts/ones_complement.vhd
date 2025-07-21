-- Nombre de archivo	: ones_complement.vhd
--	Titulo				: operacion complemento a uno
-----------------------------------------------------------------------------	
-- Descripcion			: realiza la operacion de complemento a uno al dato de 
--							  entrada solo si i_en es habilitado.
--
-- 	WIDE				: ancho del dato
--
-- 	i_data			: dato a operar
-- 	i_en				: 1-> habilita operacion
--    o_data			: resultado
-- 	
-- Notas:
--		si i_en = 0, o_data = i_data
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


entity ones_complement is

	generic (WIDE 		: positive := 7);
		 port(i_data 	: in std_logic_vector (WIDE-1 downto 0);
				i_en		: in std_logic;	
				o_data 	: out std_logic_vector (WIDE-1 downto 0));
end ones_complement;
-----------------------------------------------------------------------------	

architecture main of ones_complement is

	signal w_C1 :std_logic_vector(WIDE-1 downto 0);

begin

	a:for i in 0 to WIDE-1 generate
			w_C1(i) 	<= i_data(i) xor i_en;
	end generate;
  
  o_data <= std_logic_vector(w_C1);
  
end main;
-----------------------------------------------------------------------------	