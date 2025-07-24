
import os
import cmd
import shlex
import logging
import argparse
from cli.main import cli_entry
from utils.logger import setup_logger
from utils.constants import *

class ShadowfiShell(cmd.Cmd):
    intro = "Welcome to the SHADOWFI Tool shell. Type help or ? to list commands.\n"
    prompt = "Shadowfi> "
    doc_header = "Help (type help <Shadowfi cmd>):"
    misc_header = "Documented Shadowfi comands:"

    def __init__(self):
        super().__init__()
        self.current_project = None

    def default(self, line):
        import sys
        sys.argv = ['shadowfi_main.py'] + shlex.split(line)
        try:
            self.current_project=cli_entry(self.current_project)
        except Exception as e:
            logging.error(f"Error executing command '{line}': {e}")
            print(f"Error: {e}")
        
    def do_exit(self, arg):
        print("Exiting SHADOWFI shell.")
        return True

    def do_EOF(self, arg):
        return self.do_exit(arg)

    def help_create(self):
        print(create_help_str)
        
    def help_load(self):
        print(load_help_str)

    def help_elaborate(self):
        print(elaborate_help_str)

    def help_pnr(self):
        print(pnr_help_str)
    
    def help_tb_setup(self):
        print(tb_setup_help_str)

    def help_fsim_setup(self):
        print(fsim_setup_help_str)
    
    def help_fsim_exec(self):
        print(fsim_exec_help_str)

    
    

def main():
    os.environ['SHADOWFI_ROOT'] = os.path.dirname(os.path.abspath(__file__))  # export root directory
    setup_logger()
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="SHADOWFI Shell with optional script mode")
    parser.add_argument('-s', '--script', type=str, help="Script file to execute commands from")
    args = parser.parse_args()

    shell = ShadowfiShell()
    shell.current_project = None
    if args.script:
        try:
            with open(args.script, 'r') as f:
                for line in f:
                    cmd_line = line.strip()
                    if not cmd_line or cmd_line.startswith("#"):
                        continue
                    print(f"Executing: {cmd_line}")
                    shell.onecmd(cmd_line)
        except FileNotFoundError:
            print(f"Script file not found: {args.script}")
    else:
        shell.cmdloop()

if __name__ == '__main__':
    main()
