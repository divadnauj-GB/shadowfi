--------------------------------------------------------------------------------
--                        DSPBlock_17x24_Freq625_uid9
-- VHDL generated for Kintex7 @ 625MHz
-- This operator is part of the Infinite Virtual Library FloPoCoLib
-- All rights reserved 
-- Authors: 
--------------------------------------------------------------------------------
-- Pipeline depth: 0 cycles
-- Clock period (ns): 1.6
-- Target frequency (MHz): 625
-- Input signals: X Y
-- Output signals: R

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library std;
use std.textio.all;
library work;

entity DSPBlock_17x24_Freq625_uid9 is
    port (clk, rst : in std_logic;
          X : in  std_logic_vector(16 downto 0);
          Y : in  std_logic_vector(23 downto 0);
          R : out  std_logic_vector(40 downto 0)   );
end entity;

architecture arch of DSPBlock_17x24_Freq625_uid9 is
signal Mint :  std_logic_vector(40 downto 0);
signal M :  std_logic_vector(40 downto 0);
signal Rtmp :  std_logic_vector(40 downto 0);
begin
   Mint <= std_logic_vector(unsigned(X) * unsigned(Y)); -- multiplier
   M <= Mint(40 downto 0);
   Rtmp <= M;
   R <= Rtmp;
end architecture;

--------------------------------------------------------------------------------
--                        DSPBlock_7x24_Freq625_uid11
-- VHDL generated for Kintex7 @ 625MHz
-- This operator is part of the Infinite Virtual Library FloPoCoLib
-- All rights reserved 
-- Authors: 
--------------------------------------------------------------------------------
-- Pipeline depth: 0 cycles
-- Clock period (ns): 1.6
-- Target frequency (MHz): 625
-- Input signals: X Y
-- Output signals: R

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library std;
use std.textio.all;
library work;

entity DSPBlock_7x24_Freq625_uid11 is
    port (clk, rst : in std_logic;
          X : in  std_logic_vector(6 downto 0);
          Y : in  std_logic_vector(23 downto 0);
          R : out  std_logic_vector(30 downto 0)   );
end entity;

architecture arch of DSPBlock_7x24_Freq625_uid11 is
signal Mint :  std_logic_vector(30 downto 0);
signal M :  std_logic_vector(30 downto 0);
signal Rtmp :  std_logic_vector(30 downto 0);
begin
   Mint <= std_logic_vector(unsigned(X) * unsigned(Y)); -- multiplier
   M <= Mint(30 downto 0);
   Rtmp <= M;
   R <= Rtmp;
end architecture;

--------------------------------------------------------------------------------
--                         IntAdder_32_Freq625_uid14
-- VHDL generated for Kintex7 @ 625MHz
-- This operator is part of the Infinite Virtual Library FloPoCoLib
-- All rights reserved 
-- Authors: Bogdan Pasca, Florent de Dinechin (2008-2016)
--------------------------------------------------------------------------------
-- Pipeline depth: 1 cycles
-- Clock period (ns): 1.6
-- Target frequency (MHz): 625
-- Input signals: X Y Cin
-- Output signals: R

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;
library std;
use std.textio.all;
library work;

entity IntAdder_32_Freq625_uid14 is
    port (clk, rst : in std_logic;
          X : in  std_logic_vector(31 downto 0);
          Y : in  std_logic_vector(31 downto 0);
          Cin : in  std_logic;
          R : out  std_logic_vector(31 downto 0)   );
end entity;

architecture arch of IntAdder_32_Freq625_uid14 is
signal Cin_0, Cin_0_d1 :  std_logic;
signal X_0, X_0_d1 :  std_logic_vector(31 downto 0);
signal Y_0, Y_0_d1 :  std_logic_vector(31 downto 0);
signal S_0 :  std_logic_vector(31 downto 0);
signal R_0 :  std_logic_vector(30 downto 0);
signal Cin_1 :  std_logic;
signal X_1, X_1_d1 :  std_logic_vector(1 downto 0);
signal Y_1, Y_1_d1 :  std_logic_vector(1 downto 0);
signal S_1 :  std_logic_vector(1 downto 0);
signal R_1 :  std_logic_vector(0 downto 0);
begin
   process(clk, rst)
      begin
         if rst = '1' then
            Cin_0_d1 <=  '0';
            X_0_d1 <=  (others => '0');
            Y_0_d1 <=  (others => '0');
            X_1_d1 <=  (others => '0');
            Y_1_d1 <=  (others => '0');
         elsif clk'event and clk = '1' then
            Cin_0_d1 <=  Cin_0;
            X_0_d1 <=  X_0;
            Y_0_d1 <=  Y_0;
            X_1_d1 <=  X_1;
            Y_1_d1 <=  Y_1;
         end if;
      end process;
   Cin_0 <= Cin;
   X_0 <= '0' & X(30 downto 0);
   Y_0 <= '0' & Y(30 downto 0);
   S_0 <= X_0_d1 + Y_0_d1 + Cin_0_d1;
   R_0 <= S_0(30 downto 0);
   Cin_1 <= S_0(31);
   X_1 <= '0' & X(31 downto 31);
   Y_1 <= '0' & Y(31 downto 31);
   S_1 <= X_1_d1 + Y_1_d1 + Cin_1;
   R_1 <= S_1(0 downto 0);
   R <= R_1 & R_0 ;
end architecture;

--------------------------------------------------------------------------------
--                         IntMultiplier_Freq625_uid5
-- VHDL generated for Kintex7 @ 625MHz
-- This operator is part of the Infinite Virtual Library FloPoCoLib
-- All rights reserved 
-- Authors: Martin Kumm, Florent de Dinechin, Kinga Illyes, Bogdan Popa, Bogdan Pasca, 2012
--------------------------------------------------------------------------------
-- Pipeline depth: 1 cycles
-- Clock period (ns): 1.6
-- Target frequency (MHz): 625
-- Input signals: X Y
-- Output signals: R

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library std;
use std.textio.all;
library work;

entity IntMultiplier_Freq625_uid5 is
    port (clk, rst : in std_logic;
          X : in  std_logic_vector(23 downto 0);
          Y : in  std_logic_vector(23 downto 0);
          R : out  std_logic_vector(47 downto 0)   );
end entity;

architecture arch of IntMultiplier_Freq625_uid5 is
   component DSPBlock_17x24_Freq625_uid9 is
      port ( clk, rst : in std_logic;
             X : in  std_logic_vector(16 downto 0);
             Y : in  std_logic_vector(23 downto 0);
             R : out  std_logic_vector(40 downto 0)   );
   end component;

   component DSPBlock_7x24_Freq625_uid11 is
      port ( clk, rst : in std_logic;
             X : in  std_logic_vector(6 downto 0);
             Y : in  std_logic_vector(23 downto 0);
             R : out  std_logic_vector(30 downto 0)   );
   end component;

   component IntAdder_32_Freq625_uid14 is
      port ( clk, rst : in std_logic;
             X : in  std_logic_vector(31 downto 0);
             Y : in  std_logic_vector(31 downto 0);
             Cin : in  std_logic;
             R : out  std_logic_vector(31 downto 0)   );
   end component;

signal XX_m6 :  std_logic_vector(23 downto 0);
signal YY_m6 :  std_logic_vector(23 downto 0);
signal tile_0_X :  std_logic_vector(16 downto 0);
signal tile_0_Y :  std_logic_vector(23 downto 0);
signal tile_0_output :  std_logic_vector(40 downto 0);
signal tile_0_filtered_output :  unsigned(40-0 downto 0);
signal bh7_w0_0 :  std_logic;
signal bh7_w1_0 :  std_logic;
signal bh7_w2_0 :  std_logic;
signal bh7_w3_0 :  std_logic;
signal bh7_w4_0 :  std_logic;
signal bh7_w5_0 :  std_logic;
signal bh7_w6_0 :  std_logic;
signal bh7_w7_0 :  std_logic;
signal bh7_w8_0 :  std_logic;
signal bh7_w9_0 :  std_logic;
signal bh7_w10_0 :  std_logic;
signal bh7_w11_0 :  std_logic;
signal bh7_w12_0 :  std_logic;
signal bh7_w13_0 :  std_logic;
signal bh7_w14_0 :  std_logic;
signal bh7_w15_0 :  std_logic;
signal bh7_w16_0 :  std_logic;
signal bh7_w17_0 :  std_logic;
signal bh7_w18_0 :  std_logic;
signal bh7_w19_0 :  std_logic;
signal bh7_w20_0 :  std_logic;
signal bh7_w21_0 :  std_logic;
signal bh7_w22_0 :  std_logic;
signal bh7_w23_0 :  std_logic;
signal bh7_w24_0 :  std_logic;
signal bh7_w25_0 :  std_logic;
signal bh7_w26_0 :  std_logic;
signal bh7_w27_0 :  std_logic;
signal bh7_w28_0 :  std_logic;
signal bh7_w29_0 :  std_logic;
signal bh7_w30_0 :  std_logic;
signal bh7_w31_0 :  std_logic;
signal bh7_w32_0 :  std_logic;
signal bh7_w33_0 :  std_logic;
signal bh7_w34_0 :  std_logic;
signal bh7_w35_0 :  std_logic;
signal bh7_w36_0 :  std_logic;
signal bh7_w37_0 :  std_logic;
signal bh7_w38_0 :  std_logic;
signal bh7_w39_0 :  std_logic;
signal bh7_w40_0 :  std_logic;
signal tile_1_X :  std_logic_vector(6 downto 0);
signal tile_1_Y :  std_logic_vector(23 downto 0);
signal tile_1_output :  std_logic_vector(30 downto 0);
signal tile_1_filtered_output :  unsigned(30-0 downto 0);
signal bh7_w17_1 :  std_logic;
signal bh7_w18_1 :  std_logic;
signal bh7_w19_1 :  std_logic;
signal bh7_w20_1 :  std_logic;
signal bh7_w21_1 :  std_logic;
signal bh7_w22_1 :  std_logic;
signal bh7_w23_1 :  std_logic;
signal bh7_w24_1 :  std_logic;
signal bh7_w25_1 :  std_logic;
signal bh7_w26_1 :  std_logic;
signal bh7_w27_1 :  std_logic;
signal bh7_w28_1 :  std_logic;
signal bh7_w29_1 :  std_logic;
signal bh7_w30_1 :  std_logic;
signal bh7_w31_1 :  std_logic;
signal bh7_w32_1 :  std_logic;
signal bh7_w33_1 :  std_logic;
signal bh7_w34_1 :  std_logic;
signal bh7_w35_1 :  std_logic;
signal bh7_w36_1 :  std_logic;
signal bh7_w37_1 :  std_logic;
signal bh7_w38_1 :  std_logic;
signal bh7_w39_1 :  std_logic;
signal bh7_w40_1 :  std_logic;
signal bh7_w41_0 :  std_logic;
signal bh7_w42_0 :  std_logic;
signal bh7_w43_0 :  std_logic;
signal bh7_w44_0 :  std_logic;
signal bh7_w45_0 :  std_logic;
signal bh7_w46_0 :  std_logic;
signal bh7_w47_0 :  std_logic;
signal tmp_bitheapResult_bh7_16, tmp_bitheapResult_bh7_16_d1 :  std_logic_vector(16 downto 0);
signal bitheapFinalAdd_bh7_In0 :  std_logic_vector(31 downto 0);
signal bitheapFinalAdd_bh7_In1 :  std_logic_vector(31 downto 0);
signal bitheapFinalAdd_bh7_Cin :  std_logic;
signal bitheapFinalAdd_bh7_Out :  std_logic_vector(31 downto 0);
signal bitheapResult_bh7 :  std_logic_vector(47 downto 0);
begin
   process(clk, rst)
      begin
         if rst = '1' then
            tmp_bitheapResult_bh7_16_d1 <=  (others => '0');
         elsif clk'event and clk = '1' then
            tmp_bitheapResult_bh7_16_d1 <=  tmp_bitheapResult_bh7_16;
         end if;
      end process;
   XX_m6 <= X ;
   YY_m6 <= Y ;
   tile_0_X <= X(16 downto 0);
   tile_0_Y <= Y(23 downto 0);
   tile_0_mult: DSPBlock_17x24_Freq625_uid9
      port map ( clk  => clk,
                 rst  => rst,
                 X => tile_0_X,
                 Y => tile_0_Y,
                 R => tile_0_output);

   tile_0_filtered_output <= unsigned(tile_0_output(40 downto 0));
   bh7_w0_0 <= tile_0_filtered_output(0);
   bh7_w1_0 <= tile_0_filtered_output(1);
   bh7_w2_0 <= tile_0_filtered_output(2);
   bh7_w3_0 <= tile_0_filtered_output(3);
   bh7_w4_0 <= tile_0_filtered_output(4);
   bh7_w5_0 <= tile_0_filtered_output(5);
   bh7_w6_0 <= tile_0_filtered_output(6);
   bh7_w7_0 <= tile_0_filtered_output(7);
   bh7_w8_0 <= tile_0_filtered_output(8);
   bh7_w9_0 <= tile_0_filtered_output(9);
   bh7_w10_0 <= tile_0_filtered_output(10);
   bh7_w11_0 <= tile_0_filtered_output(11);
   bh7_w12_0 <= tile_0_filtered_output(12);
   bh7_w13_0 <= tile_0_filtered_output(13);
   bh7_w14_0 <= tile_0_filtered_output(14);
   bh7_w15_0 <= tile_0_filtered_output(15);
   bh7_w16_0 <= tile_0_filtered_output(16);
   bh7_w17_0 <= tile_0_filtered_output(17);
   bh7_w18_0 <= tile_0_filtered_output(18);
   bh7_w19_0 <= tile_0_filtered_output(19);
   bh7_w20_0 <= tile_0_filtered_output(20);
   bh7_w21_0 <= tile_0_filtered_output(21);
   bh7_w22_0 <= tile_0_filtered_output(22);
   bh7_w23_0 <= tile_0_filtered_output(23);
   bh7_w24_0 <= tile_0_filtered_output(24);
   bh7_w25_0 <= tile_0_filtered_output(25);
   bh7_w26_0 <= tile_0_filtered_output(26);
   bh7_w27_0 <= tile_0_filtered_output(27);
   bh7_w28_0 <= tile_0_filtered_output(28);
   bh7_w29_0 <= tile_0_filtered_output(29);
   bh7_w30_0 <= tile_0_filtered_output(30);
   bh7_w31_0 <= tile_0_filtered_output(31);
   bh7_w32_0 <= tile_0_filtered_output(32);
   bh7_w33_0 <= tile_0_filtered_output(33);
   bh7_w34_0 <= tile_0_filtered_output(34);
   bh7_w35_0 <= tile_0_filtered_output(35);
   bh7_w36_0 <= tile_0_filtered_output(36);
   bh7_w37_0 <= tile_0_filtered_output(37);
   bh7_w38_0 <= tile_0_filtered_output(38);
   bh7_w39_0 <= tile_0_filtered_output(39);
   bh7_w40_0 <= tile_0_filtered_output(40);
   tile_1_X <= X(23 downto 17);
   tile_1_Y <= Y(23 downto 0);
   tile_1_mult: DSPBlock_7x24_Freq625_uid11
      port map ( clk  => clk,
                 rst  => rst,
                 X => tile_1_X,
                 Y => tile_1_Y,
                 R => tile_1_output);

   tile_1_filtered_output <= unsigned(tile_1_output(30 downto 0));
   bh7_w17_1 <= tile_1_filtered_output(0);
   bh7_w18_1 <= tile_1_filtered_output(1);
   bh7_w19_1 <= tile_1_filtered_output(2);
   bh7_w20_1 <= tile_1_filtered_output(3);
   bh7_w21_1 <= tile_1_filtered_output(4);
   bh7_w22_1 <= tile_1_filtered_output(5);
   bh7_w23_1 <= tile_1_filtered_output(6);
   bh7_w24_1 <= tile_1_filtered_output(7);
   bh7_w25_1 <= tile_1_filtered_output(8);
   bh7_w26_1 <= tile_1_filtered_output(9);
   bh7_w27_1 <= tile_1_filtered_output(10);
   bh7_w28_1 <= tile_1_filtered_output(11);
   bh7_w29_1 <= tile_1_filtered_output(12);
   bh7_w30_1 <= tile_1_filtered_output(13);
   bh7_w31_1 <= tile_1_filtered_output(14);
   bh7_w32_1 <= tile_1_filtered_output(15);
   bh7_w33_1 <= tile_1_filtered_output(16);
   bh7_w34_1 <= tile_1_filtered_output(17);
   bh7_w35_1 <= tile_1_filtered_output(18);
   bh7_w36_1 <= tile_1_filtered_output(19);
   bh7_w37_1 <= tile_1_filtered_output(20);
   bh7_w38_1 <= tile_1_filtered_output(21);
   bh7_w39_1 <= tile_1_filtered_output(22);
   bh7_w40_1 <= tile_1_filtered_output(23);
   bh7_w41_0 <= tile_1_filtered_output(24);
   bh7_w42_0 <= tile_1_filtered_output(25);
   bh7_w43_0 <= tile_1_filtered_output(26);
   bh7_w44_0 <= tile_1_filtered_output(27);
   bh7_w45_0 <= tile_1_filtered_output(28);
   bh7_w46_0 <= tile_1_filtered_output(29);
   bh7_w47_0 <= tile_1_filtered_output(30);

   -- Adding the constant bits 
      -- All the constant bits are zero, nothing to add

   tmp_bitheapResult_bh7_16 <= bh7_w16_0 & bh7_w15_0 & bh7_w14_0 & bh7_w13_0 & bh7_w12_0 & bh7_w11_0 & bh7_w10_0 & bh7_w9_0 & bh7_w8_0 & bh7_w7_0 & bh7_w6_0 & bh7_w5_0 & bh7_w4_0 & bh7_w3_0 & bh7_w2_0 & bh7_w1_0 & bh7_w0_0;

   bitheapFinalAdd_bh7_In0 <= "0" & bh7_w47_0 & bh7_w46_0 & bh7_w45_0 & bh7_w44_0 & bh7_w43_0 & bh7_w42_0 & bh7_w41_0 & bh7_w40_0 & bh7_w39_0 & bh7_w38_0 & bh7_w37_0 & bh7_w36_0 & bh7_w35_0 & bh7_w34_0 & bh7_w33_0 & bh7_w32_0 & bh7_w31_0 & bh7_w30_0 & bh7_w29_0 & bh7_w28_0 & bh7_w27_0 & bh7_w26_0 & bh7_w25_0 & bh7_w24_0 & bh7_w23_0 & bh7_w22_0 & bh7_w21_0 & bh7_w20_0 & bh7_w19_0 & bh7_w18_0 & bh7_w17_0;
   bitheapFinalAdd_bh7_In1 <= "0" & "0" & "0" & "0" & "0" & "0" & "0" & "0" & bh7_w40_1 & bh7_w39_1 & bh7_w38_1 & bh7_w37_1 & bh7_w36_1 & bh7_w35_1 & bh7_w34_1 & bh7_w33_1 & bh7_w32_1 & bh7_w31_1 & bh7_w30_1 & bh7_w29_1 & bh7_w28_1 & bh7_w27_1 & bh7_w26_1 & bh7_w25_1 & bh7_w24_1 & bh7_w23_1 & bh7_w22_1 & bh7_w21_1 & bh7_w20_1 & bh7_w19_1 & bh7_w18_1 & bh7_w17_1;
   bitheapFinalAdd_bh7_Cin <= '0';

   bitheapFinalAdd_bh7: IntAdder_32_Freq625_uid14
      port map ( clk  => clk,
                 rst  => rst,
                 Cin => bitheapFinalAdd_bh7_Cin,
                 X => bitheapFinalAdd_bh7_In0,
                 Y => bitheapFinalAdd_bh7_In1,
                 R => bitheapFinalAdd_bh7_Out);
   bitheapResult_bh7 <= bitheapFinalAdd_bh7_Out(30 downto 0) & tmp_bitheapResult_bh7_16_d1;
   R <= bitheapResult_bh7(47 downto 0);
end architecture;

--------------------------------------------------------------------------------
--                         IntAdder_33_Freq625_uid17
-- VHDL generated for Kintex7 @ 625MHz
-- This operator is part of the Infinite Virtual Library FloPoCoLib
-- All rights reserved 
-- Authors: Bogdan Pasca, Florent de Dinechin (2008-2016)
--------------------------------------------------------------------------------
-- Pipeline depth: 1 cycles
-- Clock period (ns): 1.6
-- Target frequency (MHz): 625
-- Input signals: X Y Cin
-- Output signals: R

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;
library std;
use std.textio.all;
library work;

entity IntAdder_33_Freq625_uid17 is
    port (clk, rst : in std_logic;
          X : in  std_logic_vector(32 downto 0);
          Y : in  std_logic_vector(32 downto 0);
          Cin : in  std_logic;
          R : out  std_logic_vector(32 downto 0)   );
end entity;

architecture arch of IntAdder_33_Freq625_uid17 is
signal Cin_0, Cin_0_d1 :  std_logic;
signal X_0, X_0_d1, X_0_d2 :  std_logic_vector(7 downto 0);
signal Y_0, Y_0_d1, Y_0_d2, Y_0_d3 :  std_logic_vector(7 downto 0);
signal S_0 :  std_logic_vector(7 downto 0);
signal R_0 :  std_logic_vector(6 downto 0);
signal Cin_1 :  std_logic;
signal X_1, X_1_d1, X_1_d2 :  std_logic_vector(26 downto 0);
signal Y_1, Y_1_d1, Y_1_d2, Y_1_d3 :  std_logic_vector(26 downto 0);
signal S_1 :  std_logic_vector(26 downto 0);
signal R_1 :  std_logic_vector(25 downto 0);
begin
   process(clk, rst)
      begin
         if rst = '1' then
            Cin_0_d1 <=  '0';
            X_0_d1 <=  (others => '0');
            X_0_d2 <=  (others => '0');
            Y_0_d1 <=  (others => '0');
            Y_0_d2 <=  (others => '0');
            Y_0_d3 <=  (others => '0');
            X_1_d1 <=  (others => '0');
            X_1_d2 <=  (others => '0');
            Y_1_d1 <=  (others => '0');
            Y_1_d2 <=  (others => '0');
            Y_1_d3 <=  (others => '0');
         elsif clk'event and clk = '1' then
            Cin_0_d1 <=  Cin_0;
            X_0_d1 <=  X_0;
            X_0_d2 <=  X_0_d1;
            Y_0_d1 <=  Y_0;
            Y_0_d2 <=  Y_0_d1;
            Y_0_d3 <=  Y_0_d2;
            X_1_d1 <=  X_1;
            X_1_d2 <=  X_1_d1;
            Y_1_d1 <=  Y_1;
            Y_1_d2 <=  Y_1_d1;
            Y_1_d3 <=  Y_1_d2;
         end if;
      end process;
   Cin_0 <= Cin;
   X_0 <= '0' & X(6 downto 0);
   Y_0 <= '0' & Y(6 downto 0);
   S_0 <= X_0_d2 + Y_0_d3 + Cin_0_d1;
   R_0 <= S_0(6 downto 0);
   Cin_1 <= S_0(7);
   X_1 <= '0' & X(32 downto 7);
   Y_1 <= '0' & Y(32 downto 7);
   S_1 <= X_1_d2 + Y_1_d3 + Cin_1;
   R_1 <= S_1(25 downto 0);
   R <= R_1 & R_0 ;
end architecture;

--------------------------------------------------------------------------------
--                               FPMult_3_pipex
--                 (FPMult_8_23_8_23_8_23_uid2_Freq625_uid3)
-- VHDL generated for Kintex7 @ 625MHz
-- This operator is part of the Infinite Virtual Library FloPoCoLib
-- All rights reserved 
-- Authors: Bogdan Pasca, Florent de Dinechin 2008-2021
--------------------------------------------------------------------------------
-- Pipeline depth: 3 cycles
-- Clock period (ns): 1.6
-- Target frequency (MHz): 625
-- Input signals: X Y
-- Output signals: R

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;
library std;
use std.textio.all;
library work;

entity FPMult_3_pipex is
    port (clk, rst : in std_logic;
          X : in  std_logic_vector(8+23+2 downto 0);
          Y : in  std_logic_vector(8+23+2 downto 0);
          R : out  std_logic_vector(8+23+2 downto 0)   );
end entity;

architecture arch of FPMult_3_pipex is
   component IntMultiplier_Freq625_uid5 is
      port ( clk, rst : in std_logic;
             X : in  std_logic_vector(23 downto 0);
             Y : in  std_logic_vector(23 downto 0);
             R : out  std_logic_vector(47 downto 0)   );
   end component;

   component IntAdder_33_Freq625_uid17 is
      port ( clk, rst : in std_logic;
             X : in  std_logic_vector(32 downto 0);
             Y : in  std_logic_vector(32 downto 0);
             Cin : in  std_logic;
             R : out  std_logic_vector(32 downto 0)   );
   end component;

signal sign, sign_d1, sign_d2, sign_d3 :  std_logic;
signal expX :  std_logic_vector(7 downto 0);
signal expY :  std_logic_vector(7 downto 0);
signal expSumPreSub, expSumPreSub_d1 :  std_logic_vector(9 downto 0);
signal bias, bias_d1 :  std_logic_vector(9 downto 0);
signal expSum :  std_logic_vector(9 downto 0);
signal sigX :  std_logic_vector(23 downto 0);
signal sigY :  std_logic_vector(23 downto 0);
signal sigProd :  std_logic_vector(47 downto 0);
signal excSel :  std_logic_vector(3 downto 0);
signal exc, exc_d1, exc_d2, exc_d3 :  std_logic_vector(1 downto 0);
signal norm :  std_logic;
signal expPostNorm :  std_logic_vector(9 downto 0);
signal sigProdExt, sigProdExt_d1 :  std_logic_vector(47 downto 0);
signal expSig :  std_logic_vector(32 downto 0);
signal sticky, sticky_d1 :  std_logic;
signal guard :  std_logic;
signal round :  std_logic;
signal expSigPostRound :  std_logic_vector(32 downto 0);
signal excPostNorm :  std_logic_vector(1 downto 0);
signal finalExc :  std_logic_vector(1 downto 0);
begin
   process(clk, rst)
      begin
         if rst = '1' then
            sign_d1 <=  '0';
            sign_d2 <=  '0';
            sign_d3 <=  '0';
            expSumPreSub_d1 <=  (others => '0');
            bias_d1 <=  (others => '0');
            exc_d1 <=  (others => '0');
            exc_d2 <=  (others => '0');
            exc_d3 <=  (others => '0');
            sigProdExt_d1 <=  (others => '0');
            sticky_d1 <=  '0';
         elsif clk'event and clk = '1' then
            sign_d1 <=  sign;
            sign_d2 <=  sign_d1;
            sign_d3 <=  sign_d2;
            expSumPreSub_d1 <=  expSumPreSub;
            bias_d1 <=  bias;
            exc_d1 <=  exc;
            exc_d2 <=  exc_d1;
            exc_d3 <=  exc_d2;
            sigProdExt_d1 <=  sigProdExt;
            sticky_d1 <=  sticky;
         end if;
      end process;
   sign <= X(31) xor Y(31);
   expX <= X(30 downto 23);
   expY <= Y(30 downto 23);
   expSumPreSub <= ("00" & expX) + ("00" & expY);
   bias <= CONV_STD_LOGIC_VECTOR(127,10);
   expSum <= expSumPreSub_d1 - bias_d1;
   sigX <= "1" & X(22 downto 0);
   sigY <= "1" & Y(22 downto 0);
   SignificandMultiplication: IntMultiplier_Freq625_uid5
      port map ( clk  => clk,
                 rst  => rst,
                 X => sigX,
                 Y => sigY,
                 R => sigProd);
   excSel <= X(33 downto 32) & Y(33 downto 32);
   with excSel  select  
   exc <= "00" when  "0000" | "0001" | "0100", 
          "01" when "0101",
          "10" when "0110" | "1001" | "1010" ,
          "11" when others;
   norm <= sigProd(47);
   -- exponent update
   expPostNorm <= expSum + ("000000000" & norm);
   -- significand normalization shift
   sigProdExt <= sigProd(46 downto 0) & "0" when norm='1' else
                         sigProd(45 downto 0) & "00";
   expSig <= expPostNorm & sigProdExt(47 downto 25);
   sticky <= sigProdExt(24);
   guard <= '0' when sigProdExt_d1(23 downto 0)="000000000000000000000000" else '1';
   round <= sticky_d1 and ( (guard and not(sigProdExt_d1(25))) or (sigProdExt_d1(25) ))  ;
   RoundingAdder: IntAdder_33_Freq625_uid17
      port map ( clk  => clk,
                 rst  => rst,
                 Cin => round,
                 X => expSig,
                 Y => "000000000000000000000000000000000",
                 R => expSigPostRound);
   with expSigPostRound(32 downto 31)  select 
   excPostNorm <=  "01"  when  "00",
                               "10"             when "01", 
                               "00"             when "11"|"10",
                               "11"             when others;
   with exc_d3  select  
   finalExc <= exc_d3 when  "11"|"10"|"00",
                       excPostNorm when others; 
   R <= finalExc & sign_d3 & expSigPostRound(30 downto 0);
end architecture;


--------------------------------------------------------------------------------
--                                 InputIEEE
--                          (InputIEEE_8_23_to_8_23)
-- VHDL generated for Kintex7 @ 0MHz
-- This operator is part of the Infinite Virtual Library FloPoCoLib
-- All rights reserved 
-- Authors: Florent de Dinechin (2008)
--------------------------------------------------------------------------------
-- combinatorial
-- Clock period (ns): inf
-- Target frequency (MHz): 0
-- Input signals: X
-- Output signals: R

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;
library std;
use std.textio.all;
library work;

entity InputIEEE is
    port (X : in  std_logic_vector(31 downto 0);
          R : out  std_logic_vector(8+23+2 downto 0)   );
end entity;

architecture arch of InputIEEE is
signal expX :  std_logic_vector(7 downto 0);
signal fracX :  std_logic_vector(22 downto 0);
signal sX :  std_logic;
signal expZero :  std_logic;
signal expInfty :  std_logic;
signal fracZero :  std_logic;
signal reprSubNormal :  std_logic;
signal sfracX :  std_logic_vector(22 downto 0);
signal fracR :  std_logic_vector(22 downto 0);
signal expR :  std_logic_vector(7 downto 0);
signal infinity :  std_logic;
signal zero :  std_logic;
signal NaN :  std_logic;
signal exnR :  std_logic_vector(1 downto 0);
begin
   expX  <= X(30 downto 23);
   fracX  <= X(22 downto 0);
   sX  <= X(31);
   expZero  <= '1' when expX = (7 downto 0 => '0') else '0';
   expInfty  <= '1' when expX = (7 downto 0 => '1') else '0';
   fracZero <= '1' when fracX = (22 downto 0 => '0') else '0';
   reprSubNormal <= fracX(22);
   -- since we have one more exponent value than IEEE (field 0...0, value emin-1),
   -- we can represent subnormal numbers whose mantissa field begins with a 1
   sfracX <= fracX(21 downto 0) & '0' when (expZero='1' and reprSubNormal='1')    else fracX;
   fracR <= sfracX;
   -- copy exponent. This will be OK even for subnormals, zero and infty since in such cases the exn bits will prevail
   expR <= expX;
   infinity <= expInfty and fracZero;
   zero <= expZero and not reprSubNormal;
   NaN <= expInfty and not fracZero;
   exnR <= 
           "00" when zero='1' 
      else "10" when infinity='1' 
      else "11" when NaN='1' 
      else "01" ;  -- normal number
   R <= exnR & sX & expR & fracR; 
end architecture;


--------------------------------------------------------------------------------
--                                 OutputIEEE
--                         (OutputIEEE_8_23_to_8_23)
-- VHDL generated for Kintex7 @ 0MHz
-- This operator is part of the Infinite Virtual Library FloPoCoLib
-- All rights reserved 
-- Authors: F. Ferrandi  (2009-2012)
--------------------------------------------------------------------------------
-- combinatorial
-- Clock period (ns): inf
-- Target frequency (MHz): 0
-- Input signals: X
-- Output signals: R

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;
library std;
use std.textio.all;
library work;

entity OutputIEEE is
    port (X : in  std_logic_vector(8+23+2 downto 0);
          R : out  std_logic_vector(31 downto 0)   );
end entity;

architecture arch of OutputIEEE is
signal fracX :  std_logic_vector(22 downto 0);
signal exnX :  std_logic_vector(1 downto 0);
signal expX :  std_logic_vector(7 downto 0);
signal sX :  std_logic;
signal expZero :  std_logic;
signal fracR :  std_logic_vector(22 downto 0);
signal expR :  std_logic_vector(7 downto 0);
begin
   fracX  <= X(22 downto 0);
   exnX  <= X(33 downto 32);
   expX  <= X(30 downto 23);
   sX  <= X(31) when (exnX = "01" or exnX = "10" or exnX = "00") else '0';
   expZero  <= '1' when expX = (7 downto 0 => '0') else '0';
   -- since we have one more exponent value than IEEE (field 0...0, value emin-1),
   -- we can represent subnormal numbers whose mantissa field begins with a 1
   fracR <= 
      "00000000000000000000000" when (exnX = "00") else
      '1' & fracX(22 downto 1) & "" when (expZero = '1' and exnX = "01") else
      fracX  & "" when (exnX = "01") else 
      "0000000000000000000000" & exnX(0);
   expR <=  
      (7 downto 0 => '0') when (exnX = "00") else
      expX when (exnX = "01") else 
      (7 downto 0 => '1');
   R <= sX & expR & fracR; 
end architecture;



library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;
library std;
use std.textio.all;
library work;

entity FPMult_3_pipe is
    port (clk, rst : in std_logic;
		  X : in  std_logic_vector(31 downto 0);
		  Y : in  std_logic_vector(31 downto 0);
		  R : out  std_logic_vector(31 downto 0)   );
end entity;

architecture arch of FPMult_3_pipe is
	component OutputIEEE is
		port (X : in  std_logic_vector(8+23+2 downto 0);
			  R : out  std_logic_vector(31 downto 0)   );
	end component;
    
	component InputIEEE is
    port (X : in  std_logic_vector(31 downto 0);
          R : out  std_logic_vector(8+23+2 downto 0)   );
	end component;
	
	component FPMult_3_pipex is
		port (clk, rst : in std_logic;
			  X : in  std_logic_vector(8+23+2 downto 0);
			  Y : in  std_logic_vector(8+23+2 downto 0);
			  R : out  std_logic_vector(8+23+2 downto 0)   );
	end component;
	
	signal X1: std_logic_vector(8+23+2 downto 0);
	signal Y1: std_logic_vector(8+23+2 downto 0);
	signal R1: std_logic_vector(8+23+2 downto 0);
	
begin
	InputX: InputIEEE
		port map(
		X => X,
		R => X1);
	
	InputY: InputIEEE
		port map(
		X => Y,
		R => Y1);
	
	FlopocoFPMult: FPMult_3_pipex
		port map(
		clk => clk,
		rst => rst,
		X => X1,
		Y => Y1,
		R => R1);
		
	OutputR: OutputIEEE
		port map(
		X => R1,
		R => R);
end architecture;
