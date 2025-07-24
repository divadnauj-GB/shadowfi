-- Log2 IEEE754 case detect
library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;
	
entity rsqrt_ieee is
	port 	  (i_data					: in	std_logic_vector(31 downto 0);
				o_case					: out std_logic_vector(31 downto 0);
				o_case_en				: out std_logic);
end entity;

architecture rtl of rsqrt_ieee is

	signal s_sgn	: std_logic;
	signal s_exp	: std_logic_vector(7 downto 0);
	signal s_mantis: std_logic_vector(22 downto 0);
	
begin
	s_sgn 	<= i_data(i_data'left);
	s_exp 	<= i_data(i_data'left-1 downto 23);
	s_mantis	<= i_data(22 downto 0);
	
	process(s_sgn, s_exp, s_mantis)
	begin	

		if s_sgn = '1' then
			o_case_en	<= '1';
			if s_exp = X"00" then
				o_case <= X"FF800000";		-- -inf
			else
				o_case <= X"FFFFFFFF";		-- NaN
			end if;

		else
			if s_exp = X"00" then
				o_case_en	<= '1';
				o_case <= X"7F800000";		-- +inf
			elsif s_exp = X"FF" then
				o_case_en	<= '1';
				if s_mantis = "00000000000000000000000" then
					o_case <= X"00000000";	
				else
					o_case <= X"FFFFFFFF"; -- NaN
				end if;
			else
				o_case_en	<= '0';
				o_case <= X"FFFFFFFF"; 		-- (dont care)
			end if;

		end if;

	end process;
	
end rtl;

