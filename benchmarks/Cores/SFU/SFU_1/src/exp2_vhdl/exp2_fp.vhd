-- Proyecto				: EXPONENT BASE 2 IEEE754
-- Nombre de archivo	: exp2_fp.vhd
--	Titulo				: operacion exponencial base 2
-----------------------------------------------------------------------------	
-- Descripcion			: calcula la potencia en base de dos de un numero en
--							  formato IEEE754.
--
--		MANTISBITS 		: Numero de bits de la mantisa
--		EXPBITS			: Numero de bits del exponente
-- 	SEG				: Numero de segmentos utilizados para la aproximacion
--		SEGBITS			: Ancho del segmento
-- 	i_x				: Numero en formato numerico IEEE754
-- 	o_exp2			: Resultado en formato numerico IEEE754
-- 
-- Notas: 
--		las constantes correspondientes a los segmentos se encuentran en 
-- 	complemento a 2.
--		c_BX controla la cantidad de desplazamientos hacia la derecha para el
--		dato de entrada. Conforme se incrementa se aumenta la precision para
--		valores de entrada con exponente negativo, a su vez se incrementa el
--		numero de multiplexores para realizar el desplazamiento.
-----------------------------------------------------------------------------	
-- Universidad Pedagogica y Tecnologica de Colombia.
-- Facultad de ingenieria.
-- Escuela de ingenieria Electronica - extension Tunja.
-- 
-- Autor: Cristhian Fernando Moreno Manrique
-- Mayo 2020
-----------------------------------------------------------------------------	

library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;
	use work.log2_pkg.all;

	
entity exp2_fp is
	generic (MANTISBITS				: 		natural:= 23;		-- Formato IEEE754:
				EXPBITS					: 		natural:= 8;		-- signo[1] & exponente[8] & mantisa[23]
				SEG						:		natural:= 64;
				SEGBITS					:		natural:= 23);
	port 	  (i_x						: in	std_logic_vector(EXPBITS+MANTISBITS downto 0);
				o_exp2					: out std_logic_vector(EXPBITS+MANTISBITS downto 0));	
end entity;


architecture arch of exp2_fp is
	constant c_BX						: natural	:= 16;  -- %errormax: BX=16: 0.00105,  BX=12: 0.0169
	constant c_64seg_23b				: std_logic_vector(SEGBITS-1 downto 0) := "11111111111111101011101";
	constant c_log2_seg				: natural	:= f_log2(SEG);
	
	signal w_mantis	 				: std_logic_vector(MANTISBITS-1 downto 0);
	signal w_exp		 				: std_logic_vector(EXPBITS-1 downto 0);
	signal w_sgn 						: std_logic;
	
	signal w_exp_adj					: std_logic_vector(EXPBITS-2 downto 0); -- se ajusta segun el valor maximo calculable
	signal w_adderA_iterm1			: std_logic_vector(EXPBITS-2 downto 0);
	signal w_adderA					: std_logic_vector(EXPBITS-2 downto 0);
	signal w_mantis_adj				: std_logic_vector(c_BX+EXPBITS+MANTISBITS-2 downto 0);
	signal w_lshifter					: std_logic_vector(w_mantis_adj'left downto 0);
	signal w_lshifter_ishifts		: std_logic_vector(f_log2(w_mantis_adj'length)-1 downto 0);
	signal w_c1_lshifter				: std_logic_vector(EXPBITS+MANTISBITS-2 downto 0);
	
	signal w_adderB					: std_logic_vector(EXPBITS-2 downto 0);
	signal w_comp_EQexp				: std_logic;
	signal w_exp_MSB_result			: std_logic;
	
	signal w_ctrl_seg					: std_logic;	
	signal w_addr_lutA				: std_logic_vector(c_log2_seg-2 downto 0);
	signal w_adderC					: std_logic_vector(c_log2_seg-2 downto 0);
	signal w_lutA						: std_logic_vector(SEGBITS-1 downto 0);
	signal w_comp_EQseg				: std_logic;
	signal w_muxA_idata				: std_logic_vector(2*SEGBITS-1 downto 0);
	--signal w_muxA_isel 				: std_logic_vector(0 downto 0);
	signal w_muxA 						: std_logic_vector(SEGBITS-1 downto 0);
	signal w_addr_lutB				: std_logic_vector(c_log2_seg-2 downto 0);
	signal w_lutB						: std_logic_vector(SEGBITS-1 downto 0);
	
	signal w_comp_ctrlsubs			: std_logic;
	signal w_xor_comp_ctrlsubs		: std_logic;
	signal w_nxor_comp_ctrlsubs	: std_logic;
	signal w_C1_muxA					: std_logic_vector(SEGBITS-1 downto 0);
	signal w_C1_lutB					: std_logic_vector(SEGBITS-1 downto 0);
	signal w_adderE					: std_logic_vector(SEGBITS-1 downto 0);
	
	signal w_muxB_idata				: std_logic_vector(2*SEGBITS-1 downto 0);
	--signal w_muxB_iselect			: std_logic_vector(0 downto 0);
	signal w_muxB						: std_logic_vector(SEGBITS-1 downto 0);
	signal w_adderD					: std_logic_vector(SEGBITS-1 downto 0);
	signal w_adderD_cout				: std_logic;
	signal w_slf_segx					: std_logic_vector(MANTISBITS-1 downto 0); -- (s*lf - segx)
	signal w_mult						: std_logic_vector(MANTISBITS*2-1 downto 0);
	signal w_C1_mult_idata			: std_logic_vector(MANTISBITS+1 downto 0);
	signal w_C1_mult					: std_logic_vector(w_C1_mult_idata'left downto 0);
	signal w_adderF_iterm1			: std_logic_vector(w_C1_mult_idata'left downto 0);
	signal w_adderF					: std_logic_vector(w_C1_mult_idata'left downto 0);
	
	signal mantis_result				: std_logic_vector(MANTISBITS-1 downto 0);
	signal exp_result 				: std_logic_vector(EXPBITS-1 downto 0);
	signal sgn_result					: std_logic;
	
	signal w_ieeecase					: std_logic_vector(i_x'left downto 0);
	signal w_case_en					: std_logic_vector(1 downto 0);
	signal w_mux_case_idata 		: std_logic_vector(i_x'length*2-1 downto 0);
	signal w_mux_case 				: std_logic_vector(i_x'left downto 0);
begin

	w_mantis								<= i_x(MANTISBITS-1 downto 0);
	w_exp									<= i_x(MANTISBITS+EXPBITS-1 downto MANTISBITS);
	w_sgn									<= i_x(MANTISBITS+EXPBITS);
	

	--------------------------------------------------------------------------	
	-- < Ajuste de dato >
	--------------------------------------------------------------------------	
	
	w_exp_adj							<= w_exp(w_exp_adj'left downto 0);
	w_adderA_iterm1					<= w_exp_adj;

	adderA 								:	entity work.sum_ripple_carry_adder 
	generic map(WIDE					=> EXPBITS-1,
				C1 => 0)
	port map   (i_term1				=> w_adderA_iterm1,
					i_term2 				=> std_logic_vector(to_unsigned(c_BX, EXPBITS-1)),
					i_cin					=> '1',
					o_sum					=> w_adderA);	

	w_mantis_adj						<= std_logic_vector(to_unsigned(0, c_BX)) & std_logic_vector(to_unsigned(1, EXPBITS-1)) & w_mantis;
	w_lshifter_ishifts				<= w_adderA(f_log2(w_mantis_adj'length)-1 downto 0);
	
	lshifter								: entity work.left_shifter
	generic map(DATA_BITS			=> w_mantis_adj'length)
	port map	  (i_data				=> w_mantis_adj,
					i_shifts				=> w_lshifter_ishifts,
					o_dataShift			=> w_lshifter);

	ones_complement_lshifter		: entity work.ones_complement
	generic map(WIDE					=>	w_c1_lshifter'length)
	port map	  (i_data				=> w_lshifter(c_BX+MANTISBITS+EXPBiTS-2 downto c_BX),
					i_en					=> w_sgn,
					o_data				=> w_c1_lshifter);


	--------------------------------------------------------------------------	
	-- < calculo de esxponente >
	--------------------------------------------------------------------------	

	adderB								:entity work.sum_ripple_carry_adder 
	generic map(WIDE					=> EXPBITS-1,
					C1						=> 2) 
	port map   (i_term1				=> w_c1_lshifter(w_c1_lshifter'left downto MANTISBITS),
					i_term2 				=> std_logic_vector(to_unsigned(1, EXPBITS-1)),
					i_cin					=> '1',
					o_sum					=> w_adderB);	
					
	comparator_EQexponent			: entity work.comparator
	generic map(WIDE 					=> w_exp'length,
					MODO					=> 1)
	port map	  (i_data1				=> w_exp,
					i_data2				=> std_logic_vector(to_unsigned(126, w_exp'length)),
					o_result				=> w_comp_EQexp);

	w_exp_MSB_result					<= w_comp_EQexp and not(w_sgn);


	--------------------------------------------------------------------------	
	-- < Seleccion de constantes >
	--------------------------------------------------------------------------	
	
	w_addr_lutA							<= w_c1_lshifter(w_mantis'left downto w_mantis'left-c_log2_seg+2);
	w_addr_lutB							<= w_c1_lshifter(w_mantis'left downto w_mantis'left-c_log2_seg+2);
	w_ctrl_seg							<= w_c1_lshifter(w_mantis'left-c_log2_seg+1);
	
	adderC								:	entity work.sum_ripple_carry_adder 
	generic map(WIDE					=> c_log2_seg-1,
				C1 => 0)
	port map   (i_term1				=> w_addr_lutA,
					i_term2 				=> std_logic_vector(to_unsigned(0, c_log2_seg-1)),
					i_cin					=> w_ctrl_seg,
					o_sum					=> w_adderC);	
	
--	LUT32C: if SEG = 32 generate
--		LUT32_23b							: luts_32x23b
--		port map	  (i_lutA_addr			=> w_adderC,
--						i_lutB_addr			=> w_addr_lutB,
--						o_lutA				=> w_lutA,
--						o_lutB				=> w_lutB);
--	end generate;

	LUT64C: if SEG = 64 generate
		LUT64_23b							: entity work.exp2_luts_64x23b
		generic map(SEG => SEG)
		port map	  (i_lutA_addr			=> w_adderC,
						i_lutB_addr			=> w_addr_lutB,
						o_lutA				=> w_lutA,
						o_lutB				=> w_lutB);
	end generate;	
	
	comparator_EQsegments			: entity work.comparator
	generic map(WIDE 					=> c_log2_seg,
					MODO					=> 0)
	port map	  (i_data1				=> w_c1_lshifter(w_mantis'left downto MANTISBITS-c_log2_seg),
					i_data2				=> std_logic_vector(to_unsigned(SEG-1, c_log2_seg)),
					o_result				=> w_comp_EQseg);
  	
   --w_muxA_idata						<= c_64seg_23b & w_lutA;
 	--w_muxA_isel							<= w_comp_EQseg & std_logic_vector(to_unsigned(0, 0));  -- entidad mux requiere que el dato siempre sea std_logic_vector
 	
--  	mux_lutA									: mux
--	generic map(SELECT_BITS			=> 1, 
--					DATA_BITS			=> SEGBITS)
--	port map	  (i_data 				=> w_muxA_idata,
--					i_select				=> w_muxA_isel, 	
--					o_data				=>	w_muxA);	
	
w_muxA <= w_lutA when w_comp_EQseg='0' else c_64seg_23b;
	--------------------------------------------------------------------------
	-- < control resta de constantes >
	--------------------------------------------------------------------------

	comparator_control_lut			:	entity work.comparator
	generic map(WIDE					=> c_log2_seg,
					MODO					=>	2)
	port map	  (i_data1				=> w_c1_lshifter(w_mantis'left downto MANTISBITS-c_log2_seg),
					i_data2				=> std_logic_vector(to_unsigned(34, c_log2_seg)), -- constante solo funciona para 64 segmentos 
					o_result				=>	w_comp_ctrlsubs);
	
	w_xor_comp_ctrlsubs				<= w_comp_ctrlsubs xor w_c1_lshifter(MANTISBITS-c_log2_seg);
	w_nxor_comp_ctrlsubs				<= not(w_xor_comp_ctrlsubs);
	
	ones_complement_muxA				: entity work.ones_complement
	generic map(WIDE					=>	SEGBITS)
	port map	  (i_data				=> w_muxA,
					i_en					=> w_nxor_comp_ctrlsubs,
					o_data				=> w_C1_muxA);
	
	ones_complement_lutB				: entity work.ones_complement
	generic map(WIDE					=>	SEGBITS)
	port map	  (i_data				=> w_lutB,
					i_en					=> w_xor_comp_ctrlsubs,
					o_data				=> w_C1_lutB);
	
	constants_sub						:	entity work.sum_ripple_carry_adder
	generic map(WIDE					=> SEGBITS,
				C1 => 0)
	port map   (i_term1				=> w_C1_muxA,
					i_term2 				=> w_C1_lutB,
					i_cin					=> '1',
					o_sum					=> w_adderE);
					

	--------------------------------------------------------------------------
	-- < Calculo de mantisa >
	--------------------------------------------------------------------------

	w_muxB_idata						<= w_lutB & w_muxA;
	--w_muxB_iselect						<= w_ctrl_seg & std_logic_vector(to_unsigned(0, 0));  -- entidad mux requiere que el dato siempre sea del tipo std_logic_vector
	
--	muxB									: mux
--	generic map(SELECT_BITS			=> 1, 
--					DATA_BITS			=> SEGBITS)
--	port map	  (i_data 				=> w_muxB_idata,
--					i_select				=> w_muxB_iselect, 	
--					o_data				=>	w_muxB);
w_muxB <= w_muxA when w_ctrl_seg='0' else w_lutB;
	
	adderD								: entity work.sum_ripple_carry_adder
	generic map(WIDE					=> SEGBITS,
				C1 => 0)
	port map	  (i_term1				=> w_muxB,
					i_term2 				=> w_c1_lshifter(w_mantis'left downto 0),
					i_cin					=> '0',
					o_sum					=> w_adderD,
					o_cout				=> w_adderD_cout);	
	
	w_slf_segx							<= w_c1_lshifter(MANTISBITS-c_log2_seg-1 downto 0) & std_logic_vector(to_unsigned(0, c_log2_seg));
	
	multiplier							: entity work.mult
	generic map(WIDE					=> SEGBITS)
	port map	  (i_term1 				=> w_adderE,
					i_term2				=> w_slf_segx,
					o_product			=> w_mult);
	
	w_C1_mult_idata					<= w_mult(MANTISBITS*2-1 downto MANTISBITS-2);
	
	ones_complement_mult				: entity work.ones_complement
	generic map(WIDE					=>	w_C1_mult_idata'length)
	port map	  (i_data				=> w_C1_mult_idata,
					i_en					=> w_comp_ctrlsubs,
					o_data				=> w_C1_mult);
	
	w_adderF_iterm1					<= w_adderD & "00";	
	
	adderF								: entity work.sum_ripple_carry_adder
	generic map(WIDE					=> w_C1_mult'length,
				C1 => 0)
	port map	  (i_term1				=> w_adderF_iterm1,
					i_term2 				=> w_C1_mult,
					i_cin					=> w_comp_ctrlsubs,
					o_sum					=> w_adderF,
					o_cout				=> open);
					
	--------------------------------------------------------------------------
	-- < deteccion de caso ieee>
	--------------------------------------------------------------------------
	sgn_result						<= '0';
	exp_result						<= w_exp_MSB_result  & w_adderB;
	mantis_result					<= w_adderF(w_adderF'left downto w_adderF'left-MANTISBITS+1); 
	
	ieee32_case							: entity work.exp2_ieee
	generic map(BX 					=> c_BX)
	port map	  (i_data 				=> i_x,
					o_case				=> w_ieeecase,
					o_case_en			=> w_case_en(0));

	w_mux_case_idata					<= w_ieeecase & sgn_result & exp_result & mantis_result;

--	mux_ieee32_case					: mux
--	generic map(SELECT_BITS			=> 1,
--					DATA_BITS			=> i_x'length)
--	port map	  (i_data 				=> w_mux_case_idata,
--					i_select				=> w_case_en,
--					o_data 				=> w_mux_case);


w_mux_case <= sgn_result & exp_result & mantis_result when w_case_en(0)='0' else w_ieeecase;
	--------------------------------------------------------------------------
	-- < RESULTADO >
	--------------------------------------------------------------------------	

	o_exp2								<= w_mux_case ;


end arch;