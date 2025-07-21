----------------------------------------------------------------------------
-- Company:         	Politecnico di Torino
-- Engineer:          	Josie E. Rodriguez Condia
--
-- Create Date:     		23/10/2022
-- Module Name:   	internal packages
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


Library IEEE;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package def_package is
		constant long : natural := 32;
		type operand_array is array(natural range <>) of std_logic_vector(long - 1 downto 0);
		constant size_TCU_op: natural := 4;	 	-- size of the operands that can be executed in the complete TCU configuration. 4 for 16 x 16 size input matrices.
		constant size_sub_tensor: natural := 2;	-- Fine-grain size of the tensor DPU unit and the 3D organization.
		constant size_sub_tensor_synth_ports : natural := 7;  -- GL variable to define the size of ports of the sub-tensor unit. Used in the GL-TB

end package;



