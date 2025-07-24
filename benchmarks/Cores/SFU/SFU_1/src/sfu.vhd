-- Proyecto				: SFU IEEE754
-- Nombre de archivo	: SFU.vhd
-- Titulo				: Special Function Unit  
-----------------------------------------------------------------------------	
-- Descripcion			: This unit performs the floating point operations
--						  sin(x), cos(x), rsqrt(x), log2(x) and exp2(x) using
--						IEE754 standard and operational compliant with GPU G80
--						architecture
--
-----------------------------------------------------------------------------	
-- Universidad Pedagogica y Tecnologica de Colombia.
-- Facultad de ingenieria.
-- Escuela de ingenieria Electronica - extension Tunja.
-- 
-- Autor: Cristhian Fernando Moreno Manrique
-- Abril 2020
-----------------------------------------------------------------------------	


library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;


entity sfu is
port(clk_i	  :in std_logic;	--input clock
	 rst_n	  :in std_logic;	--reset active low
	 start_i  :in std_logic;	--start operation
	 src1_i	  :in std_logic_vector(31 downto 0); --IEE754 input data
	 selop_i  :in std_logic_vector(2 downto 0); --operation selection
	 Result_o :out std_logic_vector(31 downto 0); --IEE754 result data output
	 stall_o  :out std_logic --stall signal 
);
end entity sfu;


architecture structure of sfu is 
signal sin_res, cos_res, rsqrt_res,log2_res,exp2_res :std_logic_vector(31 downto 0);
signal start_cordic,ready_cordic, cordic_sel,ff_ready_cordic :std_logic;

begin 
--oparators intance
Cordic_inst: entity work.cordic
	port map(iClk	  => clk_i,
			 iReset	  => rst_n,
	         istart	  => start_cordic,
	         iEntrada => src1_i,
	         oSalida1 => cos_res,
	         oSalida2 => sin_res,
	         oready	  => ready_cordic);

			 
rsqrt_ints: entity work.rsqrt
	port map(i_x	 => src1_i,	
	         o_rsqrt => rsqrt_res);
			 
 log2_inst: entity work.log2_fp
	port map(i_x	=> src1_i,	
	         o_log2	=> log2_res);
			 
 exp2_inst: entity work.exp2_fp
	port map(i_x	=> src1_i,	
	         o_exp2	=> exp2_res);		 
--stall control
cordic_sel <= selop_i(2) nor selop_i(1);
start_cordic <= cordic_sel and start_i;

ff_d: process(clk_i,rst_n)
	begin
		if(rst_n='0') then
			ff_ready_cordic <= '0';
		elsif rising_edge(clk_i) then
			ff_ready_cordic <= ready_cordic;
		end if;
	end process;
	
stall_o <= cordic_sel and ((not ready_cordic) or ff_ready_cordic);


--output multiplexer

with selop_i select
	Result_o <= sin_res 	when "000",
				cos_res 	when "001",
				rsqrt_res 	when "010",
				log2_res	when "011",
				exp2_res	when "100",
				src1_i		when others;
end structure;