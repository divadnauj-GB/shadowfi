----------------------------------------------------------------------------------
-- Right Shifter for FP addition-subtraction (right_shifter.vhd)
-- P: number of fractional (significant) bits
-- right shift up to E positions. Generates in the last bit the sticky bit.
-- PLOG is log (P); numbers of bits to represent P
-- Used in FP add of section 12.5.1
----------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity right_shifter is
	generic (
		P: natural		:= 27;
		E: natural 		:= 8;
		PLOG: natural	:= 4
	);
	port ( 
		frac 				:in  std_logic_vector (P downto 0);
		diff_exp 		:in  std_logic_vector (E downto 0);
		frac_align		:out  std_logic_vector (P downto 0));
end entity;

architecture behav of right_shifter is
   signal fracAlign_int :std_logic_vector(P downto 0);
	signal aux				:std_logic_vector(E downto PLOG+1);
   constant allShifted	:std_logic_vector(P downto 0):=(0 =>'1', others =>'0'); 
   constant CZEROS 		:std_logic_vector(E downto PLOG+1):=(others =>'0'); 
begin
   --Right Shifter. Shifts up to p+3 positions
	process(diff_exp, frac)
		variable temp 			:std_logic_vector(P downto 0);
      variable dtemp 		:std_logic_vector(P downto 0);
      variable fracAgnVar 	:std_logic_vector(P downto 0);
      variable sticky 		:std_logic;
      constant zeros 		:std_logic_vector(P downto 0):=(others => '0');
   begin
      temp := frac;
      sticky := '0';
      for i in PLOG downto 0 loop --4 downto 0 for single (P=24+3=27)
			if (diff_exp(i) = '1') then
            dtemp := (others => '0');
            dtemp(P - 2**i downto 0) := temp(P downto 2**i);
            if temp(2**i-1 downto 0) /= zeros(2**i-1 downto 0) then
               sticky := '1';
				else
					sticky := '0';
            end if;           
         else
            dtemp := temp;
         end if;
			temp := dtemp;
      end loop;
      fracAlign_int <= dtemp(P downto 1)&(dtemp(0) or sticky);
   end process;

   frac_align <= fracAlign_int when diff_exp(E downto PLOG+1) = CZEROS else allShifted;
end architecture;