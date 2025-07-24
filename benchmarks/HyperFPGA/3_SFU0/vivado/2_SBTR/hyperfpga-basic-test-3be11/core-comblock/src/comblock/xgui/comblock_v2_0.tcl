
# Loading additional proc with user specified bodies to compute parameter values.
source [file join [file dirname [file dirname [info script]]] gui/comblock_v2_0.gtcl]

# Definitional proc to organize widgets for parameters.
proc init_gui { IPINST } {
  ipgui::add_param $IPINST -name "Component_Name"
  #Adding Group
  set Registers [ipgui::add_group $IPINST -name "Registers" -layout horizontal]
  set_property tooltip {Registers} ${Registers}
  #Adding Group
  set Input_(FPGA_to_PROC) [ipgui::add_group $IPINST -name "Input (FPGA to PROC)" -parent ${Registers}]
  set REGS_IN_ENA [ipgui::add_param $IPINST -name "REGS_IN_ENA" -parent ${Input_(FPGA_to_PROC)}]
  set_property tooltip {Enable the input registers (FPGA to PROC)} ${REGS_IN_ENA}
  set REGS_IN_DWIDTH [ipgui::add_param $IPINST -name "REGS_IN_DWIDTH" -parent ${Input_(FPGA_to_PROC)}]
  set_property tooltip {Data Width (bits) of the input registers} ${REGS_IN_DWIDTH}
  set REGS_IN_DEPTH [ipgui::add_param $IPINST -name "REGS_IN_DEPTH" -parent ${Input_(FPGA_to_PROC)}]
  set_property tooltip {Quantity of input registers} ${REGS_IN_DEPTH}

  #Adding Group
  set Output_(PROC_to_FPGA) [ipgui::add_group $IPINST -name "Output (PROC to FPGA)" -parent ${Registers}]
  set REGS_OUT_ENA [ipgui::add_param $IPINST -name "REGS_OUT_ENA" -parent ${Output_(PROC_to_FPGA)}]
  set_property tooltip {Enable the output registers (PROC to FPGA)} ${REGS_OUT_ENA}
  set REGS_OUT_DWIDTH [ipgui::add_param $IPINST -name "REGS_OUT_DWIDTH" -parent ${Output_(PROC_to_FPGA)}]
  set_property tooltip {Data Width (bits) of the output registers} ${REGS_OUT_DWIDTH}
  set REGS_OUT_DEPTH [ipgui::add_param $IPINST -name "REGS_OUT_DEPTH" -parent ${Output_(PROC_to_FPGA)}]
  set_property tooltip {Quantity of output registers} ${REGS_OUT_DEPTH}


  #Adding Group
  set True_Dual_Port_RAM_(FPGA_to_PROC,_PROC_to_FPGA) [ipgui::add_group $IPINST -name "True Dual Port RAM (FPGA to PROC, PROC to FPGA)"]
  set_property tooltip {True Dual Port RAM (FPGA to PROC, PROC to FPGA)} ${True_Dual_Port_RAM_(FPGA_to_PROC,_PROC_to_FPGA)}
  set DRAM_IO_ENA [ipgui::add_param $IPINST -name "DRAM_IO_ENA" -parent ${True_Dual_Port_RAM_(FPGA_to_PROC,_PROC_to_FPGA)}]
  set_property tooltip {Enable the True Dual Port RAM} ${DRAM_IO_ENA}
  set DRAM_IO_DWIDTH [ipgui::add_param $IPINST -name "DRAM_IO_DWIDTH" -parent ${True_Dual_Port_RAM_(FPGA_to_PROC,_PROC_to_FPGA)}]
  set_property tooltip {Data Width (bits) of the DRAM} ${DRAM_IO_DWIDTH}
  set DRAM_IO_AWIDTH [ipgui::add_param $IPINST -name "DRAM_IO_AWIDTH" -parent ${True_Dual_Port_RAM_(FPGA_to_PROC,_PROC_to_FPGA)}]
  set_property tooltip {Address Width (bits) of the DRAM} ${DRAM_IO_AWIDTH}
  set DRAM_IO_DEPTH [ipgui::add_param $IPINST -name "DRAM_IO_DEPTH" -parent ${True_Dual_Port_RAM_(FPGA_to_PROC,_PROC_to_FPGA)}]
  set_property tooltip {Quantity of memory positions (0 to use the full address range)} ${DRAM_IO_DEPTH}

  #Adding Group
  set FIFOs [ipgui::add_group $IPINST -name "FIFOs" -layout horizontal]
  #Adding Group
  set Input [ipgui::add_group $IPINST -name "Input" -parent ${FIFOs} -display_name {Input (FPGA to PROC)}]
  set_property tooltip {Input (FPGA to PROC)} ${Input}
  set FIFO_IN_ENA [ipgui::add_param $IPINST -name "FIFO_IN_ENA" -parent ${Input}]
  set_property tooltip {Enable the input FIFO (FPGA to PROC)} ${FIFO_IN_ENA}
  set FIFO_IN_DWIDTH [ipgui::add_param $IPINST -name "FIFO_IN_DWIDTH" -parent ${Input}]
  set_property tooltip {Data Width (bits) of the input FIFO} ${FIFO_IN_DWIDTH}
  set FIFO_IN_DEPTH [ipgui::add_param $IPINST -name "FIFO_IN_DEPTH" -parent ${Input}]
  set_property tooltip {Quantity of memory positions} ${FIFO_IN_DEPTH}
  set FIFO_IN_AFOFFSET [ipgui::add_param $IPINST -name "FIFO_IN_AFOFFSET" -parent ${Input}]
  set_property tooltip {Almost Full Offset of the input FIFO} ${FIFO_IN_AFOFFSET}
  set FIFO_IN_AEOFFSET [ipgui::add_param $IPINST -name "FIFO_IN_AEOFFSET" -parent ${Input}]
  set_property tooltip {Almost Empty Offset of the input FIFO} ${FIFO_IN_AEOFFSET}

  #Adding Group
  set Output [ipgui::add_group $IPINST -name "Output" -parent ${FIFOs} -display_name {Output (PROC to FPGA)}]
  set_property tooltip {Output (PROC to FPGA)} ${Output}
  set FIFO_OUT_ENA [ipgui::add_param $IPINST -name "FIFO_OUT_ENA" -parent ${Output}]
  set_property tooltip {Enable the output FIFO (PROC to FPGA)} ${FIFO_OUT_ENA}
  set FIFO_OUT_DWIDTH [ipgui::add_param $IPINST -name "FIFO_OUT_DWIDTH" -parent ${Output}]
  set_property tooltip {Data Width (bits) of the output FIFO} ${FIFO_OUT_DWIDTH}
  set FIFO_OUT_DEPTH [ipgui::add_param $IPINST -name "FIFO_OUT_DEPTH" -parent ${Output}]
  set_property tooltip {Quantity of memory positions} ${FIFO_OUT_DEPTH}
  set FIFO_OUT_AFOFFSET [ipgui::add_param $IPINST -name "FIFO_OUT_AFOFFSET" -parent ${Output}]
  set_property tooltip {Almost Full Offset of the output FIFO} ${FIFO_OUT_AFOFFSET}
  set FIFO_OUT_AEOFFSET [ipgui::add_param $IPINST -name "FIFO_OUT_AEOFFSET" -parent ${Output}]
  set_property tooltip {Almost Empty Offset of the output FIFO} ${FIFO_OUT_AEOFFSET}



}

proc update_PARAM_VALUE.DRAM_IO_AWIDTH { PARAM_VALUE.DRAM_IO_AWIDTH PARAM_VALUE.DRAM_IO_ENA } {
	# Procedure called to update DRAM_IO_AWIDTH when any of the dependent parameters in the arguments change
	
	set DRAM_IO_AWIDTH ${PARAM_VALUE.DRAM_IO_AWIDTH}
	set DRAM_IO_ENA ${PARAM_VALUE.DRAM_IO_ENA}
	set values(DRAM_IO_ENA) [get_property value $DRAM_IO_ENA]
	if { [gen_USERPARAMETER_DRAM_IO_AWIDTH_ENABLEMENT $values(DRAM_IO_ENA)] } {
		set_property enabled true $DRAM_IO_AWIDTH
	} else {
		set_property enabled false $DRAM_IO_AWIDTH
	}
}

proc validate_PARAM_VALUE.DRAM_IO_AWIDTH { PARAM_VALUE.DRAM_IO_AWIDTH } {
	# Procedure called to validate DRAM_IO_AWIDTH
	return true
}

proc update_PARAM_VALUE.DRAM_IO_DEPTH { PARAM_VALUE.DRAM_IO_DEPTH PARAM_VALUE.DRAM_IO_ENA } {
	# Procedure called to update DRAM_IO_DEPTH when any of the dependent parameters in the arguments change

	set DRAM_IO_DEPTH ${PARAM_VALUE.DRAM_IO_DEPTH}
	set DRAM_IO_ENA ${PARAM_VALUE.DRAM_IO_ENA}
	set values(DRAM_IO_ENA) [get_property value $DRAM_IO_ENA]
	if { [gen_USERPARAMETER_DRAM_IO_DEPTH_ENABLEMENT $values(DRAM_IO_ENA)] } {
		set_property enabled true $DRAM_IO_DEPTH
	} else {
		set_property enabled false $DRAM_IO_DEPTH
	}
}

proc validate_PARAM_VALUE.DRAM_IO_DEPTH { PARAM_VALUE.DRAM_IO_DEPTH } {
	# Procedure called to validate DRAM_IO_DEPTH
	return true
}

proc update_PARAM_VALUE.DRAM_IO_DWIDTH { PARAM_VALUE.DRAM_IO_DWIDTH PARAM_VALUE.DRAM_IO_ENA } {
	# Procedure called to update DRAM_IO_DWIDTH when any of the dependent parameters in the arguments change
	
	set DRAM_IO_DWIDTH ${PARAM_VALUE.DRAM_IO_DWIDTH}
	set DRAM_IO_ENA ${PARAM_VALUE.DRAM_IO_ENA}
	set values(DRAM_IO_ENA) [get_property value $DRAM_IO_ENA]
	if { [gen_USERPARAMETER_DRAM_IO_DWIDTH_ENABLEMENT $values(DRAM_IO_ENA)] } {
		set_property enabled true $DRAM_IO_DWIDTH
	} else {
		set_property enabled false $DRAM_IO_DWIDTH
	}
}

proc validate_PARAM_VALUE.DRAM_IO_DWIDTH { PARAM_VALUE.DRAM_IO_DWIDTH } {
	# Procedure called to validate DRAM_IO_DWIDTH
	return true
}

proc update_PARAM_VALUE.FIFO_IN_AEOFFSET { PARAM_VALUE.FIFO_IN_AEOFFSET PARAM_VALUE.FIFO_IN_ENA } {
	# Procedure called to update FIFO_IN_AEOFFSET when any of the dependent parameters in the arguments change
	
	set FIFO_IN_AEOFFSET ${PARAM_VALUE.FIFO_IN_AEOFFSET}
	set FIFO_IN_ENA ${PARAM_VALUE.FIFO_IN_ENA}
	set values(FIFO_IN_ENA) [get_property value $FIFO_IN_ENA]
	if { [gen_USERPARAMETER_FIFO_IN_AEOFFSET_ENABLEMENT $values(FIFO_IN_ENA)] } {
		set_property enabled true $FIFO_IN_AEOFFSET
	} else {
		set_property enabled false $FIFO_IN_AEOFFSET
	}
}

proc validate_PARAM_VALUE.FIFO_IN_AEOFFSET { PARAM_VALUE.FIFO_IN_AEOFFSET } {
	# Procedure called to validate FIFO_IN_AEOFFSET
	return true
}

proc update_PARAM_VALUE.FIFO_IN_AFOFFSET { PARAM_VALUE.FIFO_IN_AFOFFSET PARAM_VALUE.FIFO_IN_ENA } {
	# Procedure called to update FIFO_IN_AFOFFSET when any of the dependent parameters in the arguments change
	
	set FIFO_IN_AFOFFSET ${PARAM_VALUE.FIFO_IN_AFOFFSET}
	set FIFO_IN_ENA ${PARAM_VALUE.FIFO_IN_ENA}
	set values(FIFO_IN_ENA) [get_property value $FIFO_IN_ENA]
	if { [gen_USERPARAMETER_FIFO_IN_AFOFFSET_ENABLEMENT $values(FIFO_IN_ENA)] } {
		set_property enabled true $FIFO_IN_AFOFFSET
	} else {
		set_property enabled false $FIFO_IN_AFOFFSET
	}
}

proc validate_PARAM_VALUE.FIFO_IN_AFOFFSET { PARAM_VALUE.FIFO_IN_AFOFFSET } {
	# Procedure called to validate FIFO_IN_AFOFFSET
	return true
}

proc update_PARAM_VALUE.FIFO_IN_DEPTH { PARAM_VALUE.FIFO_IN_DEPTH PARAM_VALUE.FIFO_IN_ENA } {
	# Procedure called to update FIFO_IN_DEPTH when any of the dependent parameters in the arguments change
	
	set FIFO_IN_DEPTH ${PARAM_VALUE.FIFO_IN_DEPTH}
	set FIFO_IN_ENA ${PARAM_VALUE.FIFO_IN_ENA}
	set values(FIFO_IN_ENA) [get_property value $FIFO_IN_ENA]
	if { [gen_USERPARAMETER_FIFO_IN_DEPTH_ENABLEMENT $values(FIFO_IN_ENA)] } {
		set_property enabled true $FIFO_IN_DEPTH
	} else {
		set_property enabled false $FIFO_IN_DEPTH
	}
}

proc validate_PARAM_VALUE.FIFO_IN_DEPTH { PARAM_VALUE.FIFO_IN_DEPTH } {
	# Procedure called to validate FIFO_IN_DEPTH
	return true
}

proc update_PARAM_VALUE.FIFO_IN_DWIDTH { PARAM_VALUE.FIFO_IN_DWIDTH PARAM_VALUE.FIFO_IN_ENA } {
	# Procedure called to update FIFO_IN_DWIDTH when any of the dependent parameters in the arguments change
	
	set FIFO_IN_DWIDTH ${PARAM_VALUE.FIFO_IN_DWIDTH}
	set FIFO_IN_ENA ${PARAM_VALUE.FIFO_IN_ENA}
	set values(FIFO_IN_ENA) [get_property value $FIFO_IN_ENA]
	if { [gen_USERPARAMETER_FIFO_IN_DWIDTH_ENABLEMENT $values(FIFO_IN_ENA)] } {
		set_property enabled true $FIFO_IN_DWIDTH
	} else {
		set_property enabled false $FIFO_IN_DWIDTH
	}
}

proc validate_PARAM_VALUE.FIFO_IN_DWIDTH { PARAM_VALUE.FIFO_IN_DWIDTH } {
	# Procedure called to validate FIFO_IN_DWIDTH
	return true
}

proc update_PARAM_VALUE.FIFO_OUT_AEOFFSET { PARAM_VALUE.FIFO_OUT_AEOFFSET PARAM_VALUE.FIFO_OUT_ENA } {
	# Procedure called to update FIFO_OUT_AEOFFSET when any of the dependent parameters in the arguments change
	
	set FIFO_OUT_AEOFFSET ${PARAM_VALUE.FIFO_OUT_AEOFFSET}
	set FIFO_OUT_ENA ${PARAM_VALUE.FIFO_OUT_ENA}
	set values(FIFO_OUT_ENA) [get_property value $FIFO_OUT_ENA]
	if { [gen_USERPARAMETER_FIFO_OUT_AEOFFSET_ENABLEMENT $values(FIFO_OUT_ENA)] } {
		set_property enabled true $FIFO_OUT_AEOFFSET
	} else {
		set_property enabled false $FIFO_OUT_AEOFFSET
	}
}

proc validate_PARAM_VALUE.FIFO_OUT_AEOFFSET { PARAM_VALUE.FIFO_OUT_AEOFFSET } {
	# Procedure called to validate FIFO_OUT_AEOFFSET
	return true
}

proc update_PARAM_VALUE.FIFO_OUT_AFOFFSET { PARAM_VALUE.FIFO_OUT_AFOFFSET PARAM_VALUE.FIFO_OUT_ENA } {
	# Procedure called to update FIFO_OUT_AFOFFSET when any of the dependent parameters in the arguments change
	
	set FIFO_OUT_AFOFFSET ${PARAM_VALUE.FIFO_OUT_AFOFFSET}
	set FIFO_OUT_ENA ${PARAM_VALUE.FIFO_OUT_ENA}
	set values(FIFO_OUT_ENA) [get_property value $FIFO_OUT_ENA]
	if { [gen_USERPARAMETER_FIFO_OUT_AFOFFSET_ENABLEMENT $values(FIFO_OUT_ENA)] } {
		set_property enabled true $FIFO_OUT_AFOFFSET
	} else {
		set_property enabled false $FIFO_OUT_AFOFFSET
	}
}

proc validate_PARAM_VALUE.FIFO_OUT_AFOFFSET { PARAM_VALUE.FIFO_OUT_AFOFFSET } {
	# Procedure called to validate FIFO_OUT_AFOFFSET
	return true
}

proc update_PARAM_VALUE.FIFO_OUT_DEPTH { PARAM_VALUE.FIFO_OUT_DEPTH PARAM_VALUE.FIFO_OUT_ENA } {
	# Procedure called to update FIFO_OUT_DEPTH when any of the dependent parameters in the arguments change
	
	set FIFO_OUT_DEPTH ${PARAM_VALUE.FIFO_OUT_DEPTH}
	set FIFO_OUT_ENA ${PARAM_VALUE.FIFO_OUT_ENA}
	set values(FIFO_OUT_ENA) [get_property value $FIFO_OUT_ENA]
	if { [gen_USERPARAMETER_FIFO_OUT_DEPTH_ENABLEMENT $values(FIFO_OUT_ENA)] } {
		set_property enabled true $FIFO_OUT_DEPTH
	} else {
		set_property enabled false $FIFO_OUT_DEPTH
	}
}

proc validate_PARAM_VALUE.FIFO_OUT_DEPTH { PARAM_VALUE.FIFO_OUT_DEPTH } {
	# Procedure called to validate FIFO_OUT_DEPTH
	return true
}

proc update_PARAM_VALUE.FIFO_OUT_DWIDTH { PARAM_VALUE.FIFO_OUT_DWIDTH PARAM_VALUE.FIFO_OUT_ENA } {
	# Procedure called to update FIFO_OUT_DWIDTH when any of the dependent parameters in the arguments change
	
	set FIFO_OUT_DWIDTH ${PARAM_VALUE.FIFO_OUT_DWIDTH}
	set FIFO_OUT_ENA ${PARAM_VALUE.FIFO_OUT_ENA}
	set values(FIFO_OUT_ENA) [get_property value $FIFO_OUT_ENA]
	if { [gen_USERPARAMETER_FIFO_OUT_DWIDTH_ENABLEMENT $values(FIFO_OUT_ENA)] } {
		set_property enabled true $FIFO_OUT_DWIDTH
	} else {
		set_property enabled false $FIFO_OUT_DWIDTH
	}
}

proc validate_PARAM_VALUE.FIFO_OUT_DWIDTH { PARAM_VALUE.FIFO_OUT_DWIDTH } {
	# Procedure called to validate FIFO_OUT_DWIDTH
	return true
}

proc update_PARAM_VALUE.REGS_IN_DEPTH { PARAM_VALUE.REGS_IN_DEPTH PARAM_VALUE.REGS_IN_ENA } {
	# Procedure called to update REGS_IN_DEPTH when any of the dependent parameters in the arguments change
	
	set REGS_IN_DEPTH ${PARAM_VALUE.REGS_IN_DEPTH}
	set REGS_IN_ENA ${PARAM_VALUE.REGS_IN_ENA}
	set values(REGS_IN_ENA) [get_property value $REGS_IN_ENA]
	if { [gen_USERPARAMETER_REGS_IN_DEPTH_ENABLEMENT $values(REGS_IN_ENA)] } {
		set_property enabled true $REGS_IN_DEPTH
	} else {
		set_property enabled false $REGS_IN_DEPTH
	}
}

proc validate_PARAM_VALUE.REGS_IN_DEPTH { PARAM_VALUE.REGS_IN_DEPTH } {
	# Procedure called to validate REGS_IN_DEPTH
	return true
}

proc update_PARAM_VALUE.REGS_IN_DWIDTH { PARAM_VALUE.REGS_IN_DWIDTH PARAM_VALUE.REGS_IN_ENA } {
	# Procedure called to update REGS_IN_DWIDTH when any of the dependent parameters in the arguments change
	
	set REGS_IN_DWIDTH ${PARAM_VALUE.REGS_IN_DWIDTH}
	set REGS_IN_ENA ${PARAM_VALUE.REGS_IN_ENA}
	set values(REGS_IN_ENA) [get_property value $REGS_IN_ENA]
	if { [gen_USERPARAMETER_REGS_IN_DWIDTH_ENABLEMENT $values(REGS_IN_ENA)] } {
		set_property enabled true $REGS_IN_DWIDTH
	} else {
		set_property enabled false $REGS_IN_DWIDTH
	}
}

proc validate_PARAM_VALUE.REGS_IN_DWIDTH { PARAM_VALUE.REGS_IN_DWIDTH } {
	# Procedure called to validate REGS_IN_DWIDTH
	return true
}

proc update_PARAM_VALUE.REGS_OUT_DEPTH { PARAM_VALUE.REGS_OUT_DEPTH PARAM_VALUE.REGS_OUT_ENA } {
	# Procedure called to update REGS_OUT_DEPTH when any of the dependent parameters in the arguments change
	
	set REGS_OUT_DEPTH ${PARAM_VALUE.REGS_OUT_DEPTH}
	set REGS_OUT_ENA ${PARAM_VALUE.REGS_OUT_ENA}
	set values(REGS_OUT_ENA) [get_property value $REGS_OUT_ENA]
	if { [gen_USERPARAMETER_REGS_OUT_DEPTH_ENABLEMENT $values(REGS_OUT_ENA)] } {
		set_property enabled true $REGS_OUT_DEPTH
	} else {
		set_property enabled false $REGS_OUT_DEPTH
	}
}

proc validate_PARAM_VALUE.REGS_OUT_DEPTH { PARAM_VALUE.REGS_OUT_DEPTH } {
	# Procedure called to validate REGS_OUT_DEPTH
	return true
}

proc update_PARAM_VALUE.REGS_OUT_DWIDTH { PARAM_VALUE.REGS_OUT_DWIDTH PARAM_VALUE.REGS_OUT_ENA } {
	# Procedure called to update REGS_OUT_DWIDTH when any of the dependent parameters in the arguments change
	
	set REGS_OUT_DWIDTH ${PARAM_VALUE.REGS_OUT_DWIDTH}
	set REGS_OUT_ENA ${PARAM_VALUE.REGS_OUT_ENA}
	set values(REGS_OUT_ENA) [get_property value $REGS_OUT_ENA]
	if { [gen_USERPARAMETER_REGS_OUT_DWIDTH_ENABLEMENT $values(REGS_OUT_ENA)] } {
		set_property enabled true $REGS_OUT_DWIDTH
	} else {
		set_property enabled false $REGS_OUT_DWIDTH
	}
}

proc validate_PARAM_VALUE.REGS_OUT_DWIDTH { PARAM_VALUE.REGS_OUT_DWIDTH } {
	# Procedure called to validate REGS_OUT_DWIDTH
	return true
}

proc update_PARAM_VALUE.REGS_OUT_ENA { PARAM_VALUE.REGS_OUT_ENA PARAM_VALUE.REGS_IN_ENA PARAM_VALUE.DRAM_IO_ENA PARAM_VALUE.FIFO_IN_ENA PARAM_VALUE.FIFO_OUT_ENA } {
	# Procedure called to update REGS_OUT_ENA when any of the dependent parameters in the arguments change
	
	set REGS_OUT_ENA ${PARAM_VALUE.REGS_OUT_ENA}
	set REGS_IN_ENA ${PARAM_VALUE.REGS_IN_ENA}
	set DRAM_IO_ENA ${PARAM_VALUE.DRAM_IO_ENA}
	set FIFO_IN_ENA ${PARAM_VALUE.FIFO_IN_ENA}
	set FIFO_OUT_ENA ${PARAM_VALUE.FIFO_OUT_ENA}
	set values(REGS_IN_ENA) [get_property value $REGS_IN_ENA]
	set values(DRAM_IO_ENA) [get_property value $DRAM_IO_ENA]
	set values(FIFO_IN_ENA) [get_property value $FIFO_IN_ENA]
	set values(FIFO_OUT_ENA) [get_property value $FIFO_OUT_ENA]
	if { [gen_USERPARAMETER_REGS_OUT_ENA_ENABLEMENT $values(REGS_IN_ENA) $values(DRAM_IO_ENA) $values(FIFO_IN_ENA) $values(FIFO_OUT_ENA)] } {
		set_property enabled true $REGS_OUT_ENA
	} else {
		set_property enabled false $REGS_OUT_ENA
		set_property value [gen_USERPARAMETER_REGS_OUT_ENA_VALUE $values(REGS_IN_ENA) $values(DRAM_IO_ENA) $values(FIFO_IN_ENA) $values(FIFO_OUT_ENA)] $REGS_OUT_ENA
	}
}

proc validate_PARAM_VALUE.REGS_OUT_ENA { PARAM_VALUE.REGS_OUT_ENA } {
	# Procedure called to validate REGS_OUT_ENA
	return true
}

proc update_PARAM_VALUE.C_AXIF_ARUSER_WIDTH { PARAM_VALUE.C_AXIF_ARUSER_WIDTH } {
	# Procedure called to update C_AXIF_ARUSER_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXIF_ARUSER_WIDTH { PARAM_VALUE.C_AXIF_ARUSER_WIDTH } {
	# Procedure called to validate C_AXIF_ARUSER_WIDTH
	return true
}

proc update_PARAM_VALUE.C_AXIF_AWUSER_WIDTH { PARAM_VALUE.C_AXIF_AWUSER_WIDTH } {
	# Procedure called to update C_AXIF_AWUSER_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXIF_AWUSER_WIDTH { PARAM_VALUE.C_AXIF_AWUSER_WIDTH } {
	# Procedure called to validate C_AXIF_AWUSER_WIDTH
	return true
}

proc update_PARAM_VALUE.C_AXIF_BASEADDR { PARAM_VALUE.C_AXIF_BASEADDR } {
	# Procedure called to update C_AXIF_BASEADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXIF_BASEADDR { PARAM_VALUE.C_AXIF_BASEADDR } {
	# Procedure called to validate C_AXIF_BASEADDR
	return true
}

proc update_PARAM_VALUE.C_AXIF_BUSER_WIDTH { PARAM_VALUE.C_AXIF_BUSER_WIDTH } {
	# Procedure called to update C_AXIF_BUSER_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXIF_BUSER_WIDTH { PARAM_VALUE.C_AXIF_BUSER_WIDTH } {
	# Procedure called to validate C_AXIF_BUSER_WIDTH
	return true
}

proc update_PARAM_VALUE.C_AXIF_HIGHADDR { PARAM_VALUE.C_AXIF_HIGHADDR } {
	# Procedure called to update C_AXIF_HIGHADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXIF_HIGHADDR { PARAM_VALUE.C_AXIF_HIGHADDR } {
	# Procedure called to validate C_AXIF_HIGHADDR
	return true
}

proc update_PARAM_VALUE.C_AXIF_RUSER_WIDTH { PARAM_VALUE.C_AXIF_RUSER_WIDTH } {
	# Procedure called to update C_AXIF_RUSER_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXIF_RUSER_WIDTH { PARAM_VALUE.C_AXIF_RUSER_WIDTH } {
	# Procedure called to validate C_AXIF_RUSER_WIDTH
	return true
}

proc update_PARAM_VALUE.C_AXIF_WUSER_WIDTH { PARAM_VALUE.C_AXIF_WUSER_WIDTH } {
	# Procedure called to update C_AXIF_WUSER_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXIF_WUSER_WIDTH { PARAM_VALUE.C_AXIF_WUSER_WIDTH } {
	# Procedure called to validate C_AXIF_WUSER_WIDTH
	return true
}

proc update_PARAM_VALUE.C_AXIL_BASEADDR { PARAM_VALUE.C_AXIL_BASEADDR } {
	# Procedure called to update C_AXIL_BASEADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXIL_BASEADDR { PARAM_VALUE.C_AXIL_BASEADDR } {
	# Procedure called to validate C_AXIL_BASEADDR
	return true
}

proc update_PARAM_VALUE.C_AXIL_HIGHADDR { PARAM_VALUE.C_AXIL_HIGHADDR } {
	# Procedure called to update C_AXIL_HIGHADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXIL_HIGHADDR { PARAM_VALUE.C_AXIL_HIGHADDR } {
	# Procedure called to validate C_AXIL_HIGHADDR
	return true
}

proc update_PARAM_VALUE.DRAM_IO_ENA { PARAM_VALUE.DRAM_IO_ENA } {
	# Procedure called to update DRAM_IO_ENA when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.DRAM_IO_ENA { PARAM_VALUE.DRAM_IO_ENA } {
	# Procedure called to validate DRAM_IO_ENA
	return true
}

proc update_PARAM_VALUE.FIFO_IN_ENA { PARAM_VALUE.FIFO_IN_ENA } {
	# Procedure called to update FIFO_IN_ENA when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.FIFO_IN_ENA { PARAM_VALUE.FIFO_IN_ENA } {
	# Procedure called to validate FIFO_IN_ENA
	return true
}

proc update_PARAM_VALUE.FIFO_OUT_ENA { PARAM_VALUE.FIFO_OUT_ENA } {
	# Procedure called to update FIFO_OUT_ENA when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.FIFO_OUT_ENA { PARAM_VALUE.FIFO_OUT_ENA } {
	# Procedure called to validate FIFO_OUT_ENA
	return true
}

proc update_PARAM_VALUE.REGS_IN_ENA { PARAM_VALUE.REGS_IN_ENA } {
	# Procedure called to update REGS_IN_ENA when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.REGS_IN_ENA { PARAM_VALUE.REGS_IN_ENA } {
	# Procedure called to validate REGS_IN_ENA
	return true
}

proc update_PARAM_VALUE.C_AXIF_ID_WIDTH { PARAM_VALUE.C_AXIF_ID_WIDTH } {
	# Procedure called to update C_AXIF_ID_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_AXIF_ID_WIDTH { PARAM_VALUE.C_AXIF_ID_WIDTH } {
	# Procedure called to validate C_AXIF_ID_WIDTH
	return true
}


proc update_MODELPARAM_VALUE.REGS_IN_ENA { MODELPARAM_VALUE.REGS_IN_ENA PARAM_VALUE.REGS_IN_ENA } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.REGS_IN_ENA}] ${MODELPARAM_VALUE.REGS_IN_ENA}
}

proc update_MODELPARAM_VALUE.REGS_IN_DWIDTH { MODELPARAM_VALUE.REGS_IN_DWIDTH PARAM_VALUE.REGS_IN_DWIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.REGS_IN_DWIDTH}] ${MODELPARAM_VALUE.REGS_IN_DWIDTH}
}

proc update_MODELPARAM_VALUE.REGS_IN_DEPTH { MODELPARAM_VALUE.REGS_IN_DEPTH PARAM_VALUE.REGS_IN_DEPTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.REGS_IN_DEPTH}] ${MODELPARAM_VALUE.REGS_IN_DEPTH}
}

proc update_MODELPARAM_VALUE.REGS_OUT_ENA { MODELPARAM_VALUE.REGS_OUT_ENA PARAM_VALUE.REGS_OUT_ENA } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.REGS_OUT_ENA}] ${MODELPARAM_VALUE.REGS_OUT_ENA}
}

proc update_MODELPARAM_VALUE.REGS_OUT_DWIDTH { MODELPARAM_VALUE.REGS_OUT_DWIDTH PARAM_VALUE.REGS_OUT_DWIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.REGS_OUT_DWIDTH}] ${MODELPARAM_VALUE.REGS_OUT_DWIDTH}
}

proc update_MODELPARAM_VALUE.REGS_OUT_DEPTH { MODELPARAM_VALUE.REGS_OUT_DEPTH PARAM_VALUE.REGS_OUT_DEPTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.REGS_OUT_DEPTH}] ${MODELPARAM_VALUE.REGS_OUT_DEPTH}
}

proc update_MODELPARAM_VALUE.DRAM_IO_ENA { MODELPARAM_VALUE.DRAM_IO_ENA PARAM_VALUE.DRAM_IO_ENA } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.DRAM_IO_ENA}] ${MODELPARAM_VALUE.DRAM_IO_ENA}
}

proc update_MODELPARAM_VALUE.DRAM_IO_DWIDTH { MODELPARAM_VALUE.DRAM_IO_DWIDTH PARAM_VALUE.DRAM_IO_DWIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.DRAM_IO_DWIDTH}] ${MODELPARAM_VALUE.DRAM_IO_DWIDTH}
}

proc update_MODELPARAM_VALUE.DRAM_IO_AWIDTH { MODELPARAM_VALUE.DRAM_IO_AWIDTH PARAM_VALUE.DRAM_IO_AWIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.DRAM_IO_AWIDTH}] ${MODELPARAM_VALUE.DRAM_IO_AWIDTH}
}

proc update_MODELPARAM_VALUE.DRAM_IO_DEPTH { MODELPARAM_VALUE.DRAM_IO_DEPTH PARAM_VALUE.DRAM_IO_DEPTH PARAM_VALUE.DRAM_IO_AWIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set DRAM_IO_AWIDTH [get_property value ${PARAM_VALUE.DRAM_IO_AWIDTH}]
	set DRAM_IO_DEPTH [get_property value ${PARAM_VALUE.DRAM_IO_DEPTH}]
	if {$DRAM_IO_AWIDTH >= 26} {
		set DRAM_IO_AWIDTH 26
	}
	if {$DRAM_IO_DEPTH == 0} {
		set_property value [expr {2 ** $DRAM_IO_AWIDTH} - 1] ${MODELPARAM_VALUE.DRAM_IO_DEPTH}
	} else {
		set_property value $DRAM_IO_DEPTH ${MODELPARAM_VALUE.DRAM_IO_DEPTH}
	}
}

proc update_MODELPARAM_VALUE.FIFO_IN_ENA { MODELPARAM_VALUE.FIFO_IN_ENA PARAM_VALUE.FIFO_IN_ENA } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.FIFO_IN_ENA}] ${MODELPARAM_VALUE.FIFO_IN_ENA}
}

proc update_MODELPARAM_VALUE.FIFO_IN_DWIDTH { MODELPARAM_VALUE.FIFO_IN_DWIDTH PARAM_VALUE.FIFO_IN_DWIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.FIFO_IN_DWIDTH}] ${MODELPARAM_VALUE.FIFO_IN_DWIDTH}
}

proc update_MODELPARAM_VALUE.FIFO_IN_DEPTH { MODELPARAM_VALUE.FIFO_IN_DEPTH PARAM_VALUE.FIFO_IN_DEPTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.FIFO_IN_DEPTH}] ${MODELPARAM_VALUE.FIFO_IN_DEPTH}
}

proc update_MODELPARAM_VALUE.FIFO_IN_AFOFFSET { MODELPARAM_VALUE.FIFO_IN_AFOFFSET PARAM_VALUE.FIFO_IN_AFOFFSET } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.FIFO_IN_AFOFFSET}] ${MODELPARAM_VALUE.FIFO_IN_AFOFFSET}
}

proc update_MODELPARAM_VALUE.FIFO_IN_AEOFFSET { MODELPARAM_VALUE.FIFO_IN_AEOFFSET PARAM_VALUE.FIFO_IN_AEOFFSET } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.FIFO_IN_AEOFFSET}] ${MODELPARAM_VALUE.FIFO_IN_AEOFFSET}
}

proc update_MODELPARAM_VALUE.FIFO_OUT_ENA { MODELPARAM_VALUE.FIFO_OUT_ENA PARAM_VALUE.FIFO_OUT_ENA } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.FIFO_OUT_ENA}] ${MODELPARAM_VALUE.FIFO_OUT_ENA}
}

proc update_MODELPARAM_VALUE.FIFO_OUT_DWIDTH { MODELPARAM_VALUE.FIFO_OUT_DWIDTH PARAM_VALUE.FIFO_OUT_DWIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.FIFO_OUT_DWIDTH}] ${MODELPARAM_VALUE.FIFO_OUT_DWIDTH}
}

proc update_MODELPARAM_VALUE.FIFO_OUT_DEPTH { MODELPARAM_VALUE.FIFO_OUT_DEPTH PARAM_VALUE.FIFO_OUT_DEPTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.FIFO_OUT_DEPTH}] ${MODELPARAM_VALUE.FIFO_OUT_DEPTH}
}

proc update_MODELPARAM_VALUE.FIFO_OUT_AFOFFSET { MODELPARAM_VALUE.FIFO_OUT_AFOFFSET PARAM_VALUE.FIFO_OUT_AFOFFSET } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.FIFO_OUT_AFOFFSET}] ${MODELPARAM_VALUE.FIFO_OUT_AFOFFSET}
}

proc update_MODELPARAM_VALUE.FIFO_OUT_AEOFFSET { MODELPARAM_VALUE.FIFO_OUT_AEOFFSET PARAM_VALUE.FIFO_OUT_AEOFFSET } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.FIFO_OUT_AEOFFSET}] ${MODELPARAM_VALUE.FIFO_OUT_AEOFFSET}
}

proc update_MODELPARAM_VALUE.C_AXIF_ID_WIDTH { MODELPARAM_VALUE.C_AXIF_ID_WIDTH PARAM_VALUE.C_AXIF_ID_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_AXIF_ID_WIDTH}] ${MODELPARAM_VALUE.C_AXIF_ID_WIDTH}
}

proc update_MODELPARAM_VALUE.C_AXIF_AWUSER_WIDTH { MODELPARAM_VALUE.C_AXIF_AWUSER_WIDTH PARAM_VALUE.C_AXIF_AWUSER_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_AXIF_AWUSER_WIDTH}] ${MODELPARAM_VALUE.C_AXIF_AWUSER_WIDTH}
}

proc update_MODELPARAM_VALUE.C_AXIF_ARUSER_WIDTH { MODELPARAM_VALUE.C_AXIF_ARUSER_WIDTH PARAM_VALUE.C_AXIF_ARUSER_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_AXIF_ARUSER_WIDTH}] ${MODELPARAM_VALUE.C_AXIF_ARUSER_WIDTH}
}

proc update_MODELPARAM_VALUE.C_AXIF_WUSER_WIDTH { MODELPARAM_VALUE.C_AXIF_WUSER_WIDTH PARAM_VALUE.C_AXIF_WUSER_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_AXIF_WUSER_WIDTH}] ${MODELPARAM_VALUE.C_AXIF_WUSER_WIDTH}
}

proc update_MODELPARAM_VALUE.C_AXIF_RUSER_WIDTH { MODELPARAM_VALUE.C_AXIF_RUSER_WIDTH PARAM_VALUE.C_AXIF_RUSER_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_AXIF_RUSER_WIDTH}] ${MODELPARAM_VALUE.C_AXIF_RUSER_WIDTH}
}

proc update_MODELPARAM_VALUE.C_AXIF_BUSER_WIDTH { MODELPARAM_VALUE.C_AXIF_BUSER_WIDTH PARAM_VALUE.C_AXIF_BUSER_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_AXIF_BUSER_WIDTH}] ${MODELPARAM_VALUE.C_AXIF_BUSER_WIDTH}
}

