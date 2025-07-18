
import argparse
from core import project, elaboration, place_and_route, sim_setup, sim_execute
from utils.logger import setup_logger
from utils.config_loader import load_config
import os

def cli_entry(current_project=None):
    root_dir = os.getenv('SHADOWFI_ROOT', os.path.join(os.path.dirname(os.path.abspath(__file__)),"/.."))
    setup_logger()
    parser = argparse.ArgumentParser(description='EDA Tool CLI')
    subparsers = parser.add_subparsers(dest='command')

    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('--name', required=True)
    create_parser.add_argument('--project-dir', default=f"{root_dir}/projects")

    load_parser = subparsers.add_parser('load')
    load_parser.add_argument('--project-dir', required=True)

    elaborate_parser = subparsers.add_parser('elaborate')
    elaborate_parser.add_argument('--config', required=False)  

    pnr_parser = subparsers.add_parser('pnr')
    pnr_parser.add_argument('--cmp-sel', default='random', choices=['random', 'top', 'hierarchy'], help='Target for place and route') 
    pnr_parser.add_argument('--fault-model', default='S@', choices=['S@', 'SET', 'SEU', 'MEU'], help='select fault model for saboteur insertion')
    pnr_parser.add_argument('--fault-sampling', default='Full', choices=['Full', 'Statistical'], help='Fault sampling strategy') 

    fisetup_parser = subparsers.add_parser('fisetup')
    fisetup_parser.add_argument('--setup-type', default="sim", choices=['sim', 'fpga'], help='Setup type for fault injection simulation')

    fiexec_parser = subparsers.add_parser('fiexec')
    fiexec_parser.add_argument('--campaign-type', default="standalone", choices=['standalone', 'slurm'], help='Campaign type for fault injection execution')
    
    
    args = parser.parse_args()
    proj_config_file = current_project
    if args.command == 'create':
        project.create_project(args.name, args.project_dir, template_config=f"{root_dir}/config/project_config.yaml")
        proj_config_file = project.load_project_config(os.path.join(args.project_dir, args.name))
    elif args.command == 'load':
        proj_config_file=project.load_project_config(args.project_dir)
        print(f"Project loaded from {proj_config_file}")
    elif args.command == 'elaborate':
        config = load_config(proj_config_file)
        elaboration.elaborate(config)
    elif args.command == 'pnr':
        config = load_config(proj_config_file)
        place_and_route.run_pnr(config,args)
    elif args.command == 'fisetup':
        config = load_config(proj_config_file)
        sim_setup.setup_fault_injection(config)
    elif args.command == 'fiexec':
        config = load_config(proj_config_file)
        sim_execute.execute_fault_injection(config)
    return proj_config_file


def run_all():
    root_dir = os.getenv('SHADOWFI_ROOT', os.path.join(os.path.dirname(os.path.abspath(__file__)),"/.."))
    setup_logger()

    parser = argparse.ArgumentParser(description='EDA Tool CLI')
    subparsers = parser.add_subparsers(dest='command')

    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('--name', required=True)
    create_parser.add_argument('--project-dir', default=f"{root_dir}/projects")

    load_parser = subparsers.add_parser('run_all')
    load_parser.add_argument('--project-dir', required=True)
    args = parser.parse_args()

    if args.command == 'create':
        project.create_project(args.name, args.project_dir, template_config=f"{root_dir}/config/project_config.yaml")
        proj_config_file = project.load_project_config(os.path.join(args.project_dir, args.name))
    elif args.command == 'run_all':
        proj_config_file=project.load_project_config(args.project_dir)
        print(f"Project loaded from {proj_config_file}")

    config = load_config(proj_config_file)
    elaboration.elaborate(config)
    place_and_route.run_pnr(config)
    sim_setup.setup_simulation(config)
    sim_execute.execute_simulation(config)

if __name__ == '__main__':
    cli_entry()
