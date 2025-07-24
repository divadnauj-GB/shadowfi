library IEEE;
use ieee.std_logic_1164.all;

entity mux2_1 is 
port(
	 x,y,s: in std_logic;
	 z: out std_logic
	);
end mux2_1;

architecture au of mux2_1 is
begin
z <= x when s='0' else y when s='1';  -- si S=1 salida =y, si S=0 salida =X
end au;