LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;
USE IEEE.numeric_std.all;

ENTITY cordic IS
	PORT(
			iClk		:in		std_logic;
			iReset		:in 	std_logic;
			istart		:in		std_logic;
			iEntrada	:in 	std_logic_vector(31 downto 0);
			oSalida1	:out	std_logic_vector(31 downto 0);
			oSalida2	:out	std_logic_vector(31 downto 0);
			oready		:out	std_logic
		);             
END cordic;

ARCHITECTURE RTL OF cordic IS
type estados is(s0,s1);
signal ep,ns:estados;

type memoria is array(0 to 19) of std_logic_vector(31 downto 0);

constant	Angulo  : memoria :=(
X"3F490FDB",
X"3EED6338",
X"3E7ADBB0",
X"3DFEADD5",
X"3D7FAADE",
X"3CFFEAAE",
X"3C7FFAAB",
X"3BFFFEAB",
X"3B7FFFAB",
X"3AFFFFEB",
X"3A7FFFFB",
X"39FFFFFF",
X"39800000",
X"39000000",
X"38800000",
X"38000000",
X"37800000",
X"37000000",
X"36800000",
X"36000000");

constant	Constante  : memoria :=(
X"3F800000",
X"3F000000",
X"3E800000",
X"3E000000",
X"3D800000",
X"3D000000",
X"3C800000",
X"3C000000",
X"3B800000",
X"3B000000",
X"3A800000",
X"3A000000",
X"39800000",
X"39000000",
X"38800000",
X"38000000",
X"37800000",
X"37000000",
X"36800000",
X"36000000");

signal X,Y,Z :std_logic_vector(31 downto 0);
signal xsub,yadd,zsub :std_logic_vector(31 downto 0);
signal prodx,prody :std_logic_vector(31 downto 0);
signal di2_i,diangulo :std_logic_vector(31 downto 0);
signal counteri :std_logic_vector(4 downto 0);
signal selx,enx,sely,eny,selz,enz,seli,eni :std_logic;

signal w_case_cos: std_logic_vector(31 downto 0);
signal w_case_sin: std_logic_vector(31 downto 0);
signal w_case_en: std_logic;



BEGIN

FP_SUB_X: entity work.suma_resta
	port map(operando1   =>unsigned(X),
			operando2	 =>unsigned(prodx),
			operacion	 =>"0010",
			std_logic_vector(resultado)	 =>xsub);


FP_ADD_Y: entity work.suma_resta
	port map(operando1   =>unsigned(Y),
			operando2	 =>unsigned(prody),
			operacion	 =>"0001",
			std_logic_vector(resultado)	 =>yadd);
			
FP_SUB_Z: entity work.suma_resta
	port map(operando1   =>unsigned(Z),
			operando2	 =>unsigned(diangulo),
			operacion	 =>"0010",
			std_logic_vector(resultado)	 =>zsub);
			
FP_MUL_X: entity work.multFP
	port map(entrada_x  => Y,
			 entrada_y	=> di2_i,	 
			 salida     => prodx);
			 
FP_MUL_Y: entity work.multFP
	port map(entrada_x  => X,
			 entrada_y	=> di2_i,	 
			 salida     => prody);
			 

di2_i <= (Constante(to_integer(unsigned(counteri)))(31) xor Z(31))&(Constante(to_integer(unsigned(counteri)))(30 downto 0));
diangulo <= (Angulo(to_integer(unsigned(counteri)))(31) xor Z(31))&(Angulo(to_integer(unsigned(counteri)))(30 downto 0));


Xreg:process(iClk,iReset)
	begin
		if iReset='0' then
			X <= (others=>'0');
		elsif rising_edge(iClk) then
			if enx='1' then
				if selx='1' then
					if w_case_en = '1' then
						X <= w_case_cos;
					else
						if(unsigned(X(30 downto 23))=127 and unsigned(X(22 downto 0))=0) then
							X <= X"3f800000";
						else
							X <= xsub;
						end if;						
					end if;
				else
					X <= X"3f1b74ee";
				end if;
			end if;
		end if;
	end process Xreg;

Yreg:process(iClk,iReset)
	begin
		if iReset='0' then
			Y <= (others=>'0');
		elsif rising_edge(iClk) then
			if eny='1' then
				if sely='1' then
					if w_case_en = '1' then
						Y <= w_case_sin;
					else
						if(unsigned(Y(30 downto 23))=127 and unsigned(Y(22 downto 0))=0) then
							Y <= X"3f800000";
						else
							Y <= yadd;
						end if;
					end if;
				else
					Y <= (others=>'0');
				end if;
			end if;
		end if;
	end process Yreg;
	
	
Zreg:process(iClk,iReset)
	begin
		if iReset='0' then
			Z <= (others=>'0');
		elsif rising_edge(iClk) then
			if enz='1' then
				if selz='1' then
					Z <= zsub;
				else
					Z <= iEntrada;
				end if;
			end if;
		end if;
	end process Zreg;
	
ireg:process(iClk,iReset)
	begin
		if iReset='0' then
			counteri <= (others=>'0');
		elsif rising_edge(iClk) then
			if eni='1' then
				if seli='1' then
					counteri <= std_logic_vector(unsigned(counteri)+1);
				else
					counteri <= (others=>'0');
				end if;
			end if;
		end if;
	end process ireg;
	
FSM_NS:process(istart,ep,counteri,w_case_en)
	begin
		case ep is
			when s0 =>
				if istart='1' then
					ns <= s1;
				else
					ns <= s0;
				end if;
			when s1 =>
				if unsigned(counteri)=16 or w_case_en='1' then
					ns <= s0;
				else
					ns <= s1;
				end if;
			when others=>
				ns <= s0;
		end case;
	end process;
	
	
FSM_TS:process(iClk,iReset)
	begin
		if iReset='0' then
			ep <= s0;
		elsif rising_edge(iClk) then
			ep <= ns;
		end if;
	end process;
	
FSM_OUT:process(istart,ep,counteri,w_case_en)
	begin
		case ep is
			when s0 =>
				oready <= '1';
				if istart='1' then
					enx   <= '1';
					selx  <= '0';
					eny   <= '1';
					sely  <= '0';
					enz   <= '1';
					selz  <= '0';
					eni   <= '1';
					seli  <= '0';						
				else
					enx   <= '0';
					selx  <= '0';
					eny   <= '0';
					sely  <= '0';
					enz   <= '0';
					selz  <= '0';
					eni   <= '0';
					seli  <= '0';
				end if;
			when s1 =>
				oready <= '0';
				enx   <= '1';
				selx  <= '1';
				eny   <= '1';
				sely  <= '1';
				enz   <= '1';
				selz  <= '1';				
				if unsigned(counteri)=16 or w_case_en='1' then
					eni   <= '0';
					seli  <= '0';
				else
					eni   <= '1';
					seli  <= '1';
				end if;
			when others=>
				oready <= '0';
				enx   <= '0';
				selx  <= '0';
				eny   <= '0';
				sely  <= '0';
				enz   <= '0';
				selz  <= '0';
				eni   <= '0';
				seli  <= '0';
		end case;
	end process;

	
	IEEECASE: entity work.cordic_ieee
		port map(
		i_reset			=> iReset,
		i_clk			=> iClk,
		i_data			=> iEntrada,
		i_en			=> enx,
		i_sel			=> selx,
		o_case_cos		=> w_case_cos,
		o_case_sin		=> w_case_sin,
		o_case_en		=> w_case_en
		);


--	ieeeprocess: process(w_case_en)

--	begin
		
--		case w_case_en is
--		when '0'	=> oSalida1 <= X;			oSalida2 <= Y;
--		when '1' 	=> oSalida1 <= w_case_cos;	oSalida2 <= w_case_sin;
--		when others => oSalida1 <= X; 			oSalida2 <= Y;
--		end case;

--	end process;

	oSalida1 <= X;
	oSalida2 <= Y;

END RTL;