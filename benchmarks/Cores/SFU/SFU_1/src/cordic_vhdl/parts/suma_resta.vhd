
-- operacion de suma y resta en flotante.
Library IEEE;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
--use IEEE.numeric_bit.all;

--use IEEE.STD_LOGIC_ARITH.ALL;

entity suma_resta is 
generic(
		long : natural := 32
		);
     
port(
	operando1, operando2: in unsigned(long-1 downto 0);
	operacion: in unsigned(3 downto 0);
	resultado: out unsigned(long-1 downto 0)
	);
end suma_resta;

architecture ar of suma_resta is
		component prueba is
		Port ( FP_A : in  std_logic_vector (31 downto 0);
			FP_B : in  std_logic_vector (31 downto 0);
			add_sub: in std_logic;  			
			FP_Z : out  std_logic_vector (31 downto 0));
	end component;

begin

	P2: prueba port map(
				FP_A =>STD_LOGIC_VECTOR(operando1),
				FP_B =>STD_LOGIC_VECTOR(operando2),
				add_sub =>operacion(0),  			
				unsigned(FP_Z) =>resultado 
				);
end ar;

































