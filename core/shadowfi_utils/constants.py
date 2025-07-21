import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../"))
SCRIPTS_PATH = os.path.join(ROOT,"core","shadowfi_core/sabotuer_scripts")
SBTR_CELLS = os.path.join(ROOT,"core","shadowfi_core/sbtr_cells")

#TARGET_MODULES = os.path.abspath("Config_files/target_modules_original.yml")

#SCRIPTS_PATH = os.path.abspath("core/shadowfi_core/sabotuer_scripts")
#SBTR_CELLS = os.path.abspath("core/shadowfi_core/sbtr_cells")
#TARGET_MODULES = os.path.abspath("Config_files/target_modules_original.yml")

F_LIST_NAME = "fault_list.csv"
F_SIM_REPORT = "fsim_report.csv"

DEFAULT_DICT = {
    "design_info": {
        "inc_directories": [],
        "src_list_files": [],
        "module_params": []},
    "testbench_info": {
        "make_sim_tb": False,
        "inc_directories": [],
        "tb_list_files": [],
        "tb_target_file": "",
        "tb_top": "",
        "tb_params": [],
        "verilator_params": "--trace --trace-depth 1",
        "make_cmd": ""},
    "target_modules": [],
    "hierarchical_component": [], 
}


MAKEFILE_SBTR = """
ifneq ($(words $(CURDIR)),1)
 $(error Unsupported: GNU Make cannot build in directories containing spaces, build elsewhere: '$(CURDIR)')
endif

ifeq ($(VERILATOR_ROOT),)
VERILATOR = verilator
VERILATOR_COVERAGE = verilator_coverage
else
export VERILATOR_ROOT
VERILATOR = $(VERILATOR_ROOT)/bin/verilator
VERILATOR_COVERAGE = $(VERILATOR_ROOT)/bin/verilator_coverage
endif

VERILATOR_PARAMS =
VERILATOR_PARAMS += --timing 
VERILATOR_PARAMS += --binary
VERILATOR_PARAMS += -Wno-lint -Wno-ASSIGNIN -Wno-PINMISSING
VERILATOR_PARAMS += {verilator_params}
VERILATOR_PARAMS += -O3 --timescale-override 1ns/1ps
VERILATOR_PARAMS += -max-num-width 80000
#VERILATOR_PARAMS += -o Vtop

default: compile

compile: 
	@echo "-- VERILATE/COMPILE SBTR --------------------"
	$(VERILATOR) $(VERILATOR_PARAMS) -f verilator_sbtr.f 
	@echo "-- DONE -------------------------------------"


######################################################################
# Other targets

show-config:
	$(VERILATOR) -V

maintainer-copy::
clean mostlyclean distclean maintainer-clean::
	-rm -rf obj_dir logs *.log *.dmp *.vpd core *.txt *.vcd
        """
    #return(MAKEFILE_SBTR)