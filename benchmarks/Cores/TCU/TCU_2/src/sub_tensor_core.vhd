----------------------------------------------------------------------------
-- Company:         	Politecnico di Torino
-- Engineer:          	Josie E. Rodriguez Condia
--
-- Create Date:     		23/10/2022
-- Module Name:   	Sub-tensor Unit - 6 - pipes from flopoco
-- Project Name:   	Open TCU
-- Target Devices:		
-- Tool versions:    	ModelSim
-- Description:
--
----------------------------------------------------------------------------
-- Revisions:
--  REV:        Date:          			Description:
--  1.0.a       	23/10/2022      	 	Created Top level file
----------------------------------------------------------------------------

-- The sub_tensor_core_unit process the vectorial 4X4 matrix multiplication
--



Library IEEE;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.def_package.all;

entity sub_tensor_core is
	
	generic(
				size: natural:= 2;			-- I think it must be 2..
				long : natural := 32
				);

	port(
	-- modified for the synth version...(currently working the synthesis)
				clk : in std_logic;
				rst : in std_logic;
				A_0X: in  operand_array(2**size - 1 downto 0);	-- A_0X <= (0 => bus0, 1 => bus1, 2 => bus2, 3 => bus3);
				A_1X: in  operand_array(2**size - 1 downto 0);
				A_2X: in  operand_array(2**size - 1 downto 0);
				A_3X: in  operand_array(2**size - 1 downto 0);
				B_0X: in  operand_array(2**size - 1 downto 0);
				B_1X: in  operand_array(2**size - 1 downto 0);
				B_2X: in  operand_array(2**size - 1 downto 0);
				B_3X: in  operand_array(2**size - 1 downto 0);
				C_0X: in  operand_array(2**size - 1 downto 0);
				C_1X: in  operand_array(2**size - 1 downto 0);
				C_2X: in  operand_array(2**size - 1 downto 0);
				C_3X: in operand_array(2**size - 1 downto 0);
				W_0X3: out operand_array(2**size - 1 downto 0);
				W_1X3: out operand_array(2**size - 1 downto 0);
				W_2X3: out operand_array(2**size - 1 downto 0);
				W_3X3: out operand_array(2**size - 1 downto 0)
	);
end sub_tensor_core;

architecture ar of sub_tensor_core is

	-- Signals for the interconnection of the cores:

--	signal A_0X_s: operand_array(2**size - 1 downto 0);		-- temp definition for the analysis of the missing connections.

	-- remember to include the generic port to allow the size definition...

	component dot_unit_core is port(
				clk : in std_logic;
				rst : in std_logic;
				a_X0 : in std_logic_vector(31 downto 0);
				a_X1 : in std_logic_vector(31 downto 0);
				a_X2 : in std_logic_vector(31 downto 0);
				a_X3 : in std_logic_vector(31 downto 0);
				b_X0  : in std_logic_vector(31 downto 0);
				b_X1  : in std_logic_vector(31 downto 0);
				b_X2  : in std_logic_vector(31 downto 0);
				b_X3  : in std_logic_vector(31 downto 0);		
				c_X0: in std_logic_vector(31 downto 0);
				w_XX3: out std_logic_vector(31 downto 0)
				);
		end component;
		
	signal rst_s: std_logic;
	signal clk_s: std_logic;

	begin

	-- description of the (4x4 array) 16 cores...

	clk_s <= clk;
	rst_s <= rst;

	-- A00, B00, c00
	D_UNIT0: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_0X(0),
					a_X1 => A_0X(1),
					a_X2 => A_0X(2),
					a_X3 => A_0X(3),
					b_X0 => B_0X(0),
					b_X1 => B_1X(0),
					b_X2 => B_2X(0),
					b_X3 => B_3X(0),
					c_X0 => C_0X(0),
					w_XX3 =>W_0X3(0)
				);

	-- A00, B01, c10
	D_UNIT1: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_0X(0),
					a_X1 => A_0X(1),
					a_X2 => A_0X(2),
					a_X3 => A_0X(3),
					b_X0 => B_0X(1),
					b_X1 => B_1X(1),
					b_X2 => B_2X(1),
					b_X3 => B_3X(1),
					c_X0 => C_1X(0),
					w_XX3 =>W_0X3(1)
				);

	-- A00, B02, c20
	D_UNIT2: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_0X(0),
					a_X1 => A_0X(1),
					a_X2 => A_0X(2),
					a_X3 => A_0X(3),
					b_X0 => B_0X(2),
					b_X1 => B_1X(2),
					b_X2 => B_2X(2),
					b_X3 => B_3X(2),
					c_X0 => C_2X(0),
					w_XX3 =>W_0X3(2)
				);

	-- A00, B03, c30
	D_UNIT3: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_0X(0),
					a_X1 => A_0X(1),
					a_X2 => A_0X(2),
					a_X3 => A_0X(3),
					b_X0 => B_0X(3),
					b_X1 => B_1X(3),
					b_X2 => B_2X(3),
					b_X3 => B_3X(3),
					c_X0 => C_3X(0),
					w_XX3 =>W_0X3(3)
				);
	
	-- A10, B00, c01
	D_UNIT4: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_1X(0),
					a_X1 => A_1X(1),
					a_X2 => A_1X(2),
					a_X3 => A_1X(3),
					b_X0 => B_0X(0),
					b_X1 => B_1X(0),
					b_X2 => B_2X(0),
					b_X3 => B_3X(0),
					c_X0 => C_0X(1),
					w_XX3 =>W_1X3(0)
				);
	
	-- A10, B01, c11
	D_UNIT5: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_1X(0),
					a_X1 => A_1X(1),
					a_X2 => A_1X(2),
					a_X3 => A_1X(3),
					b_X0 => B_0X(1),
					b_X1 => B_1X(1),
					b_X2 => B_2X(1),
					b_X3 => B_3X(1),
					c_X0 => C_1X(1),
					w_XX3 =>W_1X3(1)
				);

	-- A10, B02, c21
	D_UNIT6: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_1X(0),
					a_X1 => A_1X(1),
					a_X2 => A_1X(2),
					a_X3 => A_1X(3),
					b_X0 => B_0X(2),
					b_X1 => B_1X(2),
					b_X2 => B_2X(2),
					b_X3 => B_3X(2),
					c_X0 => C_2X(1),
					w_XX3 =>W_1X3(2)
				);

	-- A10, B03, c31
	D_UNIT7: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_1X(0),
					a_X1 => A_1X(1),
					a_X2 => A_1X(2),
					a_X3 => A_1X(3),
					b_X0 => B_0X(3),
					b_X1 => B_1X(3),
					b_X2 => B_2X(3),
					b_X3 => B_3X(3),
					c_X0 => C_3X(1),
					w_XX3 =>W_1X3(3)
				);

	-- A20, B00, c02
	D_UNIT8: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_2X(0),
					a_X1 => A_2X(1),
					a_X2 => A_2X(2),
					a_X3 => A_2X(3),
					b_X0 => B_0X(0),
					b_X1 => B_1X(0),
					b_X2 => B_2X(0),
					b_X3 => B_3X(0),
					c_X0 => C_0X(2),
					w_XX3 =>W_2X3(0)
				);

	-- A20, B01, c12
	D_UNIT9: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_2X(0),
					a_X1 => A_2X(1),
					a_X2 => A_2X(2),
					a_X3 => A_2X(3),
					b_X0 => B_0X(1),
					b_X1 => B_1X(1),
					b_X2 => B_2X(1),
					b_X3 => B_3X(1),
					c_X0 => C_1X(2),
					w_XX3 =>W_2X3(1)
				);

	-- A20, B02, c22
	D_UNIT10: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_2X(0),
					a_X1 => A_2X(1),
					a_X2 => A_2X(2),
					a_X3 => A_2X(3),
					b_X0 => B_0X(2),
					b_X1 => B_1X(2),
					b_X2 => B_2X(2),
					b_X3 => B_3X(2),
					c_X0 => C_2X(2),
					w_XX3 =>W_2X3(2)
				);

	-- A20, B03, c32
	D_UNIT11: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_2X(0),
					a_X1 => A_2X(1),
					a_X2 => A_2X(2),
					a_X3 => A_2X(3),
					b_X0 => B_0X(3),
					b_X1 => B_1X(3),
					b_X2 => B_2X(3),
					b_X3 => B_3X(3),
					c_X0 => C_3X(2),
					w_XX3 =>W_2X3(3)
				);

	-- A30, B00, c03
	D_UNIT12: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_3X(0),
					a_X1 => A_3X(1),
					a_X2 => A_3X(2),
					a_X3 => A_3X(3),
					b_X0 => B_0X(0),
					b_X1 => B_1X(0),
					b_X2 => B_2X(0),
					b_X3 => B_3X(0),
					c_X0 => C_0X(3),
					w_XX3 =>W_3X3(0)
				);

	-- A30, B01, c13
	D_UNIT13: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_3X(0),
					a_X1 => A_3X(1),
					a_X2 => A_3X(2),
					a_X3 => A_3X(3),
					b_X0 => B_0X(1),
					b_X1 => B_1X(1),
					b_X2 => B_2X(1),
					b_X3 => B_3X(1),
					c_X0 => C_1X(3),
					w_XX3 =>W_3X3(1)
				);

	-- A30, B02, c23
	D_UNIT14: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_3X(0),
					a_X1 => A_3X(1),
					a_X2 => A_3X(2),
					a_X3 => A_3X(3),
					b_X0 => B_0X(2),
					b_X1 => B_1X(2),
					b_X2 => B_2X(2),
					b_X3 => B_3X(2),
					c_X0 => C_2X(3),
					w_XX3 =>W_3X3(2)
				);

	-- A30, B03, c32
	D_UNIT15: dot_unit_core port map(
					clk => clk_s,
					rst => rst_s,
					a_X0 => A_3X(0),
					a_X1 => A_3X(1),
					a_X2 => A_3X(2),
					a_X3 => A_3X(3),
					b_X0 => B_0X(3),
					b_X1 => B_1X(3),
					b_X2 => B_2X(3),
					b_X3 => B_3X(3),
					c_X0 => C_3X(3),
					w_XX3 =>W_3X3(3)
				);

end ar;
