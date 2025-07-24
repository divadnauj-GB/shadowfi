----------------------------------------------------------------------------
-- Company:         	Politecnico di Torino
-- Engineer:          	Josie E. Rodriguez Condia
--
-- Create Date:     		23/10/2022
-- Module Name:   	Dot Product Unit
-- Project Name:   	Open TCU, version 6-Pipes from flopoco
-- Target Devices:		
-- Tool versions:    	ModelSim
-- Description:
--
----------------------------------------------------------------------------
-- Revisions:
--  REV:        Date:          			Description:
--  1.0.a       	23/10/2022      	Created Top level file
--  1.2.a           17/11/2022          Functional verification OK 
----------------------------------------------------------------------------


-- The dot unit is the basic operation inside a tensor core unit and process the scalar product in a 4X4 matrix multiplication
--
--                         a_X0         b_X0                                 a_X1        b_X1                                a_X2         b_X2           			           a_X3           b_X3		         c_X0
--	   					____|_________|____						____|_________|____						____|_________|____						____|_________|____                |
--			FMUL0	|								|			FMUL1	|								|			FMUL2	|								|			FMUL3 |								|               |
--						|				*				|						|				*				|						|				*				|						|				*				|               |
--						|_________________|						|_________________|						|_________________|			  			|_________________|               |
--	   					_________|______________________________|________________________________|______________________________|_________________|______
--			FADD	|																																										 								                        	|
--						|																											+															 															|
--						|______________________________________________________________________________________________________________________________|
--                                                                                                                                  |
--																																w_XX3

Library IEEE;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity dot_unit_core is

			port(
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
end dot_unit_core;

architecture ar of dot_unit_core is

	-- Signals for the interconnection of the cores:
	signal a_X0_b_X0_s :std_logic_vector(31 downto 0);
	signal a_X1_b_X1_s :std_logic_vector(31 downto 0);
	signal a_X2_b_X2_s :std_logic_vector(31 downto 0);
	signal a_X3_b_X3_s :std_logic_vector(31 downto 0);
	signal c_XX_s :std_logic_vector(31 downto 0);

	signal a_X0_b_X0_plus_a_X1_b_X1_s: std_logic_vector(31 downto 0);
	signal a_X2_b_X2_plus_a_X3_b_X3_s: std_logic_vector(31 downto 0);
	signal a_plus_b_s: std_logic_vector(31 downto 0);
	signal w_XX3_s: std_logic_vector(31 downto 0);

	signal clk_s :std_logic;
	signal rst_s :std_logic;

	component FPAdd_3_pipe port (
					clk : in std_logic;
					rst : in std_logic;
         		 		X : in  std_logic_vector(31 downto 0);
          				Y : in  std_logic_vector(31 downto 0);
          				R : out  std_logic_vector(31 downto 0)
          			);
	end component;

	component FPMult_3_pipe port (
					clk : in std_logic;
					rst : in std_logic;
					  X : in  std_logic_vector(31 downto 0);
					  Y : in  std_logic_vector(31 downto 0);
					  R : out  std_logic_vector(31 downto 0)
				);
	end component;
	
begin

	c_XX_s <= c_X0;
	clk_s <= clk;
	rst_s <= rst;
	
	FMUL0: FPMult_3_pipe port map(
					clk => clk_s,
					rst => rst_s,
					  X => a_X0,
					  Y => b_X0,
					  R => a_X0_b_X0_s
					);

	FMUL1: FPMult_3_pipe port map(
					clk => clk_s,
					rst => rst_s,
					  X => a_X1,
					  Y => b_X1,
					  R => a_X1_b_X1_s
					);

	FMUL2: FPMult_3_pipe port map(
					clk => clk_s,
					rst => rst_s,
					  X => a_X2,
					  Y => b_X2,
					  R => a_X2_b_X2_s
					);

	FMUL3: FPMult_3_pipe port map(
					clk => clk_s,
					rst => rst_s,
					  X => a_X3,
					  Y => b_X3,
					  R => a_X3_b_X3_s
					);

-- adder (FADD) stage:

	ADDER0: FPAdd_3_pipe port map(
					clk => clk_s,
					rst => rst_s,
         		 		X => a_X0_b_X0_s,
          				Y => a_X1_b_X1_s,
          				R => a_X0_b_X0_plus_a_X1_b_X1_s  
          			);

	ADDER1: FPAdd_3_pipe port map(
					clk => clk_s,
					rst => rst_s,
         		 		X => a_X2_b_X2_s,
          				Y => a_X3_b_X3_s,
          				R => a_X2_b_X2_plus_a_X3_b_X3_s  
          			);

	ADDER2: FPAdd_3_pipe port map(
					clk => clk_s,
					rst => rst_s,
         		 		X => a_X0_b_X0_plus_a_X1_b_X1_s,
          				Y => a_X2_b_X2_plus_a_X3_b_X3_s,
          				R => a_plus_b_s
          			);

	ADDER3: FPAdd_3_pipe port map(
					clk => clk_s,
					rst => rst_s,
         		 		X => a_plus_b_s,
          				Y => c_XX_s,
          				R => w_XX3_s
          			);

	w_XX3 <= w_XX3_s;

end ar;
