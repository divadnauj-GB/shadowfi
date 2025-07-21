
import logging
import os
import yaml

from .shadowfi_utils.utils import (
    create_makefile_tb_sbtr,
    read_verilog_file,
    write_verilog_file,
    write_json,
)

from utils.config_loader import load_config, save_config
from core.shadowfi_utils.constants import ROOT

def testbench_creation(config):
    """
    5. TESTBENCH MODIFICATION AND MAKEFILES CREATION
    The purpose of this piece of code is to automatically inserte the saboteur control inside the original testbench.
    This part is automatic if the tesbench instantiates the target circuit, otherwise it is necesary to make this customization manually
    """

    design_config = config.get('project',{}).get('design_config', {})
    sbtr_config = config.get('project',{}).get('sbtr_config', {})
    testbench_config = config.get('project',{}).get('testbench_config', {})

    
    EXT_TB_BUILD = testbench_config.get("external_tb_build", False)
    if not EXT_TB_BUILD:
        internal_tb_config = testbench_config.get("internal_tb_config", {})
        TOP = design_config.get("top_module", "")
        INC_DIRS = design_config.get("inc_directories", []) if isinstance(design_config.get("inc_directories", []),list) else []
        INC_DIRS.extend(internal_tb_config.get("tb_inc_directories", []) if isinstance(internal_tb_config.get("tb_inc_directories", []),list) else [])
        TB_TOP = internal_tb_config.get("tb_top", "")
        TB_PATH = internal_tb_config.get("tb_path", "")
        TB_LIST_FILES = internal_tb_config.get("tb_list_files", [])
        if not isinstance(TB_LIST_FILES,list):
            TB_LIST_FILES=[]
        TB_TARGET_FILE = internal_tb_config.get("tb_target_file", "")
        VERILATOR_PARAMS = internal_tb_config.get("tb_verilator_params", "")
        FI_DESIGN_PATH = sbtr_config.get("sbtr_dir", "")

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
    testbench_config = config.get('project',{}).get('testbench_config', {})
    

    EXT_TB_BUILD = testbench_config.get("external_tb_build", False)

    if not EXT_TB_BUILD:
        internal_tb_config = testbench_config.get("internal_tb_config", {})
        TB_WORKING_DIR = internal_tb_config.get("tb_working_dir", "")
        os.chdir(TB_WORKING_DIR)
        os.system("make -f Makefile_sbtr clean; make -f Makefile_sbtr")
        os.chdir(ROOT)
    else:
        external_tb_config = testbench_config.get("external_tb_config", {})
        TB_WORKING_DIR = external_tb_config.get("tb_working_dir", "")
        TB_BUILD_CMD = external_tb_config.get("tb_build_cmd", [])
        os.chdir(TB_WORKING_DIR)
        if isinstance(TB_BUILD_CMD, list) and TB_BUILD_CMD:
            logging.info(f"Running make commands: {TB_BUILD_CMD}")
            # Execute each command in MAKE_CMD
            for cmd in TB_BUILD_CMD:
                if isinstance(cmd, str):
                    os.system(cmd)
                else:
                    logging.error(f"Invalid command in custom_tb_cmd: {cmd}")
            os.chdir(ROOT)
        else:
            logging.critical("No make commands provided for simulation setup.")
            os.chdir(ROOT)
            exit(1)


def setup_testbench(config,args=None):
    project_name = config.get('project', {}).get('name', 'unknown')
    logging.info(f'Setting up simulation for project: {project_name}')
    if args:
        if args.tb_config:
            tb_config = args.tb_config
            tb_config_data = load_config(tb_config)
            if isinstance(tb_config_data, dict):
                config['project']['testbench_config'] = tb_config_data.get('testbench_config', {})
                save_config(config, config['project']['proj_config_file'])
            else:
                logging.error(f'Testbench config file {tb_config} does not contain a valid dictionary.')
        elif args.kwargs:
            kwargs_dict = args.kwargs.get('testbench_config', {})
            print(f"Parsed kwargs: {kwargs_dict}")
            # Merge into config['project']['testbench_config']
            def deep_update(d, u):
                for k, v in u.items():
                    if isinstance(v, dict):
                        d[k] = deep_update(d.get(k, {}), v)
                    else:
                        d[k] = v
                return d
            config['project']['testbench_config'] = deep_update(config['project'].get('testbench_config', {}), kwargs_dict)
            save_config(config, config['project']['proj_config_file'])
    else:
        logging.warning('No testbench configuration file provided. Using the user defined make commands in the config file.')

    testbench_creation(config)
    simulation_setup(config)

    logging.info(f'Simulation setup for project {project_name} completed successfully.')


def setup_fault_injection(config, args=None):
    """
    7. FAULT INJECTION SETUP:
    This step is responsible for setting up the fault injection environment, including the configuration of the fault model and the testbench.
    """
    project_name = config.get('project', {}).get('name', 'unknown')
    logging.info(f'Setting up fault injection for project: {project_name}')

    if args: 
        if args.fsim_config:
            fsim_config = args.fsim_config
            fsim_config_data = load_config(fsim_config)
            if isinstance(fsim_config_data, dict):
                config['project']['sim_config'].update(fsim_config_data.get('sim_config', {}))
                save_config(config, config['project']['proj_config_file'])
            else:
                logging.error(f'Testbench config file {fsim_config} does not contain a valid dictionary.')
        elif args.kwargs:
            kwargs_dict = args.kwargs.get('sim_config', {})
            print(f"Parsed kwargs: {kwargs_dict}")
            # Merge into config['project']['testbench_config']
            def deep_update(d, u):
                for k, v in u.items():
                    if isinstance(v, dict):
                        d[k] = deep_update(d.get(k, {}), v)
                    else:
                        d[k] = v
                return d
            config['project']['sim_config'] = deep_update(config['project'].get('sim_config', {}), kwargs_dict)
            save_config(config, config['project']['proj_config_file'])
    else:
        logging.warning('No fault injection configuration file provided. ')

    sim_config = config.get('project', {}).get('sim_config', {})
    sbtr_config = config.get('project',{}).get('sbtr_config', {})
    # Extract necessary parameters from the configuration
    dest_root_work_dir = config.get('project', {}).get('work_dir', '')
    src_root_work_dir = sim_config.get('work_sim_root_dir', "")

    list_test_app_dirs = sim_config.get('tb_test_app_info', {}).get('test_app_dirs', [])
    if not isinstance(list_test_app_dirs,list):
        list_test_app_dirs=[]
    list_test_app_dirs.append(sim_config.get('tb_build_dir', ''))  # Ensure the build directory is included

    for dir in list_test_app_dirs:
        src_path = os.path.abspath(os.path.join(src_root_work_dir, dir))
        dest_path = os.path.abspath(os.path.join(dest_root_work_dir, dir))
        os.system(f"mkdir -p {dest_path}")
        os.system(f"cp -rf {src_path}/* {dest_path}/")

    list_test_app_files = sim_config.get('tb_test_app_info', {}).get('test_app_files', [])
    if not isinstance(list_test_app_files,list):
        list_test_app_files=[]
    for file in list_test_app_files:
        src_path = os.path.abspath(os.path.join(src_root_work_dir, file))
        dest_path = os.path.dirname(os.path.abspath(os.path.join(dest_root_work_dir, file)))
        if os.path.exists(src_path):
            os.system(f"mkdir -p {dest_path}")
            os.system(f"cp {src_path} {dest_path}")
        else:
            logging.warning(f"Source file {src_path} does not exist. Skipping copy.")

    FI_DESIGN_PATH = sbtr_config.get('sbtr_dir','')
    FAULT_MODEL = sbtr_config.get('fault_model', 'S@')
    F_LIST_NAME = config.get('project', {}).get('fault_list_name', 'fault_list.csv')

    work_dir = sim_config.get('work_sim_dir', '')
    WORK_DIR = os.path.abspath(os.path.join(dest_root_work_dir, work_dir))

    os.system(f"cp {os.path.abspath(FI_DESIGN_PATH)}/{FAULT_MODEL}_{F_LIST_NAME} {WORK_DIR}")

    if args.set_run_scripts:
        if args.run_script:
            src_path = args.run_script
            run_script_path = sim_config.get('tb_run_info',{}).get('tb_run_script', '')
            dest_path = os.path.dirname(os.path.abspath(os.path.join(dest_root_work_dir, run_script_path)))
            os.system(f"mkdir -p {dest_path}")
            os.system(f"cp {src_path} {dest_path}")
        else:
            src_path = os.path.join(config.get('shadowfi_root',""),"config","run.sh")
            run_script_path = sim_config.get('tb_run_info',{}).get('tb_run_script', '')
            dest_path = os.path.dirname(os.path.abspath(os.path.join(dest_root_work_dir, run_script_path)))
            os.system(f"mkdir -p {dest_path}")
            os.system(f"cp {src_path} {dest_path}")

        if args.sdc_check_script:
            src_path = args.sdc_check_script
            run_script_path = sim_config.get('tb_run_info',{}).get('tb_run_script', '')
            dest_path = os.path.dirname(os.path.abspath(os.path.join(dest_root_work_dir, run_script_path)))
            os.system(f"mkdir -p {dest_path}")
            os.system(f"cp {src_path} {dest_path}")
        else:
            src_path = os.path.join(config.get('shadowfi_root',""),"config","sdc_check.sh")
            run_script_path = sim_config.get('tb_run_info',{}).get('tb_run_script', '')
            dest_path = os.path.dirname(os.path.abspath(os.path.join(dest_root_work_dir, run_script_path)))
            os.system(f"mkdir -p {dest_path}")
            os.system(f"cp {src_path} {dest_path}")



    logging.info(f'Fault injection setup for project {project_name} completed successfully.')