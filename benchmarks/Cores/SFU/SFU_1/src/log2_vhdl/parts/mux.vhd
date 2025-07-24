-- Nombre de archivo	: mux.vhd
--	Titulo				: multiplexor configurable
-----------------------------------------------------------------------------	
-- Descripcion			: multiplexor con opcion de configuracion de las lineas
--							  seleccion y ancho de dato. Los datos a multiplexar 
--							  debe ingresar por i_data concatenados, ejemplo, si se 
--							  quiere multiplexar data1 y data2 deben ingresar por i_data
--							  como data2&data1, de esta manera se consigue: 
--							  	0 -> i_select:  o_data -> data1 
--							  	1 -> i_select:  o_data -> data2 
--							  
--
-- 	SELECT_BITS		: lineas de seleccion del multiplexor
--		DATA_BITS		: ancho de los datos a multiplexar
--
-- 	i_data			: datos de entrada
-- 	i_select			: Numero 2
-- 	o_data			: Resultado
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
	use ieee.numeric_std.all;
	

entity mux is 

	generic (SELECT_BITS	: 		natural := 2;	-- dos lineas de seleccion (2^2 datos).
				DATA_BITS	: 		natural := 8); -- Cada dato de 8 bits
	port	  (i_data		: in	std_logic_vector(2**SELECT_BITS*DATA_BITS-1 downto 0);
				i_select		: in	std_logic_vector(SELECT_BITS-1 downto 0);
				o_data		: out std_logic_vector(DATA_BITS-1 downto 0));
end entity;
-----------------------------------------------------------------------------	

architecture main of mux is	

	type data_array is array(2**SELECT_BITS-1 downto 0) of std_logic_vector(DATA_BITS-1 downto 0);	
	signal w_data : data_array;
	
begin	
	
	A: for i in 0 to 2**SELECT_BITS-1 generate
		w_data(i) <= i_data((i+1)*DATA_BITS-1 downto i*DATA_BITS);
	end generate;
	
	
	o_data <= w_data(to_integer(unsigned(i_select)));
	
end main;
-----------------------------------------------------------------------------	