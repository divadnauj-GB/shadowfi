import os, subprocess
import json
import subprocess
from glob import glob
import filecmp
import random
import shutil
import yaml
from omegaconf import OmegaConf
import re
from FI.sabotuer_scripts.yosys_rtl_elaboration_verilog import rtl_elaboration
from FI.sabotuer_scripts.yosys_extract_module import extract_verilog_module
from FI.sabotuer_scripts.script_injection import module_saboteur_insertion
# parser file
from FI.automatic_saboteur.parsers import get_components, get_hierarchy
# Hierarchy update functions
from FI.automatic_saboteur.hierarchy_updaters import identify_modified_components, get_components_to_copy
# Sabotage injector functions
from FI.automatic_saboteur.sabotage_injectors import extract_original_components, update_top_module, fi_infrastructure_interconnect_sequence
# Fault injection functions
from FI.fault_simulation.fault_sim_main import run_fault_simulation, run_fault_free_simulation

import argparse

import time

parser = argparse.ArgumentParser(
    description="Setup the testbench by incorporating the sbtr controller"
)

parser.add_argument(
    "-cfg",
    "--config-file",
    default="bench_config.yml",
    type=str,
    help="Input file with the configuration in yaml format",
)

parser.add_argument(
    "-b",
    "--benchmark",
    default="SFU0",
    type=str,
    help="name of the benchmark as in the bench_config.yml file",
)

parser.add_argument(
    "-m",
    "--target-instances",
    default="Config_files/target_modules_original.yml",
    type=str,
    help="configuration file containing the target modules to be used",
    required=False
)

parser.add_argument(
    "-fm",
    "--fault-model",
    default="S@",
    type=str,
    help="Fault model S@ for stuck-at SET for single envent transcient and and SEU for single event upset",
    required=False
)


parser.add_argument(
    "-nf",
    "--num-faults",
    default=10,
    type=int,
    help="Select the max number of injections",
    required=False
)

parser.add_argument(
    "-j",
    "--num-jobs",
    default=1,
    type=int,
    help="Select the max number of injections",
    required=False
)

parser.add_argument(
    "-os",
    "--only-sim",
    action="store_true",
    help="enable to run the simulation only",
    required=False
)

ROOT = os.getcwd()
SCRIPTS_PATH = os.path.abspath("FI/sabotuer_scripts")
SBTR_CELLS = os.path.abspath("FI/sbtr_cells")
TARGET_MODULES = os.path.abspath("Config_files/target_modules_original.yml")

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

#def get_makefile_str(params):
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


def read_yaml_file(file_name, mode):
    yaml_file = {}
    try:
        with open(file_name, mode) as fp:
            yaml_file = yaml.safe_load(fp)
    except OSError as err:
        print(f"The file was not saved due to {err}")
    return yaml_file



def create_makefile_tb_sbtr(
    SBTR_PATH,
    TOP_MODULE,
    SBTR_LIST_FILES=[],
    TB_PATH="",
    TB_TARGET_FILE="",
    TB_TOP="",
    TB_LIST_FILES=[],
    INC_DIRS=[],
    VERILATOR_PARAMS="--timing"
):
    if TB_TARGET_FILE == "":
        print(
            "SMS: No target TB file was selected, Please be sure you create your custom makefiles"
        )
        return

    if len(TB_LIST_FILES) == 0:
        print(
            f"SMS: The list of TB files was not provided, Searching for files in {TB_PATH}"
        )
        test_bench_files = []
        for filename in glob(f"{TB_PATH}/**/*.v", recursive=True):
            test_bench_files.append(os.path.abspath(filename))
    else:
        test_bench_files = TB_LIST_FILES

    target_tb_file = ""
    for file in test_bench_files:
        get_fname_from_path = file.split("/")[-1]
        if get_fname_from_path in TB_TARGET_FILE:
            target_tb_file = file
    test_bench_files.remove(target_tb_file)

    os.system(
        f"python {SCRIPTS_PATH}/test_bench_setup.py -f {target_tb_file} -c {TOP_MODULE}"
    )
    target_tb_file_name = target_tb_file.split("/")[-1]
    target_tb_file = target_tb_file.replace(
        target_tb_file_name, f"new_{target_tb_file_name}"
    )

    if len(SBTR_LIST_FILES) == 0:
        print(
            f"SMS: The list of SBTR files was not provided, Searching for files in {SBTR_PATH}"
        )
        sbtr_files = []
        for filename in glob(f"{SBTR_PATH}/**/*.v", recursive=True):
            sbtr_files.append(os.path.abspath(filename))
    else:
        sbtr_files = SBTR_LIST_FILES

    try:
        with open(
            os.path.abspath(os.path.join(TB_PATH, "verilator_sbtr.f")), "w"
        ) as fp:
            if len(INC_DIRS) > 0:
                for inc_dir in INC_DIRS:
                    fp.write(f"-I{os.path.abspath(inc_dir)}\n")
            else:
                fp.write(f"-I{os.path.abspath(SBTR_PATH)}\n")
                fp.write(f"-I{os.path.abspath(TB_PATH)}\n")
            for file in sbtr_files:
                fp.write(f" {os.path.abspath(file)}\n")
            if len(test_bench_files) > 0:
                for file in test_bench_files:
                    fp.write(f" {os.path.abspath(file)}\n") #it is possible to add -v or -sv to the config
            fp.write(f"{os.path.abspath(target_tb_file)}\n")
            fp.write(f"-Wno-moddup\n")
            fp.write(f"-Wno-fatal\n")
            fp.write(f"--top-module {TB_TOP}\n")
            fp.write(f"-o V{TB_TOP}\n")
    except OSError as err:
        print(f"The file was not created due to {err}")

    try:
        with open(os.path.abspath(os.path.join(TB_PATH, "Makefile_sbtr")), "w") as fp:
            fp.write(MAKEFILE_SBTR.format(verilator_params=VERILATOR_PARAMS))
    except OSError as err:
        print(f"The file was not created due to {err}")


def read_verilog_file(file_name):
    with open(file_name, "r") as f:
        verilog_code = f.read()
    return verilog_code

def write_verilog_file(file_name, data):
    with open(file_name, "w") as f:
        f.write(data)


def write_json(hierarchy, file_name="hierarchy.json"):
    with open(file_name, "w") as f:
        json.dump(hierarchy, f, indent=4)
    print("Hierarchy saved to hierarchy.json")


def main():
    timestamps = {}
    timestamps["0_start"] = time.time()
    args = parser.parse_args()
    target_benchmark=args.benchmark
    CONFIG_FILE = os.path.abspath(args.config_file)
    default_config = OmegaConf.create(DEFAULT_DICT)
    OmegaConf.resolve(default_config)
    config_file = read_yaml_file(CONFIG_FILE,"r")
    target_instances = os.path.abspath(args.target_instances)
    target_modules_f = read_yaml_file(target_instances,"r")


    conf_info = OmegaConf.merge(
        default_config, OmegaConf.create(config_file[target_benchmark]), OmegaConf.create(target_modules_f[target_benchmark])
    )
    # this are the configuration parameters of the accelerator passed trought the TB
    
    try:
        # SRC_PATH = args.path
        SRC_PATH = conf_info.design_info.src_path
        # TOP = args.top_entity
        TOP = conf_info.design_info.top_module
        SRC_INC_DIR = conf_info.design_info.inc_directories
        SRC_LIST_FILES = conf_info.design_info.src_list_files
        FI_DESIGN_PATH = conf_info.design_info.output_path
        TOP_PARAMS = conf_info.design_info.module_params
        MAKE_SIM_TB = conf_info.testbench_info.make_sim_tb

        TB_TOP = conf_info.testbench_info.tb_top
        TB_PATH = conf_info.testbench_info.tb_path
        TB_INC_DIR = conf_info.testbench_info.inc_directories
        TB_LIST_FILES = conf_info.testbench_info.tb_list_files
        TB_TARGET_FILE = conf_info.testbench_info.tb_target_file
        VERILATOR_PARAMS = conf_info.testbench_info.verilator_params
        MAX_TB_RUN_TIME = conf_info.testbench_info.sim_runtime
        MAKE_CMD = conf_info.testbench_info.make_cmd

        MODULES = conf_info.target_modules
        SELECTED_INSTANCE_PATHS = conf_info.hierarchical_component
        NUM_JOBS = args.num_jobs
        if NUM_JOBS > 1:
            print(f"SMS: The number of jobs is set to {NUM_JOBS}, be sure you have enough resources")
    except OSError:
        print(f"Mandatory configuration options were not given")
        exit(1)

    INC_DIRS = []
    INC_DIRS.extend(SRC_INC_DIR)
    INC_DIRS.extend(TB_INC_DIR)
    print(SRC_INC_DIR,TB_INC_DIR,INC_DIRS)

    FAULT_MODEL = args.fault_model
    
    MAX_NUM_INJ = args.num_faults
    if FAULT_MODEL in ["S@", "SET"]:
        TYPE_SABOTEUR = "SABOTUER"
        if FAULT_MODEL == "S@":
            F_CNTRL = [0, 1]
        else:
            F_CNTRL = [2]
    elif FAULT_MODEL in ["SEU"]:
        TYPE_SABOTEUR = "SEU"
        F_CNTRL = [2]
    else:
        FAULT_MODEL = "S@"
        TYPE_SABOTEUR = "SABOTUER"
        F_CNTRL = [0, 1]

    timestamps["1_init_end"] = time.time()

    rtl_prep_time_start = time.time()
    """1. RTL ELABORATION
    This step takes any verilog source code and create a simplified RTL model of the circuit in a single file"""
    rtl_elaboration(SRC_DIR=os.path.abspath(SRC_PATH), 
                    TOP_MODULE=TOP, 
                    PARAMS=TOP_PARAMS,
                    OUT_DIR=os.path.abspath(FI_DESIGN_PATH),
                    SRC_LIST_FILES=SRC_LIST_FILES,
                    SRC_INC_DIRS=SRC_INC_DIR)
    
    """1.1 Hierarchy Elaboration for selecting the target MODULE/MODULES
    In this stage, the rtl_elab file obtained from the firs stage is analyzed to extract the hierarchical component dependancies
    at this stage the user can select specific target intances to insert saboteur circuits, otherwise the system will select to 
    flatten the whole design and insert saboteur in all locations MODULES=[module1, module3 module3, ..]. """
    
    verilog_rtl_elab_code = read_verilog_file(f"{os.path.abspath(FI_DESIGN_PATH)}/{TOP}_rtl_elab.v")
    parsed_components_list = get_components(verilog_rtl_elab_code, conf_info)
    module_hierarchy = get_hierarchy(parsed_components_list, TOP)
    write_json(module_hierarchy, f"{os.path.abspath(FI_DESIGN_PATH)}/{TOP}_hierarchy.json")
    #TODO : Create a function to select the target components based on the hierarchy of the design
    rtl_prep_time_end= time.time()
    timestamps["2_rtl_elab_end"] = time.time()
    """2. TARGET COMPONENT EXTRACTION AND SABOTEUR INSERTION 
    This step select the number of components instatiated that incorporate the saboteur versions, the user defines how to carry out the
    component selection based on the hierarchy of the design"""
    sbtr_place_route_time_start= time.time()
    faults_per_module ={}
    Map_Modules = []
    for module_idx,MODULE in enumerate(MODULES):
        if "$paramod" in MODULE:
            ALT_MODULE_NAME = f"Module_{module_idx}"
        else:
            ALT_MODULE_NAME = MODULE
        Map_Modules.append([ALT_MODULE_NAME,MODULE])
        """ 2.1. component extraction from the rtl_elab design
        This step takes the previous rtl circuit and extracts an specific component as target for inserting saboteurs, a target component 
        could also be the top entity"""
        extract_verilog_module(SRC_DIR=os.path.abspath(FI_DESIGN_PATH),
                            MODULE=f"{MODULE}",
                            SRC_LIST_FILES=SRC_LIST_FILES,
                            SRC_INC_DIRS=SRC_INC_DIR,
                            OUT_DIR=os.path.abspath(FI_DESIGN_PATH),
                            FILE_OUT=f"{ALT_MODULE_NAME}",
                            FLT=True)

        """ 2.2 Saboteur insertion to the component
        This step takes a gate-level netlist and inserts saboteur circuits to the wires or to the FFs"""
        num_fault_locations=module_saboteur_insertion(f"{os.path.abspath(FI_DESIGN_PATH)}/{ALT_MODULE_NAME}_gate.v", 
                                TYPE_SABOTEUR,
                                ALT_MODULE_NAME,
                                TOP_MODULE=TOP)

        if MODULE not in faults_per_module:
            faults_per_module[MODULE] = num_fault_locations

    #TODO: Final report of the interconection sequence of the sbtr instances
    """3. FINAL INSTANTIATION OF THE SBTR MODULES TO MAKE VISIBLE THE I/O SBTR PORTS ON THE TOP MODULE OF THE DESIGN
    This could also be paralelized creating two or more design files each with different set of instances including the sbtr designs.
    for example, if in total there are 100 instances of different sbtr, it is possible to create 100 or less designs with differemt 
    modules for FIs. Thus, it is possible to have 100 sims im parallel. """
    hierarchical_components = []
    for cmp_path in SELECTED_INSTANCE_PATHS:
        parts = cmp_path.split("->")
        if len(parts) == 2:
            hierarchical_components.append(
                {"components_to_update": parts[0].split("@"), "for": parts[1]}
            )

    updated_hierarchy = identify_modified_components(module_hierarchy, hierarchical_components )
    write_json(updated_hierarchy, f"{os.path.abspath(FI_DESIGN_PATH)}/{TOP}_updated_hierarchy.json")
    updated_component_list = get_components_to_copy(updated_hierarchy)
    write_json(updated_component_list, f"{os.path.abspath(FI_DESIGN_PATH)}/{TOP}_components.json")
    augmented_modules = extract_original_components(verilog_rtl_elab_code, updated_component_list)
    verilog_rtl_elab_code += f"\n{augmented_modules}"
    verilog_rtl_elab_code = update_top_module(verilog_rtl_elab_code, updated_component_list, TOP)
    (fi_infrastructure_system, fi_infrastructure_dict) = fi_infrastructure_interconnect_sequence(updated_component_list)
    write_json(fi_infrastructure_dict, f"{os.path.abspath(FI_DESIGN_PATH)}/{TOP}_fi_infrastructure.json")

    if len(fi_infrastructure_system) == 0:
        os.system(
            f"mv {os.path.abspath(FI_DESIGN_PATH)}/{TOP}_gate_sbtr.v {os.path.abspath(FI_DESIGN_PATH)}/{TOP}_fi_sbtr.v"
        )
    else:
        write_verilog_file(f"{os.path.abspath(FI_DESIGN_PATH)}/{TOP}_fi_sbtr.v", verilog_rtl_elab_code)
    
    
    os.system(f"rm {os.path.abspath(FI_DESIGN_PATH)}/{TOP}_rtl_elab.v")
    os.system(f"cp {SBTR_CELLS}/basic_sabotuer.v {os.path.abspath(FI_DESIGN_PATH)}/ ")
    os.system(f"cp {SBTR_CELLS}/super_sabouter.v {os.path.abspath(FI_DESIGN_PATH)}/ ")
    os.system(f"cp {SBTR_CELLS}/shift_register.v {os.path.abspath(FI_DESIGN_PATH)}/ ")
    os.system(f"cp {SBTR_CELLS}/tb_sbtr_cntrl.v {os.path.abspath(FI_DESIGN_PATH)}/ ")
    timestamps["3_sbtr_place_route_end"] = time.time()
    sbtr_place_route_time_end= time.time()
    # Here the design is ready to be simulated or synthesized in FPGA
    # the next steps are to generate the fault list and the testbench
    # the fault list is generated based on the interconection of the sbtr instances
    # the testbench is modified to include the sbtr controller and the fault list is injected in the simulation
    # the simulation is executed and the results are stored in a csv file
    # TODO: It is missing the creation of a list indicating the order in which the sbtr instances are interconnected, currently it is done manually and arbitrary
    
    """3. FAULT LITS GENERATION
    This step creates a list of faults considering the sequence of interconection of the sbtr instances and the number of 
    locations that every component has. """

    start_bit_pos=0
    num_target_components=0
    total_bit_shift=0
    with open(f"{os.path.abspath(TB_PATH)}/{FAULT_MODEL}_{F_LIST_NAME}", "w") as fp:
        List_injections=[]

        if len(fi_infrastructure_system) == 0:
            end_bit_pos = (start_bit_pos + faults_per_module[TOP] + 2) 
            for fault_index in range(faults_per_module[TOP]):
                for ftype in F_CNTRL:
                    seutime = random.randint(1, MAX_TB_RUN_TIME)
                    List_injections.append([0, TOP, TOP, start_bit_pos, end_bit_pos, fault_index, ftype, seutime])
                    fp.write(f"{0},{TOP},{TOP},{start_bit_pos},{end_bit_pos},{fault_index},{ftype},{seutime}\n")
            start_bit_pos = start_bit_pos + faults_per_module[TOP] + 2
        else:
            for [idx,inst,module] in (fi_infrastructure_system):
                end_bit_pos = (start_bit_pos + faults_per_module[module] + 2) 
                for fault_index in range(faults_per_module[module]):
                    for ftype in F_CNTRL:
                        seutime = random.randint(1, MAX_TB_RUN_TIME)
                        List_injections.append([idx, inst, module, start_bit_pos, end_bit_pos, fault_index, ftype, seutime])
                        fp.write(f"{idx},{inst},{module},{start_bit_pos},{end_bit_pos},{fault_index},{ftype},{seutime}\n")
                start_bit_pos = start_bit_pos + faults_per_module[module] + 2
                num_target_components = idx 
        total_bit_shift = end_bit_pos
        num_target_components = num_target_components + 1
        
    timestamps["4_fault_list_gen_end"] = time.time()
    fi_compile_time_start= time.time()
    """5. TESTBENCH MODIFICATION AND MAKEFILES CREATION
    The purpose of this piece of code is to automatically inserte the saboteur control inside the original testbench
    This part is automatic if the tesbench instantiates the target circuit, otherwise it is necesary to make this customization manually"""
    if MAKE_SIM_TB:
        create_makefile_tb_sbtr(
            FI_DESIGN_PATH,
            TOP,
            TB_PATH=TB_PATH,
            TB_TARGET_FILE=TB_TARGET_FILE,
            TB_TOP=TB_TOP,
            TB_LIST_FILES=TB_LIST_FILES,
            INC_DIRS=INC_DIRS,
            VERILATOR_PARAMS=VERILATOR_PARAMS
        )
        print("SMS: The testbench makefile was created succesfully")
    else:
        print(
            "SMS: You haven't provided testbench files, be sure you modified the testbench and created a makefile for compile it"
        )

    """5. SIMULATION SETUP VERILATOR:
    This step takes the output file from step 4 and the modified test bench, the last one can be the automatic or the manually generated. 
    These files are passed to verilator to create the simulation executable"""
    
    WORK_DIR = os.path.abspath(TB_PATH)
    os.chdir(TB_PATH)
    if not args.only_sim:
        if MAKE_SIM_TB:
            os.system(f"make -f Makefile_sbtr clean; make -f Makefile_sbtr")
        else:
            os.system(f"{MAKE_CMD}")
    
    fi_compile_time_end= time.time()
    timestamps["5_fi_tb_compile_end"] = time.time()
    """6. FAULT INJECTION CAMPIGN:
    This step perform eht fault injection by selecting the target bit to be corrupted inside the circuit. This Fault injection can be paralelized"""   
    fi_config = {
        "FAULT_LIST_NAME": f"{FAULT_MODEL}_{F_LIST_NAME}",
        "FAULT_MODEL": f"{FAULT_MODEL}",
        "F_SIM_REPORT": f"{F_SIM_REPORT}",
        "MAX_NUM_INJ": MAX_NUM_INJ,
        "NUM_TARGET_COMPONENTS": num_target_components,
        "TOTAL_BIT_SHIFT": total_bit_shift,
        "JOBS": NUM_JOBS
    }
    
    fault_free_time_start= time.time()
    run_fault_free_simulation(WORK_DIR=WORK_DIR, fi_config=fi_config)
    fault_free_time_end= time.time()
    timestamps["6_fi_golden_sim_end"] = time.time()
    
    fault_time_start= time.time()
    run_fault_simulation(WORK_DIR=WORK_DIR, fi_config=fi_config)
    fault_time_end= time.time()
    timestamps["7_fi_fault_sim_end"] = time.time()

    print(f"SMS: The simulation was completed, the report is in {os.path.abspath(TB_PATH)}/{F_SIM_REPORT}")
    print(f"SMS: The simulation was completed, the report is in {os.path.abspath(TB_PATH)}/{F_LIST_NAME}")
    print(f"rtl_preparation_time, {abs(rtl_prep_time_start-rtl_prep_time_end)}")
    print(f"sbtr_place_route_time, {abs(sbtr_place_route_time_start-sbtr_place_route_time_end)}")
    print(f"fi_compile_time, {abs(fi_compile_time_start-fi_compile_time_end)}")
    print(f"fault_free_time, {abs(fault_free_time_start-fault_free_time_end)}")
    print(f"fault_time, {abs(fault_time_start-fault_time_end)/(NUM_JOBS*2)}")

    os.chdir(ROOT)
    write_json(timestamps, "timestamps.json")

if __name__ == "__main__":
    main()
