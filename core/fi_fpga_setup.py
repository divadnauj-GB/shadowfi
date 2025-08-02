import logging
import os
import subprocess


from utils.config_loader import load_config, save_config
from utils.constants import prompt_msg


GEN_VIVADO_PROJ_SCRIPT = "recreate_project.tcl"
BUILD_VIVADO_PROJ_SCRIPT = "build_project.tcl"
PROJ_NAME = "basic_test-3be11_prj"

BUILD_PROJECT_TCL_TEMPLATE = """# Open the Vivado project

open_project ./{PROJ_NAME}/{PROJ_NAME}.xpr

# Launch synthesis run
launch_runs synth_1
wait_on_run synth_1

# Launch implementation run and generate bitstream
launch_runs impl_1 -to_step write_bitstream
wait_on_run impl_1

# Optional: Generate reports or perform other actions
#report_timing_summary
#report_utilization

write_hw_platform -fixed -include_bit -force -file {HFPGA_NAME}-3be11.xsa

close_project
exit
"""


def run_cmd(cmd):
    logging.info(f"Running command: {cmd}")
    pr = subprocess.Popen(cmd, shell=True, executable="/bin/bash", preexec_fn=os.setsid)
    wait = True
    while wait:
        returnval = pr.wait()
        if returnval is not None:
            wait = False


def fpga_setup(config,args):
    project_name = config.get('project', {}).get('name', 'unknown')
    logging.info(prompt_msg.format(msg=f'Executing FPGA setup: {project_name}'))

    if args: 
        if args.emu_config:
            emu_config = args.emu_config
            if os.path.exists(emu_config):
                emu_config_data = load_config(emu_config)
                if isinstance(emu_config_data, dict):
                    config['project']['emu_config'].update(emu_config_data.get('emu_config', {}))
                    save_config(config, config['project']['proj_config_file'])
                else:
                    logging.error(f'Testbench config file {emu_config} does not contain a valid dictionary.')
            else:
                logging.warning(f'Simulation config file not found: {emu_config}')
        elif args.kwargs:
            kwargs_dict = args.kwargs.get('emu_config', {})
            print(f"Parsed kwargs: {kwargs_dict}")
            # Merge into config['project']['testbench_config']
            def deep_update(d, u):
                for k, v in u.items():
                    if isinstance(v, dict):
                        d[k] = deep_update(d.get(k, {}), v)
                    else:
                        d[k] = v
                return d
            config['project']['emu_config'] = deep_update(config['project'].get('emu_config', {}), kwargs_dict)
            save_config(config, config['project']['proj_config_file'])
    else:
        logging.warning('No fault injection configuration file provided. ')

    emu_config = config.get('project', {}).get('emu_config', {})
    sbtr_config = config.get('project',{}).get('sbtr_config', {})
    # Extract necessary parameters from the configuration
    dest_root_work_dir = config.get('project', {}).get('work_dir', '')
    src_root_work_dir = emu_config.get('src_data_root_dir', "")

    list_test_app_dirs = emu_config.get('test_data_info', {}).get('test_app_dirs', [])
    if not isinstance(list_test_app_dirs,list):
        list_test_app_dirs=[]

    for dir in list_test_app_dirs:
        src_path = os.path.abspath(os.path.join(src_root_work_dir, dir))
        dest_path = os.path.abspath(os.path.join(dest_root_work_dir, dir))
        os.system(f"mkdir -p {dest_path}")
        os.system(f"cp -rf {src_path}/* {dest_path}/")

    list_test_app_files = emu_config.get('test_data_info', {}).get('test_app_files', [])
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

    #work_dir = emu_config.get('src_data_root_dir', '')
    WORK_DIR = os.path.abspath(os.path.join(dest_root_work_dir, "./"))

    os.system(f"cp {os.path.abspath(FI_DESIGN_PATH)}/{FAULT_MODEL}_{F_LIST_NAME} {WORK_DIR}")

    vivado_proj_dir = emu_config.get('fpga_hw',{}).get('vivado_proj_dir', '')
    os.system(f"cp -rf {os.path.abspath(FI_DESIGN_PATH)}/* {os.path.abspath(vivado_proj_dir)}/sbtr/")

    if not args.no_gen_vivado_proj:
        generate_vivado_proj(config)

    if not args.no_compile_vivado:
        compile_vivado_proj(config)

    logging.info(prompt_msg.format(msg=f'FPGA setup for project {project_name} completed successfully.'))


def generate_vivado_proj(config):
    emu_config = config.get('project', {}).get('emu_config', {})
    vivado_proj_dir = emu_config.get('fpga_hw',{}).get('vivado_proj_dir', '')
    logging.info(prompt_msg.format(msg=f'Regenerating Vivado Project: {vivado_proj_dir}'))
    project_dir = os.path.join(os.path.abspath(vivado_proj_dir), PROJ_NAME)
    if os.path.exists(project_dir):
        logging.info(f'Removing existing Vivado project directory: {project_dir}')
        run_cmd(f"rm -rf {project_dir}")
    run_cmd(f"cd {os.path.abspath(vivado_proj_dir)}; vivado -mode tcl -source {GEN_VIVADO_PROJ_SCRIPT}")

    logging.info(prompt_msg.format(msg=f'Vivado Project at {vivado_proj_dir} generated successfully.'))

def update_vivado_proj(config):
    emu_config = config.get('project', {}).get('emu_config', {})
    vivado_proj_dir = emu_config.get('fpga_hw',{}).get('vivado_proj_dir', '')
    logging.info(prompt_msg.format(msg=f'Updating Vivado Project: {vivado_proj_dir}'))

    project_dir = os.path.join(os.path.abspath(vivado_proj_dir), PROJ_NAME)
    if not os.path.exists(project_dir):
        logging.info(f' Recreating vivado project in: {project_dir}')
        generate_vivado_proj(config)
    run_cmd(f"cd {os.path.abspath(vivado_proj_dir)}; vivado -mode tcl -source {GEN_VIVADO_PROJ_SCRIPT}")

    logging.info(prompt_msg.format(msg=f'Vivado Project at {vivado_proj_dir} generated successfully.'))

def compile_vivado_proj(config):
    emu_config = config.get('project', {}).get('emu_config', {})
    vivado_proj_dir = emu_config.get('fpga_hw',{}).get('vivado_proj_dir', '')
    design_name = emu_config.get('design_name', "")
    logging.info(prompt_msg.format(msg=f'Compiling Vivado Project: {vivado_proj_dir}'))

    update_vivado_proj(config)
    
    with open(os.path.join(os.path.abspath(vivado_proj_dir),BUILD_VIVADO_PROJ_SCRIPT ), 'w') as f:
        f.write(BUILD_PROJECT_TCL_TEMPLATE.format(PROJ_NAME=PROJ_NAME, HFPGA_NAME=design_name))

    run_cmd(f"cd {os.path.abspath(vivado_proj_dir)}; vivado -mode batch -source {BUILD_VIVADO_PROJ_SCRIPT}")

    run_cmd(f"cp -r {os.path.abspath(vivado_proj_dir)}/*.xsa ~/bitstreams")

    logging.info(prompt_msg.format(msg=f'Vivado project {vivado_proj_dir} completed successfully.'))
