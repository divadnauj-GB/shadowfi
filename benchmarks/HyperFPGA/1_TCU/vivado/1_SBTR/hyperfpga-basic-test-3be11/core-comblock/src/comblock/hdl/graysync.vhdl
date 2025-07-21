--
-- Gray Synchronizer
--
-- Author(s):
-- * Rodrigo A. Melo
--
-- Copyright (c) 2017-2019 Authors and INTI
-- Distributed under the BSD 3-Clause License
--
-- Based on cores and functions from FPGA Lib.
--

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity GraySync is
   generic(
      WIDTH : positive:=8;
      DEPTH : positive:=2
   );
   port(
      clk_i  : in  std_logic;
      data_i : in  unsigned(WIDTH-1 downto 0);
      data_o : out unsigned(WIDTH-1 downto 0)
   );
end entity GraySync;

architecture Structural of GraySync is
   signal grayi, grayo : std_logic_vector(WIDTH-1 downto 0);
   type ff_array is array (0 to DEPTH-1) of std_logic_vector(WIDTH-1 downto 0);
   signal data_r : ff_array :=(others => (others => '0'));
   ----------------------------------------------------------------------------
   -- Conversions between Binary and Gray codes
   ----------------------------------------------------------------------------
   function bin2gray(arg: unsigned) return unsigned is
   begin
      return shift_right(arg, 1) xor arg;
   end bin2gray;

   function bin2gray(arg: std_logic_vector) return std_logic_vector is
   begin
      return std_logic_vector(bin2gray(unsigned(arg)));
   end bin2gray;

   function gray2bin(arg: unsigned) return unsigned is
      variable gray, bin : unsigned(arg'high downto 0);
   begin
      gray := arg;
      bin(bin'high):=gray(gray'high);
      for i in gray'high-1 downto 0 loop
          bin(i):=bin(i+1) xor gray(i);
      end loop;
      return bin;
   end gray2bin;

   function gray2bin(arg: std_logic_vector) return std_logic_vector is
   begin
      return std_logic_vector(gray2bin(unsigned(arg)));
   end gray2bin;
begin

   grayi <= std_logic_vector(bin2gray(data_i));

   chain_proc : process (clk_i)
   begin
      if rising_edge(clk_i) then
         for i in 0 to DEPTH-1 loop
            if i=0 then
               data_r(0) <= grayi;
            else
               data_r(i) <= data_r(i-1);
            end if;
         end loop;
      end if;
   end process chain_proc;
   grayo <= data_r(DEPTH-1);

   data_o <= unsigned(gray2bin(grayo));

end architecture Structural;
