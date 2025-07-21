-- Log2 IEEE754 case detect
library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;
	
entity cordic_ieee is
	port 	  (	i_reset					: in std_logic;
				i_clk					: in std_logic;
				i_data					: in std_logic_vector(31 downto 0);
				i_en					: in std_logic;
				i_sel					: in std_logic;
				o_case_cos				: out std_logic_vector(31 downto 0);
				o_case_sin				: out std_logic_vector(31 downto 0);
				o_case_en				: out std_logic);
end entity;

architecture rtl of cordic_ieee is

	signal s_sgn	: std_logic;
	signal s_exp	: std_logic_vector(7 downto 0);
	signal s_mantis: std_logic_vector(22 downto 0);
	
begin
	s_sgn 	<= i_data(i_data'left);
	s_exp 	<= i_data(i_data'left-1 downto 23);
	s_mantis<= i_data(22 downto 0);
	

	process(s_sgn, s_exp, s_mantis,i_en, i_clk, i_reset)
	begin	

		if i_reset = '0' then

			o_case_sin 	<= (others=>'0');
			o_case_cos 	<= (others=>'0');
			o_case_en 	<= '0';

		elsif rising_edge(i_clk) then
			
			if i_en = '1' then

				if i_sel = '1' then
				
					if s_exp = X"00" then --subnormal y 0

						o_case_en	<= '1';
					
						if s_sgn = '0' then
							o_case_cos <= X"3F800000";
							o_case_sin <= X"00000000";
						else
						 	o_case_cos <= X"3F800000";
							o_case_sin <= X"80000000"; 
						end if;

					elsif  s_exp = X"FF" then -- +/- inf NaN
						
						o_case_en <= '1';

						o_case_cos <= X"FFFFFFFF";
						o_case_sin <= X"FFFFFFFF";
				 	
				 	else

						o_case_en <= '0'; 		
				 	
				 		o_case_cos <= X"00000000";	-- (dont care)
						o_case_sin <= X"00000000";

					end if;

				else

					o_case_sin 	<= (others=>'0');
					o_case_cos 	<= (others=>'0');
					o_case_en 	<= '0';

				end if;

			end if;

		end if;

	end process;
	
end rtl;

