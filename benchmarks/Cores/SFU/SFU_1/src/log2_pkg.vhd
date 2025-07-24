-- f_log2 calcula el logaritmo natural de dos de un numero,
-- retorna entero: f_log2(23) = 5, f_log2(16) = 4, f_log2(17)=5 
library ieee;
use ieee.std_logic_1164.all;


package log2_pkg is

	function f_log2 (x : positive) return natural;
	
end package;


package body log2_pkg is	

	function f_log2 (x : positive) return natural is
		variable i : natural:=0;
	begin
		i := 0;  
		while (2**i < x) and i < 31 loop
				i := i + 1;
		end loop;
		return i;
	end function;
	
end package body;