# eda_main.py

from cli.main import cli_entry

if __name__ == "__main__":
    cli_entry()


# cli/main.py
import click
from core.project import create_project
from core.elaboration import elaborate_project
from core.place_and_route import place_and_route
from core.sim_setup import setup_simulation
from core.sim_execute import execute_simulation

@click.group()
def cli_entry():
    """Main CLI entry point."""
    pass

@cli_entry.command()
@click.option('--name', prompt='Project name', help='Name of the new project')
def create(name):
    """Create a new EDA project."""
    create_project(name)

@cli_entry.command()
def elaborate():
    """Elaborate the project."""
    elaborate_project()

@cli_entry.command()
def pnr():
    """Place and Route the design."""
    place_and_route()

@cli_entry.command()
def simsetup():
    """Setup the simulation environment."""
    setup_simulation()

@cli_entry.command()
def simexec():
    """Execute the simulation."""
    execute_simulation()


# core/project.py
def create_project(name):
    print(f"[INFO] Creating project: {name}")
    # TODO: Add logic to create directory, configs, etc.


# core/elaboration.py
def elaborate_project():
    print("[INFO] Elaborating project...")
    # TODO: Add elaboration logic


# core/place_and_route.py
def place_and_route():
    print("[INFO] Running Place and Route...")
    # TODO: Add place and route logic


# core/sim_setup.py
def setup_simulation():
    print("[INFO] Setting up simulation...")
    # TODO: Add sim setup logic


# core/sim_execute.py
def execute_simulation():
    print("[INFO] Executing simulation...")
    # TODO: Add sim execution logic




# cli/main.py
import argparse
from core.project import create_project
from core.elaboration import elaborate_project
from core.place_and_route import place_and_route
from core.sim_setup import setup_simulation
from core.sim_execute import execute_simulation

def cli_entry():
    parser = argparse.ArgumentParser(description="EDA Tool CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create project command
    parser_create = subparsers.add_parser("create", help="Create a new project")
    parser_create.add_argument("--name", required=True, help="Project name")

    subparsers.add_parser("elaborate", help="Run project elaboration")
    subparsers.add_parser("pnr", help="Run place and route")
    subparsers.add_parser("simsetup", help="Setup simulation")
    subparsers.add_parser("simexec", help="Execute simulation")

    args = parser.parse_args()

    if args.command == "create":
        create_project(args.name)
    elif args.command == "elaborate":
        elaborate_project()
    elif args.command == "pnr":
        place_and_route()
    elif args.command == "simsetup":
        setup_simulation()
    elif args.command == "simexec":
        execute_simulation()
    else:
        parser.print_help()






###############################################################################################################
# eda_main.py

from cli.main import cli_entry

if __name__ == "__main__":
    cli_entry()


# cli/main.py
import argparse
import logging
from core.project import create_project
from core.elaboration import elaborate_project
from core.place_and_route import place_and_route
from core.sim_setup import setup_simulation
from core.sim_execute import execute_simulation
from utils.config_loader import load_config
from utils.logger import setup_logger

def cli_entry():
    setup_logger()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="EDA Tool CLI")
    parser.add_argument("--config", default="config/project_config.yaml", help="Path to config YAML file")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create project command
    parser_create = subparsers.add_parser("create", help="Create a new project")
    parser_create.add_argument("--name", required=False, help="Override project name")

    subparsers.add_parser("elaborate", help="Run project elaboration")
    subparsers.add_parser("pnr", help="Run place and route")
    subparsers.add_parser("simsetup", help="Setup simulation")
    subparsers.add_parser("simexec", help="Execute simulation")

    args = parser.parse_args()
    config = load_config(args.config)

    logger.info(f"Running command: {args.command}")

    if args.command == "create":
        project_name = args.name if args.name else config['project']['name']
        create_project(project_name, config)
    elif args.command == "elaborate":
        elaborate_project(config)
    elif args.command == "pnr":
        place_and_route(config)
    elif args.command == "simsetup":
        setup_simulation(config)
    elif args.command == "simexec":
        execute_simulation(config)
    else:
        parser.print_help()


# core/project.py
import logging

def create_project(name, config):
    logger = logging.getLogger(__name__)
    logger.info(f"Creating project: {name}")
    logger.debug(f"Output directory: {config['project'].get('output_dir')}")
    # TODO: Add logic to create directory, configs, etc.


# core/elaboration.py
import logging

def elaborate_project(config):
    logger = logging.getLogger(__name__)
    logger.info("Elaborating project...")
    logger.debug(f"Macro expansion enabled: {config['elaboration']['enable_macro_expansion']}")
    # TODO: Add elaboration logic


# core/place_and_route.py
import logging

def place_and_route(config):
    logger = logging.getLogger(__name__)
    logger.info("Running Place and Route...")
    logger.debug(f"P&R tool: {config['place_and_route']['tool']}")
    # TODO: Add place and route logic


# core/sim_setup.py
import logging

def setup_simulation(config):
    logger = logging.getLogger(__name__)
    logger.info("Setting up simulation...")
    logger.debug(f"Simulator: {config['simulation']['simulator']}")
    # TODO: Add sim setup logic


# core/sim_execute.py
import logging

def execute_simulation(config):
    logger = logging.getLogger(__name__)
    logger.info("Executing simulation...")
    logger.debug(f"Timescale: {config['simulation']['timescale']}")
    # TODO: Add sim execution logic


# utils/config_loader.py
import yaml

def load_config(path="config/project_config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)


# utils/logger.py
import logging
import sys

def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )



# run_create.py
from core.project import create_project
from utils.config_loader import load_config
from utils.logger import setup_logger

if __name__ == "__main__":
    setup_logger()
    config = load_config()
    project_name = config['project']['name']
    create_project(project_name, config)


# run_elaborate.py
from core.elaboration import elaborate_project
from utils.config_loader import load_config
from utils.logger import setup_logger

if __name__ == "__main__":
    setup_logger()
    config = load_config()
    elaborate_project(config)


# run_pnr.py
from core.place_and_route import place_and_route
from utils.config_loader import load_config
from utils.logger import setup_logger

if __name__ == "__main__":
    setup_logger()
    config = load_config()
    place_and_route(config)


# run_simsetup.py
from core.sim_setup import setup_simulation
from utils.config_loader import load_config
from utils.logger import setup_logger

if __name__ == "__main__":
    setup_logger()
    config = load_config()
    setup_simulation(config)


# run_simexec.py
from core.sim_execute import execute_simulation
from utils.config_loader import load_config
from utils.logger import setup_logger

if __name__ == "__main__":
    setup_logger()
    config = load_config()
    execute_simulation(config)


# eda_main.py

from cli.main import cli_entry

if __name__ == "__main__":
    cli_entry()


# cli/main.py
import argparse
import logging
from core.project import create_project
from core.elaboration import elaborate_project
from core.place_and_route import place_and_route
from core.sim_setup import setup_simulation
from core.sim_execute import execute_simulation
from utils.config_loader import load_config
from utils.logger import setup_logger

def cli_entry():
    setup_logger()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="EDA Tool CLI")
    parser.add_argument("--config", default="config/project_config.yaml", help="Path to config YAML file")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create project command
    parser_create = subparsers.add_parser("create", help="Create a new project")
    parser_create.add_argument("--name", required=False, help="Override project name")

    subparsers.add_parser("elaborate", help="Run project elaboration")
    subparsers.add_parser("pnr", help="Run place and route")
    subparsers.add_parser("simsetup", help="Setup simulation")
    subparsers.add_parser("simexec", help="Execute simulation")

    args = parser.parse_args()
    config = load_config(args.config)

    logger.info(f"Running command: {args.command}")

    if args.command == "create":
        project_name = args.name if args.name else config['project']['name']
        create_project(project_name, config)
    elif args.command == "elaborate":
        elaborate_project(config)
    elif args.command == "pnr":
        place_and_route(config)
    elif args.command == "simsetup":
        setup_simulation(config)
    elif args.command == "simexec":
        execute_simulation(config)
    else:
        parser.print_help()


# core/project.py
import logging

def create_project(name, config):
    logger = logging.getLogger(__name__)
    logger.info(f"Creating project: {name}")
    logger.debug(f"Output directory: {config['project'].get('output_dir')}")
    # TODO: Add logic to create directory, configs, etc.


# core/elaboration.py
import logging

def elaborate_project(config):
    logger = logging.getLogger(__name__)
    logger.info("Elaborating project...")
    logger.debug(f"Macro expansion enabled: {config['elaboration']['enable_macro_expansion']}")
    # TODO: Add elaboration logic


# core/place_and_route.py
import logging

def place_and_route(config):
    logger = logging.getLogger(__name__)
    logger.info("Running Place and Route...")
    logger.debug(f"P&R tool: {config['place_and_route']['tool']}")
    # TODO: Add place and route logic


# core/sim_setup.py
import logging

def setup_simulation(config):
    logger = logging.getLogger(__name__)
    logger.info("Setting up simulation...")
    logger.debug(f"Simulator: {config['simulation']['simulator']}")
    # TODO: Add sim setup logic


# core/sim_execute.py
import logging

def execute_simulation(config):
    logger = logging.getLogger(__name__)
    logger.info("Executing simulation...")
    logger.debug(f"Timescale: {config['simulation']['timescale']}")
    # TODO: Add sim execution logic


# utils/config_loader.py
import yaml

def load_config(path="config/project_config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)


# utils/logger.py
import logging
import sys

def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )







############################################
# eda_main.py

from cli.main import cli_entry

if __name__ == "__main__":
    cli_entry()


# cli/main.py
import argparse
import logging
import os
from core.project import create_project
from core.elaboration import elaborate_project
from core.place_and_route import place_and_route
from core.sim_setup import setup_simulation
from core.sim_execute import execute_simulation
from utils.config_loader import load_config
from utils.logger import setup_logger

def cli_entry():
    setup_logger()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="EDA Tool CLI")
    parser.add_argument("--config", default="config/project_config.yaml", help="Path to config YAML file")
    parser.add_argument("--project-dir", default="projects", help="Base directory for all projects")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create project command
    parser_create = subparsers.add_parser("create", help="Create a new project")
    parser_create.add_argument("--name", required=True, help="Name of the new project")

    subparsers.add_parser("elaborate", help="Run project elaboration")
    subparsers.add_parser("pnr", help="Run place and route")
    subparsers.add_parser("simsetup", help="Setup simulation")
    subparsers.add_parser("simexec", help="Execute simulation")

    args = parser.parse_args()

    if args.command == "create":
        create_project(args.name, args.config, args.project_dir)
    else:
        config = load_config(args.config)
        logger.info(f"Running command: {args.command}")

        if args.command == "elaborate":
            elaborate_project(config)
        elif args.command == "pnr":
            place_and_route(config)
        elif args.command == "simsetup":
            setup_simulation(config)
        elif args.command == "simexec":
            execute_simulation(config)
        else:
            parser.print_help()


# core/project.py
import logging
import os
import shutil
from utils.config_loader import load_config

def create_project(name, config_template_path, base_dir):
    logger = logging.getLogger(__name__)

    project_path = os.path.join(base_dir, name)
    os.makedirs(project_path, exist_ok=True)

    subdirs = ["src", "outputs", "logs"]
    for sub in subdirs:
        os.makedirs(os.path.join(project_path, sub), exist_ok=True)

    config_dest = os.path.join(project_path, "config.yaml")
    shutil.copy(config_template_path, config_dest)

    logger.info(f"Created project directory at: {project_path}")
    logger.info(f"Configuration copied to: {config_dest}")


# core/elaboration.py
import logging

def elaborate_project(config):
    logger = logging.getLogger(__name__)
    logger.info("Elaborating project...")
    logger.debug(f"Macro expansion enabled: {config['elaboration']['enable_macro_expansion']}")
    # TODO: Add elaboration logic


# core/place_and_route.py
import logging

def place_and_route(config):
    logger = logging.getLogger(__name__)
    logger.info("Running Place and Route...")
    logger.debug(f"P&R tool: {config['place_and_route']['tool']}")
    # TODO: Add place and route logic


# core/sim_setup.py
import logging

def setup_simulation(config):
    logger = logging.getLogger(__name__)
    logger.info("Setting up simulation...")
    logger.debug(f"Simulator: {config['simulation']['simulator']}")
    # TODO: Add sim setup logic


# core/sim_execute.py
import logging

def execute_simulation(config):
    logger = logging.getLogger(__name__)
    logger.info("Executing simulation...")
    logger.debug(f"Timescale: {config['simulation']['timescale']}")
    # TODO: Add sim execution logic


# utils/config_loader.py
import yaml

def load_config(path="config/project_config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)


# utils/logger.py
import logging
import sys

def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )




# Makefile for EDA Tool with per-project support

# Variables
PROJECT_NAME ?= my_design
PROJECT_DIR ?= projects
CONFIG_PATH := $(PROJECT_DIR)/$(PROJECT_NAME)/config.yaml

.PHONY: all create elaborate pnr simsetup simexec

all: create elaborate pnr simsetup simexec

create:
	@echo ">>> Creating project '$(PROJECT_NAME)' in $(PROJECT_DIR)..."
	python eda_main.py create --name $(PROJECT_NAME) --project-dir $(PROJECT_DIR)

elaborate:
	@echo ">>> Elaborating project '$(PROJECT_NAME)'..."
	python eda_main.py elaborate --config $(CONFIG_PATH)

pnr:
	@echo ">>> Running Place and Route for '$(PROJECT_NAME)'..."
	python eda_main.py pnr --config $(CONFIG_PATH)

simsetup:
	@echo ">>> Setting up simulation for '$(PROJECT_NAME)'..."
	python eda_main.py simsetup --config $(CONFIG_PATH)

simexec:
	@echo ">>> Executing simulation for '$(PROJECT_NAME)'..."
	python eda_main.py simexec --config $(CONFIG_PATH)
