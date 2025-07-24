-- Nombre de archivo	: sum_ripple_carry_adder.vhd
--	Titulo				: Sumador/restador punto fijo
-----------------------------------------------------------------------------	
-- Descripcion			: Sumador/restador arquitectura Ripple Carry Adder.
--							  Permite aplicar complemento 1 a uno o ambos numeros
--							  de entrada.
--
-- 	WIDE				: numero de bits de los numeros a operar
--		C1					: 3 -> complemento 1 a ambos numeros
--							  2 -> complemento 1 a numero 2
--							  1 -> complemento 1 a numero 1
--							  0 -> no aplicar C1
--
-- 	i_term1			: Numero 1
-- 	i_term2			: Numero 2
--    i_cin				: acarreo de entrada
-- 	o_result			: Resultado
--    o_cout			: Acarreo de salida
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
	

entity sum_ripple_carry_adder is 

	generic (WIDE		: 		natural:= 32;		
				C1			: 		natural:= 0);								-- sin complemento 1 por defecto
	port	  (i_term1	: in	std_logic_vector(WIDE-1 downto 0);
				i_term2	: in	std_logic_vector(WIDE-1 downto 0);
				i_cin		: in	std_logic;
				o_sum		: out	std_logic_vector(WIDE-1 downto 0);
				o_cout	: out std_logic);
end entity;
-----------------------------------------------------------------------------				

architecture main of sum_ripple_carry_adder is

	signal w_cout		: 		std_logic_vector(WIDE-1 downto 0);
	signal w_term1		: 		std_logic_vector(WIDE-1 downto 0);
	signal w_term2		: 		std_logic_vector(WIDE-1 downto 0);
	
begin	
	
	assert C1 > 3
		report "Opcion de C1 no disponible, intente con 0, 1, 2 o 3"
		severity note;
	
	
	BLOCK_A: 
	for i in WIDE-1 downto 0 generate
		
		-----------------------------------------------------------------------
		-- configuracion de complemento a uno
		-----------------------------------------------------------------------
		MD0: if C1 = 0 generate
			w_term1(i) <= i_term1(i);
			w_term2(i) <= i_term2(i);
		end generate MD0;
		MD1: if C1 = 1 generate
			w_term1(i) <= not(i_term1(i));
			w_term2(i) <= i_term2(i);
		end generate MD1;
		MD2: if C1 = 2 generate
			w_term1(i) <= i_term1(i);
			w_term2(i) <= not(i_term2(i));
		end generate MD2;
		MD3: if C1 = 3 generate
			w_term1(i) <= not(i_term1(i));
			w_term2(i) <= not(i_term2(i));
		end generate MD3;
		
		-----------------------------------------------------------------------
		-- arquitectura Ripple Carry Adder
		-----------------------------------------------------------------------		
		LowBit: if i=0 generate
			a: entity work.FA port map(
				i_term1	=> w_term1(i),
				i_term2	=> w_term2(i), 
				i_cin		=> i_cin,
				o_Sum 	=> o_sum(i),
				o_cout	=> w_cout(i)
			);
		end generate;	
		
		OtherBits: if i/=0 generate
			b: entity work.FA port map(
				i_term1	=> w_term1(i),
				i_term2	=> w_term2(i), 
				i_cin 	=> w_cout(i-1),
				o_sum 	=> o_sum(i),
				o_cout 	=> w_cout(i)
			);
		end generate;	
		
	end generate BLOCK_A;
	
	
	o_cout <= w_cout(WIDE-1); 
	
end main;

-------------------------------------------------------