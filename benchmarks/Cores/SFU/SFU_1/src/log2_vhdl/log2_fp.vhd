-- Proyecto				: LOG2 IEEE754
-- Nombre de archivo	: log2_fp.vhd
--	Titulo				: operacion logaritmo en base 2
-----------------------------------------------------------------------------	
-- Descripcion			: calcula el logaritmo en base de dos de un numero en
--							  formato IEEE754.
--
--		MANTISBITS 		: Numero de bits de la mantisa
--		EXPBITS			: Numero de bits del exponente
-- 	SEG				: Numero de segmentos utilizados para la aproximacion
--		SEGBITS			: Ancho del segmento
-- 	i_x				: Numero en formato numerico IEEE754
-- 	o_log2			: Resultado en formato numerico IEEE754
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
	use work.log2_pkg.all;

	
entity log2_fp is
	generic (MANTISBITS				: 		natural:= 23;		-- Formato IEEE754:
				EXPBITS					: 		natural:= 8;		-- signo[1] & exponente[8] & mantisa[23]
				SEG						:		natural:= 64;
				SEGBITS					:		natural:= 23);
	port 	  (i_x						: in	std_logic_vector(EXPBITS+MANTISBITS downto 0);
				o_log2					: out std_logic_vector(EXPBITS+MANTISBITS downto 0));
end entity;


architecture rtl of log2_fp is
	
	constant c_64seg_23b				: std_logic_vector(SEGBITS-1 downto 0) := "00000000000000000111101";
	constant c_log2_seg				: natural	:= f_log2(SEG);
	
	signal w_mantis	 				: std_logic_vector(MANTISBITS-1 downto 0);
	signal w_exp		 				: std_logic_vector(EXPBITS-1 downto 0);
	signal w_sgn 						: std_logic;

	signal w_segment_ctrl			: std_logic;
	signal w_lutA_addr				: std_logic_vector(c_log2_seg-2 downto 0);
	signal w_lutA_adder				: std_logic_vector(c_log2_seg-2 downto 0);
	signal w_lutA						: std_logic_vector(SEGBITS-1 downto 0);
	signal w_comp_EQseg				: std_logic;
	signal w_mux_lutA_idata			: std_logic_vector(2*SEGBITS-1 downto 0);
	--signal w_mux_lutA_isel			: std_logic_vector(0 downto 0);
	signal w_mux_lutA 				: std_logic_vector(SEGBITS-1 downto 0);
	signal w_lutB_addr				: std_logic_vector(c_log2_seg-2 downto 0);
	signal w_lutB						: std_logic_vector(SEGBITS-1 downto 0);
	
	signal w_comp_C1_ctrl			: std_logic;
	signal w_comp_C1_ctrl_n 		: std_logic;
	signal w_comp_C1_ctrl_xor		: std_logic;
	signal w_comp_C1_ctrl_xnor		: std_logic;
	signal w_mux_lutA_C1				: std_logic_vector(SEGBITS-1 downto 0);
	signal w_lutB_C1					: std_logic_vector(SEGBITS-1 downto 0);
	signal w_constants_sub			: std_logic_vector(SEGBITS-1 downto 0);
	
	signal w_muxA_idata				: std_logic_vector(2*SEGBITS-1 downto 0);
	--signal w_muxA_iselect			: std_logic_vector(0 downto 0);
	signal w_muxA						: std_logic_vector(SEGBITS-1 downto 0);
	signal w_adderB					: std_logic_vector(SEGBITS-1 downto 0); -- generalizar entradas
	signal w_adderB_cout				: std_logic;
	signal w_mantis_decimal			: std_logic_vector(MANTISBITS-1 downto 0);
	signal w_mult						: std_logic_vector(MANTISBITS*2-1 downto 0);
	signal w_mult_C1_idata			: std_logic_vector(MANTISBITS+2 downto 0);
	signal w_mult_C1					: std_logic_vector(MANTISBITS+2 downto 0);
	signal w_adderC_iterm1			: std_logic_vector(MANTISBITS+2 downto 0);
	signal w_adderC					: std_logic_vector(MANTISBITS+2 downto 0);
	
	signal w_exp_comp					: std_logic;
	signal w_exp_ncomp				: std_logic;
	signal w_adderD					: std_logic_vector(EXPBITS-2 downto 0);
	signal w_adderD_C1				: std_logic_vector(EXPBITS-2 downto 0);
	signal w_adderC_C1_idata		: std_logic_vector(MANTISBITS+EXPBITS downto 0);
	signal w_adderC_C1				: std_logic_vector(MANTISBITS+EXPBITS downto 0);
	signal w_adderE_iterm2			: std_logic_vector(MANTISBITS+EXPBITS downto 0);
	signal w_adderE					: std_logic_vector(MANTISBITS+EXPBITS downto 0);
	signal w_adderE_cout				: std_logic;
	signal w_CLZ						: std_logic_vector(f_log2(MANTISBITS)-1 downto 0);
	signal w_CLZ_MSB					: std_logic;

	signal w_CLZ_adj					: std_logic_vector(EXPBITS-2 downto 0);
	signal w_adderE_shift			: std_logic_vector(w_adderE'left downto 0);
	signal w_adderF					: std_logic_vector(EXPBITS-2 downto 0);
	signal w_coutF						: std_logic;
	
	signal w_mantis_result			: std_logic_vector(MANTISBITS-1 downto 0);
	signal w_exp_result 				: std_logic_vector(EXPBITS-1 downto 0);
	signal w_sgn_result				: std_logic;
	
	signal w_ieeecase					: std_logic_vector(i_x'left downto 0);
	signal w_ieeecase_en				: std_logic;
	signal w_mux_case_idata			: std_logic_vector(i_x'length*2-1 downto 0);
	signal w_mux_case					: std_logic_vector(i_x'left downto 0);
	
begin

	w_mantis								<= i_x(MANTISBITS-1 downto 0);
	w_exp									<= i_x(MANTISBITS+EXPBITS-1 downto MANTISBITS);
	w_sgn									<= i_x(MANTISBITS+EXPBITS);
	
	
	--------------------------------------------------------------------------	
	-- < Seleccion de constantes >
	--------------------------------------------------------------------------	
	
	w_lutA_addr							<= w_mantis(w_mantis'left downto w_mantis'left-c_log2_seg+2);
	w_lutB_addr							<= w_mantis(w_mantis'left downto w_mantis'left-c_log2_seg+2);
	w_segment_ctrl						<= w_mantis(w_mantis'left-c_log2_seg+1);
	
	adder_lutA							:	entity work.sum_ripple_carry_adder 
	generic map(WIDE					=> c_log2_seg-1)
	port map   (i_term1				=> w_lutA_addr,
					i_term2 				=> std_logic_vector(to_unsigned(0, c_log2_seg-1)),
					i_cin					=> w_segment_ctrl,
					o_sum					=> w_lutA_adder);	
	
--	LUT32C: if SEG = 32 generate
--		LUT32_23b							: log2_luts_32x23b
--		port map	  (i_lutA_addr			=> w_lutA_adder,
--						i_lutB_addr			=> w_lutB_addr,
--						o_lutA				=> w_lutA,
--						o_lutB				=> w_lutB);
--	end generate;

	LUT64C: if SEG = 64 generate
		LUT64_23b							: entity work.log2_luts_64x23b
		generic map(SEG=>SEG)
		port map	  (i_lutA_addr			=> w_lutA_adder,
						i_lutB_addr			=> w_lutB_addr,
						o_lutA				=> w_lutA,
						o_lutB				=> w_lutB);
	end generate;	
	
	comparator_EQsegments			: entity work.comparator
	generic map(WIDE 					=> c_log2_seg,
					MODO					=> 0)
	port map	  (i_data1				=> w_mantis(w_mantis'left downto MANTISBITS-c_log2_seg),
					i_data2				=> std_logic_vector(to_unsigned(SEG-1, c_log2_seg)),
					o_result				=> w_comp_EQseg);
  	
   --w_mux_lutA_idata					<= c_64seg_23b & w_lutA;
 	--w_mux_lutA_isel(0)					<= w_comp_EQseg & std_logic_vector(to_unsigned(0, 0));  -- entidad mux requiere que el dato siempre sea std_logic_vector
 	
	
--  	mux_lutA									: mux
--	generic map(SELECT_BITS			=> 1, 
--					DATA_BITS			=> SEGBITS)
--	port map	  (i_data 				=> w_mux_lutA_idata,
--					i_select				=> w_mux_lutA_isel(0), 	
--					o_data				=>	w_mux_lutA);	
	
	w_mux_lutA <= w_lutA when w_comp_EQseg='0' else c_64seg_23b;
	
	--------------------------------------------------------------------------
	-- < control resta de constantes >
	--------------------------------------------------------------------------
	
	comparator_control_lut			:	entity work.comparator
	generic map(WIDE					=> c_log2_seg,
					MODO					=>	2)
	port map	  (i_data1				=> w_mantis(w_mantis'left downto MANTISBITS-c_log2_seg),
					i_data2				=> std_logic_vector(to_unsigned(SEG*7/16, c_log2_seg)), -- 
					o_result				=>	w_comp_C1_ctrl);
	
	w_comp_C1_ctrl_n 					<= not(w_comp_C1_ctrl);
	w_comp_C1_ctrl_xor				<= w_comp_C1_ctrl_n xor w_mantis(MANTISBITS-c_log2_seg);
	w_comp_C1_ctrl_xnor				<= not(w_comp_C1_ctrl_xor);
	
	ones_complement_lutA				: entity work.ones_complement
	generic map(WIDE					=>	w_mux_lutA'length)
	port map	  (i_data				=> w_mux_lutA,
					i_en					=> w_comp_C1_ctrl_xnor,
					o_data				=> w_mux_lutA_C1);
	
	ones_complement_lutB				: entity work.ones_complement
	generic map(WIDE					=>	MANTISBITS)
	port map	  (i_data				=> w_lutB,
					i_en					=> w_comp_C1_ctrl_xor,
					o_data				=> w_lutB_C1);
	
	constants_sub						:	entity work.sum_ripple_carry_adder
	generic map(WIDE					=> MANTISBITS)
	port map   (i_term1				=> w_mux_lutA_C1,
					i_term2 				=> w_lutB_C1,
					i_cin					=> '1',
					o_sum					=> w_constants_sub);
					
					
	--------------------------------------------------------------------------
	-- < Calculo de parte fraccionaria >
	--------------------------------------------------------------------------
	
	--w_muxA_idata						<= w_lutB & w_mux_lutA;
	--w_muxA_iselect						<= w_segment_ctrl & std_logic_vector(to_unsigned(0, 0));  -- entidad mux requiere que el dato siempre sea std_logic_vector
	
--	muxA									: mux
--	generic map(SELECT_BITS			=> 1, 
--					DATA_BITS			=> MANTISBITS)
--	port map	  (i_data 				=> w_muxA_idata,
--					i_select				=> w_muxA_iselect, 	
--					o_data				=>	w_muxA);
					
w_muxA <= w_mux_lutA when w_segment_ctrl='0' else w_lutB;
	
	adderB								: entity work.sum_ripple_carry_adder
	generic map(WIDE					=> MANTISBITS)
	port map	  (i_term1				=> w_muxA,
					i_term2 				=> w_mantis,
					i_cin					=> '0',
					o_sum					=> w_adderB,
					o_cout				=> w_adderB_cout);	
	
	w_mantis_decimal					<= w_mantis(MANTISBITS-c_log2_seg-1 downto 0) & std_logic_vector(to_unsigned(0, c_log2_seg));
	
	multiplier							: entity work.mult
	generic map(WIDE					=> MANTISBITS)
	port map	  (i_term1 				=> w_constants_sub,
					i_term2				=> w_mantis_decimal,
					o_product			=> w_mult);
	
	w_mult_C1_idata					<= "0" & w_mult(MANTISBITS*2-1 downto MANTISBITS-2); -- se añade una parte entera al resultado
	
	ones_complement_mult				: entity work.ones_complement
	generic map(WIDE					=>	w_mult_C1_idata'length)
	port map	  (i_data				=> w_mult_C1_idata,
					i_en					=> w_comp_C1_ctrl_n,
					o_data				=> w_mult_C1);
	
	w_adderC_iterm1					<= w_adderB_cout & w_adderB & "00";	
	
	adderC								: entity work.sum_ripple_carry_adder
	generic map(WIDE					=> w_adderC_iterm1'length,
				C1 => 0)
	port map	  (i_term1				=> w_adderC_iterm1,
					i_term2 				=> w_mult_C1,
					i_cin					=> w_comp_C1_ctrl_n,
					o_sum					=> w_adderC);
					
					
	--------------------------------------------------------------------------
	-- < calculo de resultado en punto fijo >
	--------------------------------------------------------------------------	
	
	exp_comparator				:	entity work.comparator
	generic map(WIDE					=> EXPBITS,
					MODO					=> 1)
	port map	  (i_data1				=> std_logic_vector(to_unsigned(2**(EXPBITS-1)-1, EXPBITS)),
					i_data2				=> w_exp,
					o_result				=>	w_exp_comp);
	
	w_exp_ncomp							<= not(w_exp_comp);
	
	adderD								: entity work.sum_ripple_carry_adder
	generic map(WIDE					=> EXPBITS-1,
				C1 => 0)
	port map	  (i_term1				=> w_exp(w_exp'left-1 downto 0),
					i_term2 				=> std_logic_vector(to_unsigned(0, EXPBITS-1)),
					i_cin					=> w_exp_ncomp,
					o_sum					=> w_adderD);
	
	ones_complement_adderD			: entity work.ones_complement
	generic map(WIDE					=> w_adderD'length)
	port map   (i_data				=> w_adderD,
					i_en					=> w_exp_comp,
					o_data				=> w_adderD_C1);
	
	w_adderC_C1_idata					<=  std_logic_vector(to_unsigned(0, EXPBITS-2)) & w_adderC;
	
	ones_complement_adderC			: entity work.ones_complement
	generic map(WIDE					=> w_adderC_C1_idata'length)
	port map   (i_data				=> w_adderC_C1_idata,
					i_en					=> w_exp_comp,
					o_data				=> w_adderC_C1);
	
	w_adderE_iterm2					<= w_adderD_C1 & std_logic_vector(to_unsigned(0, MANTISBITS+2));
	
	adderE								: entity work.sum_ripple_carry_adder
	generic map(WIDE					=> w_adderC_C1'length,
				C1 => 0)
	port map	  (i_term1				=> w_adderC_C1,
					i_term2 				=> w_adderE_iterm2,
					i_cin					=> w_exp_comp,
					o_sum					=> w_adderE);
					
					
	--------------------------------------------------------------------------
	-- < calculo de resultado en punto flotante >
	--------------------------------------------------------------------------
	
	leading_zeros						: entity work.CLZ
	generic map(MODE => '0',
				DATA_BITS			=> 2**f_log2(w_adderE'length)) -- el modulo solo acepta un ancho de datos 2^x
	port map	  (i_data				=> w_adderE,
					o_zeros				=> w_CLZ,
					o_MSB_zeros			=>	w_CLZ_MSB);	
	
	shifter								: entity work.left_shifter
	generic map(DATA_BITS			=> w_adderE'length)
	port map	  (i_data				=> w_adderE,
					i_shifts				=> w_CLZ,
					o_dataShift			=> w_adderE_shift);
	
	w_CLZ_adj							<= "00" & w_CLZ; -- se añaden ceros segun la cantidad de bits del exponente
	
	adderF								: entity work.sum_ripple_carry_adder
	generic map(WIDE					=> EXPBITS-1, 
					C1						=> 1) -- complemento a 1
	port map	  (i_term1				=> w_CLZ_adj,
					i_term2 				=> "0000110",	-- cte encontrada experimentalmente
					i_cin					=> '0',
					o_sum					=> w_adderF,
					o_cout				=> w_coutF);
	
	
	--------------------------------------------------------------------------
	-- < deteccion de caso ieee>
	--------------------------------------------------------------------------
	
	w_sgn_result						<= w_exp_comp;
	w_exp_result						<= w_coutF  & w_adderF;
	w_mantis_result					<= w_adderE_shift(w_adderE_shift'left-1 downto w_adderE_shift'left-MANTISBITS); 
	
	case_ieee32							: entity work.log2_ieee
	port map	  (i_data				=> i_x,
					o_case				=> w_ieeecase,
					o_case_en			=> w_ieeecase_en);			
	
	--w_mux_case_idata					<= w_ieeecase & w_sgn_result & w_exp_result & w_mantis_result;
	
--	mux_case_select					: mux
--	generic map(SELECT_BITS			=> 1, 
--					DATA_BITS			=> i_x'length)
--	port map	  (i_data 				=> w_mux_case_idata,
--					i_select				=> w_ieeecase_en, 	
--					o_data				=>	w_mux_case);
	
	w_mux_case <= w_sgn_result & w_exp_result & w_mantis_result when w_ieeecase_en='0' else w_ieeecase;
	
	o_log2								<= w_mux_case;
	
end rtl;