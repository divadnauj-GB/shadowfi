
import logging
import os
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
)

def rtl_elaboration_step(config):
    """
    1. RTL ELABORATION
    This step takes any verilog source code and create a simplified RTL model of the circuit in a single file
    """

    design_config = config.get('project',{}).get('design_config', {})
    sbtr_config = config.get('project',{}).get('sbtr_config', {})

    SRC_PATH = design_config.get('src_path', '')
    TOP = design_config.get('top_module', '')
    TOP_PARAMS = design_config.get('module_params', [])
    if not isinstance(TOP_PARAMS,list):
        TOP_PARAMS=[]
    SRC_LIST_FILES = design_config.get('src_list_files', [])
    if not isinstance(SRC_LIST_FILES,list):
        SRC_LIST_FILES=[]
    FI_DESIGN_PATH = sbtr_config.get('sbtr_dir','') #design_info.get('output_path', '')
    SRC_INC_DIR = design_config.get('inc_directories', [])
    if not isinstance(SRC_INC_DIR,list):
        SRC_INC_DIR=[]
    conf_info = config

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

    new_dest_path_rtl_elab = os.path.abspath(os.path.join(FI_DESIGN_PATH,"../src"))
    os.system(f"cp {os.path.abspath(FI_DESIGN_PATH)}/{TOP}_rtl_elab.v {new_dest_path_rtl_elab}")

    return module_hierarchy, verilog_rtl_elab_code



def elaborate(config,args=None):
    project_name = config.get('project', {}).get('name', 'unknown')
    logging.info(f'Elaborating project: {project_name}')
    # Simulated logic here
    module_hierarchy, verilog_rtl_elab_code = rtl_elaboration_step(config)
    logging.info('Elaboration completed.')
