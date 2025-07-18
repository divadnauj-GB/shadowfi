
import os
import cmd
import shlex
import logging
from cli.main import cli_entry
from utils.logger import setup_logger

class EdaShell(cmd.Cmd):
    intro = "Welcome to the EDA Tool shell. Type help or ? to list commands.\n"
    prompt = "eda> "

    def __init__(self):
        super().__init__()
        self.current_project = None

    def default(self, line):
        import sys
        sys.argv = ['eda_main.py'] + shlex.split(line)
        try:
            self.current_project=cli_entry(self.current_project)
        except Exception as e:
            logging.error(f"Error executing command '{line}': {e}")
            print(f"Error: {e}")
        

    def do_exit(self, arg):
        print("Exiting EDA shell.")
        return True

    def do_EOF(self, arg):
        return self.do_exit(arg)

def main():
    os.environ['SHADOWFI_ROOT'] = os.path.dirname(os.path.abspath(__file__))  # export root directory
    setup_logger()
    EdaShell().cmdloop()

if __name__ == '__main__':
    main()
