
#import argparse
from core import fi_execute, fi_setup, project, elaboration, place_and_route, fi_fpga_exec, fi_fpga_setup
from utils.logger import setup_logger
from utils.config_loader import load_config, KeyValueAction
from utils.parsers import CustomArgumenrParser, argparse
import os

    

def cli_entry(current_project=None):
    root_dir = os.getenv('SHADOWFI_ROOT', os.path.join(os.path.dirname(os.path.abspath(__file__)),"/.."))
    setup_logger()
    parser = CustomArgumenrParser(description='SHADOWFI Tool CLI')#argparse.ArgumentParser(description='SHADOWFI Tool CLI')
    subparsers = parser.add_subparsers(dest='command')

    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('--name', required=True)
    create_parser.add_argument('--project-dir', default=f"{root_dir}/projects")
    create_parser.add_argument('--design-config', default=None, help='Path to the design configuration file')

    load_parser = subparsers.add_parser('load')
    load_parser.add_argument('--project-dir', required=True)

    elaborate_parser = subparsers.add_parser('elaborate')
    elaborate_parser.add_argument('--config', required=False)  

    pnr_parser = subparsers.add_parser('pnr')
    pnr_parser.add_argument('--cmp-sel', default='random', choices=['random', 'top', 'hierarchy'], help='Target for place and route') 
    pnr_parser.add_argument('--fault-model', default='S@', choices=['S@', 'SET', 'SEU', 'MEU'], help='select fault model for saboteur insertion')
    pnr_parser.add_argument('--fault-sampling', default='Full', choices=['Full', 'Statistical'], help='Fault sampling strategy') 
    pnr_parser.add_argument('--user-cmp-sel', default=None, help="components selection") 
    pnr_parser.add_argument('--max-sel-cmp', default=4, help="Maximum Number of selected components") 


    tb_setup_parser = subparsers.add_parser('tb_setup')
    tb_setup_parser.add_argument('--tb-config', default=None, help='Path to the testbench configuration file')
    tb_setup_parser.add_argument('--kwargs', nargs='*', action=KeyValueAction, help="Nested key-value pairs, e.g. a.b.c=val")
    
    fsim_setup_parser = subparsers.add_parser('fsim_setup')
    fsim_setup_parser.add_argument('--fsim-config', default=None, help='Path to the testbench configuration file')
    fsim_setup_parser.add_argument('--kwargs', nargs='*', action=KeyValueAction, help="Nested key-value pairs, e.g. a.b.c=val")
    fsim_setup_parser.add_argument('--run-script', default=None, help='Path to the testbench configuration file')
    fsim_setup_parser.add_argument('--sdc-check-script', default=None, help='Path to the testbench configuration file')
    fsim_setup_parser.add_argument('--noset-run-scripts', action="store_true", help= "enable setting any run.sh and sdc_check.sh scripts, otherwise directly provided by the user")

    fsim_exec_parser = subparsers.add_parser('fsim_exec')
    fsim_exec_parser.add_argument('--fsim-config', default=None, help='Path to the testbench configuration file')
    fsim_exec_parser.add_argument('--kwargs', nargs='*', action=KeyValueAction, help="Nested key-value pairs, e.g. a.b.c=val")
    fsim_exec_parser.add_argument('--hpc',action="store_true", help="enable HPC execution")
    #fsim_exec_parser.add_argument('--work-dir-root',default=None,  help="optionalworking directory root, useful when hpc job is executed")
    #fsim_exec_parser.add_argument('--slurm-jobid',default="./",  help="optionalworking directory root, useful when hpc job is executed")


    fi_fpga_setup_parser = subparsers.add_parser('fi_fpga_setup')
    fi_fpga_setup_parser.add_argument('--emu-config', default=None, help='Path to the configuration file')
    fi_fpga_setup_parser.add_argument('--no-compile-vivado', action="store_true", help='enable vivado compilation')
    fi_fpga_setup_parser.add_argument('--kwargs', nargs='*', action=KeyValueAction, help="Nested key-value pairs, e.g. a.b.c=val")


    fi_fpga_exec_parser = subparsers.add_parser('fi_fpga_exec')
    fi_fpga_exec_parser.add_argument('--config', default=None, help='Path to the testbench configuration file')

    shell_cmd_parser = subparsers.add_parser('shell')
    shell_cmd_parser.add_argument('--cmd',  nargs='+', required=True, help='Shell command to execute')
    
    proj_config_file = current_project

    try:
        args = parser.parse_args()
    except Exception as error:
        print(error)
        return proj_config_file
    
    if args.command == 'create':
        project.create_project(args.name, args.project_dir, template_config=f"{root_dir}/config/project_config.yaml",design_config=args.design_config)
        proj_config_file = project.load_project_config(os.path.join(args.project_dir, args.name))

    elif args.command == 'load':
        proj_config_file=project.load_project_config(args.project_dir)
        print(f"Project loaded from {proj_config_file}")
    elif args.command == 'elaborate':
        config = load_config(proj_config_file)
        elaboration.elaborate(config, args)
    elif args.command == 'pnr':
        config = load_config(proj_config_file)
        place_and_route.run_pnr(config,args)
    elif args.command == 'tb_setup':
        config = load_config(proj_config_file)
        fi_setup.setup_testbench(config,args)
    elif args.command == 'fsim_setup':
        config = load_config(proj_config_file)
        fi_setup.setup_fault_injection(config,args)
    elif args.command == 'fsim_exec':
        config = load_config(proj_config_file)
        fi_execute.execute_fault_injection(config,args)
    elif args.command == 'fi_fpga_setup':
        config = load_config(proj_config_file)
        fi_fpga_setup.fpga_setup(config,args)
    elif args.command == 'fi_fpga_exec':
        config = load_config(proj_config_file)
        fi_fpga_exec.fpga_execute(config)

    elif args.command == 'shell':
        if args.cmd:
            os.system(" ".join(args.cmd))
        else:
            print("No command provided to execute.")
    return proj_config_file



if __name__ == '__main__':
    cli_entry()
