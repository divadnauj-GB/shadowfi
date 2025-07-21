-- Nombre de archivo	: left_shifter.vhd
--	Titulo				: desplazador a la izquierda 
-----------------------------------------------------------------------------	
-- Descripcion			: Desplaza el dato a la izquierda segun el numero de
--							  desplazamientos indicado. El costado derecho se
--							  rellena con ceros. Segun el ancho del dato se calcula
--							  el total de desplazamientos y los bits del dato de salida:
--									DATA_BITS =23
--									i_data[22:0]
--									i_shifts[4:0]
--									o_dataShift[31:0]
--							  Para realizar el desplazamiento se utilizan multiplexores,
--							  siguiendo el ejemplo anterior: 32 multiplexores.
--							  
--		DATA_BITS		: Ancho del dato a desplazar
-- 	i_data			: Dato a desplazar
-- 	i_shifts			: Numero de desplazamientos
-- 	o_data			: Dato desplazado
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
	use work.log2_pkg.all;

	
entity left_shifter is 

	generic (DATA_BITS					: 		natural := 5);	-- Result[31:1] & cout
	port	  (i_data						: in	std_logic_vector(DATA_BITS-1 downto 0);
				i_shifts						: in	std_logic_vector(f_log2(DATA_BITS)-1 downto 0);
				o_dataShift					: out std_logic_vector(DATA_BITS-1 downto 0));
end entity;
-----------------------------------------------------------------------------				

architecture main of left_shifter is	
	type shift_data is array(0 to 2**f_log2(DATA_BITS)-1) of std_logic_vector(2**f_log2(DATA_BITS)-1 downto 0);
	signal w_mx_input	: shift_data;
begin	
	
	
	DN: process(i_data)
	begin
		for i in 0 to 2**f_log2(DATA_BITS)-1 loop
			if(i<(DATA_BITS)) then
				w_mx_input(0)(i) <= i_data(i);
			else
				w_mx_input(0)(i) <= '0';
			end if;
		end loop;
	end process DN;
	
	
	
	MUXi: for i in 1 to 2**f_log2(DATA_BITS)-1 generate
		w_mx_input(i)<= w_mx_input(i-1)(2**f_log2(DATA_BITS)-2 downto 0) & '0';
	end generate MUXi;


	
	-- se genera una cantidad de mux igual al numero de bits del dato de entrada
	
	MX: for i in 0 to o_dataShift'left generate		
			-- mux_shifter1					: mux
			-- generic map(SELECT_BITS 	=> i_shifts'length,
							-- DATA_BITS		=> 1)
			-- port map	  (i_data			=>	w_mx_input(i),
							-- i_select			=> i_shifts,
							-- o_data			=> o_dataShift(i downto i));
		o_dataShift(i) <= w_mx_input(to_integer(unsigned(i_shifts)))(i);
							
	end generate MX;
	
end main;