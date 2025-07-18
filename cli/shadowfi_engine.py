import os, random

from FI.automatic_saboteur.hierarchy_updaters import (
    identify_modified_components,
    get_components_to_copy,
)
from FI.automatic_saboteur.sabotage_injectors import (
    extract_original_components,
    fi_infrastructure_interconnect_sequence,
    update_top_module,
)
from FI.automatic_saboteur.parsers import get_components, get_hierarchy

from FI.fault_simulation.fault_sim_main import (
    run_fault_free_simulation,
    run_fault_simulation,
)

from FI.sabotuer_scripts.script_injection import module_saboteur_insertion
from FI.sabotuer_scripts.yosys_extract_module import extract_verilog_module
from FI.sabotuer_scripts.yosys_rtl_elaboration_verilog import rtl_elaboration
from utils import (
    create_makefile_tb_sbtr,
    read_verilog_file,
    write_verilog_file,
    write_json,
)


def rtl_elaboration_step(config):
    """
    1. RTL ELABORATION
    This step takes any verilog source code and create a simplified RTL model of the circuit in a single file
    """

    SRC_PATH = config["SRC_PATH"]
    TOP = config["TOP"]
    TOP_PARAMS = config["TOP_PARAMS"]
    SRC_LIST_FILES = config["SRC_LIST_FILES"]
    FI_DESIGN_PATH = config["FI_DESIGN_PATH"]
    SRC_INC_DIR = config["SRC_INC_DIR"]
    conf_info = config["conf_info"]

    rtl_elaboration(
        SRC_DIR=os.path.abspath(SRC_PATH),
        TOP_MODULE=TOP,
        PARAMS=TOP_PARAMS,
        OUT_DIR=os.path.abspath(FI_DESIGN_PATH),
        SRC_LIST_FILES=SRC_LIST_FILES,
        SRC_INC_DIRS=SRC_INC_DIR,
    )

    """
    1.1 Hierarchy Elaboration for selecting the target MODULE/MODULES
    In this stage, the rtl_elab file obtained from the firs stage is analyzed to extract the hierarchical component dependancies at this stage the user can select specific target intances to insert saboteur circuits, otherwise the system will select to flatten the whole design and insert saboteur in all locations MODULES=[module1, module3 module3, ..].
    """

    verilog_rtl_elab_code = read_verilog_file(
        f"{os.path.abspath(FI_DESIGN_PATH)}/{TOP}_rtl_elab.v"
    )
    parsed_components_list = get_components(verilog_rtl_elab_code, conf_info)
    module_hierarchy = get_hierarchy(parsed_components_list, TOP)
    write_json(
        module_hierarchy, f"{os.path.abspath(FI_DESIGN_PATH)}/{TOP}_hierarchy.json"
    )
    # TODO : Create a function to select the target components based on the hierarchy of the design

    return module_hierarchy, verilog_rtl_elab_code


def target_extraction_and_sbrt_insertion(config):
    """
    2. TARGET COMPONENT EXTRACTION AND SABOTEUR INSERTION
    This step select the number of components instatiated that incorporate the saboteur versions, the user defines how to carry out the component selection based on the hierarchy of the design
    """

    TOP = config["TOP"]
    SRC_LIST_FILES = config["SRC_LIST_FILES"]
    MODULES = config["MODULES"]
    TYPE_SABOTEUR = config["TYPE_SABOTEUR"]
    FI_DESIGN_PATH = config["FI_DESIGN_PATH"]
    SRC_INC_DIR = config["SRC_INC_DIR"]

    faults_per_module = {}
    Map_Modules = []
    for module_idx, MODULE in enumerate(MODULES):
        if "$paramod" in MODULE:
            ALT_MODULE_NAME = f"Module_{module_idx}"
        else:
            ALT_MODULE_NAME = MODULE
        Map_Modules.append([ALT_MODULE_NAME, MODULE])
        """ 2.1. component extraction from the rtl_elab design
        This step takes the previous rtl circuit and extracts an specific component as target for inserting saboteurs, a target component 
        could also be the top entity"""
        extract_verilog_module(
            SRC_DIR=os.path.abspath(FI_DESIGN_PATH),
            MODULE=f"{MODULE}",
            SRC_LIST_FILES=SRC_LIST_FILES,
            SRC_INC_DIRS=SRC_INC_DIR,
            OUT_DIR=os.path.abspath(FI_DESIGN_PATH),
            FILE_OUT=f"{ALT_MODULE_NAME}",
            FLT=True,
        )

        """ 2.2 Saboteur insertion to the component
        This step takes a gate-level netlist and inserts saboteur circuits to the wires or to the FFs"""
        num_fault_locations = module_saboteur_insertion(
            f"{os.path.abspath(FI_DESIGN_PATH)}/{ALT_MODULE_NAME}_gate.v",
            TYPE_SABOTEUR,
            ALT_MODULE_NAME,
            TOP_MODULE=TOP,
        )

        if MODULE not in faults_per_module:
            faults_per_module[MODULE] = num_fault_locations

    # TODO: Final report of the interconection sequence of the sbtr instances

    return faults_per_module


def final_sbtr_instantiation(config, module_hierarchy, verilog_rtl_elab_code):
    """
    3. FINAL INSTANTIATION OF THE SBTR MODULES TO MAKE VISIBLE THE I/O SBTR PORTS ON THE TOP MODULE OF THE DESIGN
    This could also be paralelized creating two or more design files each with different set of instances including the sbtr designs.
    For example, if in total there are 100 instances of different sbtr, it is possible to create 100 or less designs with differemt modules for FIs. Thus, it is possible to have 100 sims im parallel.
    """

    TOP = config["TOP"]
    SELECTED_INSTANCE_PATHS = config["SELECTED_INSTANCE_PATHS"]
    SBTR_CELLS = config["SBTR_CELLS"]
    FI_DESIGN_PATH = config["FI_DESIGN_PATH"]

    hierarchical_components = []
    for cmp_path in SELECTED_INSTANCE_PATHS:
        parts = cmp_path.split("->")
        if len(parts) == 2:
            hierarchical_components.append(
                {"components_to_update": parts[0].split("@"), "for": parts[1]}
            )

    updated_hierarchy = identify_modified_components(
        module_hierarchy, hierarchical_components
    )
    write_json(
        updated_hierarchy,
        f"{os.path.abspath(FI_DESIGN_PATH)}/{TOP}_updated_hierarchy.json",
    )
    updated_component_list = get_components_to_copy(updated_hierarchy)
    write_json(
        updated_component_list,
        f"{os.path.abspath(FI_DESIGN_PATH)}/{TOP}_components.json",
    )
    augmented_modules = extract_original_components(
        verilog_rtl_elab_code, updated_component_list
    )
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

    # Here the design is ready to be simulated or synthesized in FPGA
    # the next steps are to generate the fault list and the testbench
    # the fault list is generated based on the interconection of the sbtr instances
    # the testbench is modified to include the sbtr controller and the fault list is injected in the simulation
    # the simulation is executed and the results are stored in a csv file
    # TODO: It is missing the creation of a list indicating the order in which the sbtr instances are interconnected, currently it is done manually and arbitrary

    return fi_infrastructure_system


def fault_list_generation(config, fi_infrastructure_system, faults_per_module):
    """
    4. FAULT LITS GENERATION
    This step creates a list of faults considering the sequence of interconection of the sbtr instances and the number of locations that every component has.
    """
    TOP = config["TOP"]
    TB_PATH = config["TB_PATH"]
    MAX_TB_RUN_TIME = config["MAX_TB_RUN_TIME"]
    FAULT_MODEL = config["FAULT_MODEL"]
    F_CNTRL = config["F_CNTRL"]
    F_LIST_NAME = config["F_LIST_NAME"]

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

    return num_target_components, total_bit_shift


def testbench_creation(config):
    """
    5. TESTBENCH MODIFICATION AND MAKEFILES CREATION
    The purpose of this piece of code is to automatically inserte the saboteur control inside the original testbench.
    This part is automatic if the tesbench instantiates the target circuit, otherwise it is necesary to make this customization manually
    """

    TOP = config["TOP"]
    INC_DIRS = config["INC_DIRS"]
    MAKE_SIM_TB = config["MAKE_SIM_TB"]
    TB_TOP = config["TB_TOP"]
    TB_PATH = config["TB_PATH"]
    TB_LIST_FILES = config["TB_LIST_FILES"]
    TB_TARGET_FILE = config["TB_TARGET_FILE"]
    VERILATOR_PARAMS = config["VERILATOR_PARAMS"]
    FI_DESIGN_PATH = config["FI_DESIGN_PATH"]

    if MAKE_SIM_TB:
        create_makefile_tb_sbtr(
            FI_DESIGN_PATH,
            TOP,
            TB_PATH=TB_PATH,
            TB_TARGET_FILE=TB_TARGET_FILE,
            TB_TOP=TB_TOP,
            TB_LIST_FILES=TB_LIST_FILES,
            INC_DIRS=INC_DIRS,
            VERILATOR_PARAMS=VERILATOR_PARAMS,
        )
        print("SMS: The testbench makefile was created succesfully")
    else:
        print(
            "SMS: You haven't provided testbench files, be sure you modified the testbench and created a makefile for compile it"
        )


def simulation_setup(config):
    """
    6. SIMULATION SETUP VERILATOR:
    This step takes the output file from step 4 and the modified test bench, the last one can be the automatic or the manually generated.
    These files are passed to verilator to create the simulation executable
    """

    MAKE_SIM_TB = config["MAKE_SIM_TB"]
    TB_PATH = config["TB_PATH"]
    MAKE_CMD = config["MAKE_CMD"]
    ROOT = config["ROOT"]

    os.chdir(TB_PATH)
    if MAKE_SIM_TB:
        os.system("make -f Makefile_sbtr clean; make -f Makefile_sbtr")
    else:
        os.system(f"{MAKE_CMD}")
    os.chdir(ROOT)

def run_simulation(config, num_target_components, total_bit_shift):
    """
    7. FAULT INJECTION CAMPIGN:
    This step perform eht fault injection by selecting the target bit to be corrupted inside the circuit. This Fault injection can be paralelized
    """

    TB_PATH = config["TB_PATH"]
    FAULT_MODEL = config["FAULT_MODEL"]
    MAX_NUM_INJ = config["MAX_NUM_INJ"]
    F_LIST_NAME = config["F_LIST_NAME"]
    F_SIM_REPORT = config["F_SIM_REPORT"]
    NUM_JOBS = config["NUM_JOBS"]

    WORK_DIR = os.path.abspath(TB_PATH)
    fi_config = {
        "FAULT_LIST_NAME": f"{FAULT_MODEL}_{F_LIST_NAME}",
        "FAULT_MODEL": f"{FAULT_MODEL}",
        "F_SIM_REPORT": f"{F_SIM_REPORT}",
        "MAX_NUM_INJ": MAX_NUM_INJ,
        "NUM_TARGET_COMPONENTS": num_target_components,
        "TOTAL_BIT_SHIFT": total_bit_shift,
        "JOBS": NUM_JOBS,
    }

    run_fault_free_simulation(WORK_DIR=WORK_DIR, fi_config=fi_config)

    run_fault_simulation(WORK_DIR=WORK_DIR, fi_config=fi_config)

    os.chdir(config["ROOT"])


