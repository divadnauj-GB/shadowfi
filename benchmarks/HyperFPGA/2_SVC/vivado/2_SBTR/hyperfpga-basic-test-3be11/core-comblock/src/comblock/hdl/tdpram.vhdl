--
-- True Dual-Port RAM
--
-- Author(s):
-- * Rodrigo A. Melo
--
-- Copyright (c) 2016-2019 Authors and INTI
-- Distributed under the BSD 3-Clause License
--
-- A simplified version of TrueDualPortRAM from FPGA Lib
--

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity tdpram is
   generic (
      AWIDTH    : positive :=8; -- Address width
      DWIDTH    : positive :=8; -- Data width
      DEPTH     : natural  :=0  -- Memory depth
   );
   port (
      clk1_i    : in  std_logic;
      clk2_i    : in  std_logic;
      wen1_i    : in  std_logic;
      wen2_i    : in  std_logic;
      addr1_i   : in  std_logic_vector(AWIDTH-1 downto 0);
      addr2_i   : in  std_logic_vector(AWIDTH-1 downto 0);
      data1_i   : in  std_logic_vector(DWIDTH-1 downto 0);
      data2_i   : in  std_logic_vector(DWIDTH-1 downto 0);
      data1_o   : out std_logic_vector(DWIDTH-1 downto 0);
      data2_o   : out std_logic_vector(DWIDTH-1 downto 0)
   );
end entity tdpram;

architecture RTL of tdpram is
   function getMemorySize(depth: natural; awidth: positive) return positive is
   begin
      if depth=0 then
         return 2**awidth;
      else
         return depth;
      end if;
   end function getMemorySize;

   constant SIZE         : positive:=getMemorySize(DEPTH,AWIDTH);
   type ram_type is array(SIZE-1 downto 0) of std_logic_vector (DWIDTH-1 downto 0);
   shared variable ram   : ram_type;
begin
   ram1_p:
   process (clk1_i)
   begin
      if rising_edge(clk1_i) then
         if wen1_i='1' then
            ram(to_integer(unsigned(addr1_i))) := data1_i;
            data1_o <= data1_i;
         else
            data1_o <= ram(to_integer(unsigned(addr1_i)));
         end if;
      end if;
   end process ram1_p;

   ram2_p:
   process (clk2_i)
   begin
      if rising_edge(clk2_i) then
         if wen2_i='1' then
            ram(to_integer(unsigned(addr2_i))) := data2_i;
            data2_o <= data2_i;
         else
            data2_o <= ram(to_integer(unsigned(addr2_i)));
         end if;
      end if;
   end process ram2_p;
end architecture RTL;
