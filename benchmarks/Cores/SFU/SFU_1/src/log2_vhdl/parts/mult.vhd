-- multiplicador descripcion estructural
library ieee;
	use ieee.std_logic_1164.all;
	use ieee.numeric_std.all;

entity mult is
	generic (WIDE			: 		natural := 8);
	port	  (i_term1		: in	std_logic_vector(WIDE-1 downto 0);
				i_term2		: in	std_logic_vector(WIDE-1 downto 0);
				o_product	: out	std_logic_vector(WIDE*2-1 downto 0));
end entity;

	
architecture rtl of mult is
	signal s_term1: integer;
	signal s_term2: integer;
	
	type array_terms is array (WIDE-1 downto 0) of std_logic_vector(WIDE-1 downto 0);
	signal w_and_terms: array_terms;
	
	signal w_terms1: array_terms;
	signal w_terms2: array_terms;
	
	signal w_FAcin: array_terms;
	
	--signal w_HAterm1: std_logic_vector(WIDE-2 downto 0);
	--signal w_HAterm2: std_logic_vector(WIDE-2 downto 0);
	signal w_HAcout: std_logic_vector(WIDE-2 downto 0);
	signal w_HAresult: std_logic_vector(WIDE-2 downto 0);
begin
	--(i)columnas(j)filas
	--w_terms1(0) <= "0" & w_and_terms(0)(WIDE-1 downto 1);
	
	
	--U_i: for i in 0 to WIDE-1 generate
	--	U_j: for j in 0 to WIDE-1 generate
	--		w_and_terms(i)(j) <= i_term1(j) and i_term2(i);

	--		UU_i: if i < WIDE-1 generate
	--			w_terms2(i)		<= w_and_terms(i+1);

--				Half Adders
	--			U_HA: if j = 0 generate
	--				w_HAcout(i)		<= w_terms1(i)(0) and w_terms2(i)(0); 
	--				w_HAresult(i)	<= w_terms1(i)(0) xor w_terms2(i)(0); 
	--				w_FAcin(i)(0) <= w_HAcout(i);
	--			end generate;
	--			
	--			U_FA: if j /= 0 generate
	--				a: entity work.FA port map(
	--					i_term1	=> w_terms1(i)(j),
	--					i_term2	=> w_terms2(i)(j), 
	--					i_cin		=> w_FAcin(i)(j-1),
	--					o_Sum 	=> w_terms1(i+1)(j-1),
	--					o_cout	=> w_FAcin(i)(j)
	--				);
	--			end generate;
	--			
	--			UU: if j = WIDE-1 generate
	--				w_terms1(i+1)(j) <= w_FAcin(i)(j);
	--			end generate;
	--			
	--			o_product(i+1)	<= w_HAresult(i);
	--		end generate;
	--		
	--	end generate;
	--	
	--end generate;
	
	--o_product(0) <= w_and_terms(0)(0);
	--o_product(o_product'left downto WIDE) <= w_terms1(WIDE-1)(WIDE-1 downto 0);
	--o_product <= (others => '0');
	o_product <= std_logic_vector((unsigned(i_term1)*unsigned(i_term2)));
end rtl;