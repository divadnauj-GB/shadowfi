
import logging
import os
import random
from random import randint

from .shadowfi_core.automatic_saboteur.hierarchy_updaters import (
    identify_modified_components,
    get_components_to_copy,
)
from .shadowfi_core.automatic_saboteur.sabotage_injectors import (
    extract_original_components,
    fi_infrastructure_interconnect_sequence,
    update_top_module,
)
from .shadowfi_core.automatic_saboteur.parsers import get_components, get_hierarchy

from .shadowfi_core.fault_simulation.fault_sim_main import (
    run_fault_free_simulation,
    run_fault_simulation,
)

from .shadowfi_core.sabotuer_scripts.script_injection import module_saboteur_insertion
from .shadowfi_core.sabotuer_scripts.yosys_extract_module import extract_verilog_module
from .shadowfi_core.sabotuer_scripts.yosys_rtl_elaboration_verilog import rtl_elaboration

from .shadowfi_utils.utils import (
    create_makefile_tb_sbtr,
    read_verilog_file,
    write_verilog_file,
    write_json,
    read_json,
)

from utils.config_loader import load_config, save_config


def get_list_of_instances(module_hierarchy):
    """
    Get the list of instances from the configuration.
    This function extracts the list of instances from the configuration file.
    """
    instances = []
    str_path = ""
    def get_instances_recursive(modules, instances, str_path=""):
        for module in modules:
            if len(module['dependency']['components']) > 0:
                str_path += f"{module['module']}@"
                get_instances_recursive(module['dependency']['components'], instances,str_path)
                str_path = str_path.split('@')[:-2]  # Remove last module
                str_path = '@'.join(str_path) + '@'  # Rebuild the path
                str_path = str_path[1:] if str_path.startswith('@') else str_path  # Remove leading slash
            else:
                str_path += f"{module['module']}@"
                instances.append([str_path[:-1],module['component']])  # Remove trailing slash
                str_path = str_path.split('@')[:-2]  # Remove last module
                str_path = '@'.join(str_path) + '@'  # Rebuild the path
                str_path = str_path[1:] if str_path.startswith('@') else str_path  # Remove leading slash
    get_instances_recursive(module_hierarchy['components'],instances,str_path)
    return instances

def resolve_target_modules(config):
    """
    Resolve the target modules from the configuration.
    This function extracts the target modules from the configuration file.
    """
    sbtr_config = config.get('project', {}).get('sbtr_config', {})
    design_config = config.get('project', {}).get('design_config', {})
    
    cmp_sel = sbtr_config.get('component_selection', {}).get('mode', 'random')
    file_name = f"{sbtr_config['sbtr_dir']}/{design_config['top_module']}_hierarchy.json"
    module_hierarchy=read_json(os.path.join(sbtr_config['sbtr_dir'], file_name))
    instances=get_list_of_instances(module_hierarchy)
    
    selected_instances = []
    selected_components = []
    if cmp_sel == "random":
        # TODO: Implement a more sophisticated random selection
        N=4
        while len(selected_instances) < N:
            randindex = randint(0, len(instances) - 1)
            instance_path, module_name = instances[randindex]
            instance_str = f"{instance_path}->{module_name}_sbtr"
            if instance_str not in selected_instances:
                selected_instances.append(instance_str)
            if module_name not in selected_components:
                selected_components.append(module_name)

    if cmp_sel == "hierarchy":
        # TODO: Implement a more sophisticated hierarchical selection
        selected_instances = [
            "shd@\win_l:1.suma->window_sum_13_450_7_sbtr",
            "shd@\win_l:2.suma->window_sum_13_450_7_sbtr",
            "shd@\win_l:3.suma->window_sum_13_450_7_sbtr",
            "shd@\win_l:4.suma->window_sum_13_450_7_sbtr",
            "shd@\win_l:5.suma->window_sum_13_450_7_sbtr",
        ]
        selected_components = [
            "window_sum_13_450_7",
        ]

    if cmp_sel == "top":
        # Select the top module as the only target
        selected_instances = [f"{design_config['top_module']}_sbtr"]
        selected_components = [design_config['top_module']]

    # Update the configuration with the selected instances and components
    sbtr_config['component_selection']['hierarchical_component'] = selected_instances
    sbtr_config['component_selection']['target_modules'] = selected_components
    config['project']['sbtr_config'] = sbtr_config
    save_config(config, config['project']['proj_config_file'])
    return(module_hierarchy)

def target_extraction_and_sbrt_insertion(config):
    """
    2. TARGET COMPONENT EXTRACTION AND SABOTEUR INSERTION
    This step select the number of components instatiated that incorporate the saboteur versions, the user defines how to carry out the component selection based on the hierarchy of the design
    """
    design_config = config.get('project',{}).get('design_config', {})
    sbtr_config = config.get('project',{}).get('sbtr_config', {})

    TOP = design_config.get('top_module', '')
    SRC_LIST_FILES = design_config.get('src_list_files', [])
    if not isinstance(SRC_LIST_FILES,list):
        SRC_LIST_FILES=[]
    MODULES = sbtr_config.get('component_selection',{}).get('target_modules',[]) 
    if not isinstance(MODULES,list):
        MODULES=[]
    FI_DESIGN_PATH = sbtr_config.get('sbtr_dir','') #design_info.get('output_path', '')
    SRC_INC_DIR = design_config.get('inc_directories', [])
    if not isinstance(SRC_INC_DIR,list):
        SRC_INC_DIR=[]
    FAULT_MODEL = sbtr_config.get('fault_model', 'S@')

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

    design_config = config.get('project',{}).get('design_config', {})
    sbtr_config = config.get('project',{}).get('sbtr_config', {})

    TOP = design_config.get('top_module', '')
    SELECTED_INSTANCE_PATHS = sbtr_config.get('component_selection', {}).get('hierarchical_component', [])
    if not isinstance(SELECTED_INSTANCE_PATHS,list):
        SELECTED_INSTANCE_PATHS=[]
    SBTR_CELLS = os.path.join(config.get('shadowfi_root', "./"),"core/shadowfi_core/sbtr_cells")
    FI_DESIGN_PATH = sbtr_config.get('sbtr_dir','') #design_info.get('output_path', '')

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
    design_config = config.get('project',{}).get('design_config', {})
    sbtr_config = config.get('project',{}).get('sbtr_config', {})
    testbench_config = config.get('project',{}).get('testbench_config', {})

    TOP = design_config.get('top_module', '')
    WORK_DIR = config.get('project', {}).get('work_dir', '')
    #MAX_TB_RUN_TIME = testbench_config.get('sim_runtime', 1000)
    FAULT_MODEL = sbtr_config.get('fault_model', 'S@')
    FI_DESIGN_PATH = sbtr_config.get('sbtr_dir','')

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

    F_LIST_NAME = config.get('project', {}).get('fault_list_name', 'fault_list.csv')

    start_bit_pos=0
    num_target_components=0
    total_bit_shift=0
    with open(f"{os.path.abspath(FI_DESIGN_PATH)}/{FAULT_MODEL}_{F_LIST_NAME}", "w") as fp:
        List_injections=[]

        if len(fi_infrastructure_system) == 0:
            end_bit_pos = (start_bit_pos + faults_per_module[TOP] + 2) 
            for fault_index in range(faults_per_module[TOP]):
                for ftype in F_CNTRL:
                    seutime = 0
                    List_injections.append([0, TOP, TOP, start_bit_pos, end_bit_pos, fault_index, ftype, seutime])
                    fp.write(f"{0},{TOP},{TOP},{start_bit_pos},{end_bit_pos},{fault_index},{ftype},{seutime}\n")
            start_bit_pos = start_bit_pos + faults_per_module[TOP] + 2
        else:
            for [idx,inst,module] in (fi_infrastructure_system):
                end_bit_pos = (start_bit_pos + faults_per_module[module] + 2) 
                for fault_index in range(faults_per_module[module]):
                    for ftype in F_CNTRL:
                        seutime = 0
                        List_injections.append([idx, inst, module, start_bit_pos, end_bit_pos, fault_index, ftype, seutime])
                        fp.write(f"{idx},{inst},{module},{start_bit_pos},{end_bit_pos},{fault_index},{ftype},{seutime}\n")
                start_bit_pos = start_bit_pos + faults_per_module[module] + 2
                num_target_components = idx 
        total_bit_shift = end_bit_pos
        num_target_components = num_target_components + 1

    return num_target_components, total_bit_shift


def run_pnr(config,args=None):
    project_name = config.get('project', {}).get('name', 'unknown')
    logging.info(f'Running Place and Route for project: {project_name}')
    config['project']['sbtr_config']['component_selection']['mode']= args.cmp_sel
    config['project']['sbtr_config']['fault_model'] = args.fault_model
    config['project']['sbtr_config']['fault_sampling'] = args.fault_sampling
    logging.info(f"Component selection: {args.cmp_sel}, Fault model: {args.fault_model}, Fault sampling: {args.fault_sampling}")
    save_config(config, config['project']['proj_config_file'])

    design_config = config.get('project',{}).get('design_config', {})
    sbtr_config = config.get('project', {}).get('sbtr_config', {})
    path_rtl_elab = os.path.abspath(os.path.join(sbtr_config['sbtr_dir'],"../src"))
    os.system(f"cp {path_rtl_elab}/{design_config['top_module']}_rtl_elab.v {sbtr_config['sbtr_dir']}")

    file_name = f"{sbtr_config['sbtr_dir']}/{design_config['top_module']}_rtl_elab.v"
    

    verilog_rtl_elab_code = read_verilog_file(
        file_name
    )
    
    module_hierarchy = resolve_target_modules(config)
    faults_per_module=target_extraction_and_sbrt_insertion(config)

    fi_infrastructure_system = final_sbtr_instantiation(
        config, module_hierarchy, verilog_rtl_elab_code
    )

    num_target_components, total_bit_shift = fault_list_generation(
        config, fi_infrastructure_system, faults_per_module
    )

    logging.info(f"Number of target components: {num_target_components}, Total bit shift: {total_bit_shift}")
    config['project']['sim_config']['num_target_components'] = num_target_components
    config['project']['sim_config']['total_bit_shift'] = total_bit_shift
    save_config(config, config['project']['proj_config_file'])

    # Simulated logic here
    logging.info('Place and Route completed.')
