import os

from omegaconf import OmegaConf

from .args import parser
from .utils import read_yaml_file

from .constants import (
    SCRIPTS_PATH,
    SBTR_CELLS,
    TARGET_MODULES,
    F_LIST_NAME,
    F_SIM_REPORT,
    MAKEFILE_SBTR,
    DEFAULT_DICT,
    ROOT,
)


def settings():
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

    return {
        "SRC_PATH": SRC_PATH,
        "TOP": TOP,
        "SRC_LIST_FILES": SRC_LIST_FILES,
        "INC_DIRS": INC_DIRS,
        "TOP_PARAMS": TOP_PARAMS,
        "MAKE_SIM_TB": MAKE_SIM_TB,
        "TB_TOP": TB_TOP,
        "TB_PATH": TB_PATH,
        "TB_LIST_FILES": TB_LIST_FILES,
        "TB_TARGET_FILE": TB_TARGET_FILE,
        "VERILATOR_PARAMS": VERILATOR_PARAMS,
        "MAX_TB_RUN_TIME": MAX_TB_RUN_TIME,
        "MAKE_CMD": MAKE_CMD,
        "MODULES": MODULES,
        "SELECTED_INSTANCE_PATHS": SELECTED_INSTANCE_PATHS,
        "FAULT_MODEL": FAULT_MODEL,
        "MAX_NUM_INJ": MAX_NUM_INJ,
        "TYPE_SABOTEUR": TYPE_SABOTEUR,
        "F_CNTRL": F_CNTRL,
        "SCRIPTS_PATH": SCRIPTS_PATH,
        "SBTR_CELLS": SBTR_CELLS,
        "TARGET_MODULES": TARGET_MODULES,
        "F_LIST_NAME": F_LIST_NAME,
        "F_SIM_REPORT": F_SIM_REPORT,
        "MAKEFILE_SBTR": MAKEFILE_SBTR,
        "CONFIG_FILE": CONFIG_FILE,
        "FAULT_MODEL": FAULT_MODEL,
        "MAX_NUM_INJ": MAX_NUM_INJ,
        "TB_TARGET_FILE": TB_TARGET_FILE,
        "VERILATOR_PARAMS": VERILATOR_PARAMS,
        "FI_DESIGN_PATH": FI_DESIGN_PATH,
        "SRC_INC_DIR": SRC_INC_DIR,
        "NUM_JOBS": NUM_JOBS,
        "ROOT": ROOT,
        "conf_info": conf_info,
    }