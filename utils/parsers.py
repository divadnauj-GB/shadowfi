import argparse
import sys

class CustomArgumenrParser(argparse.ArgumentParser):
    def error(self, message):
            sys.stderr.write(f'Error: {message}\n')
            self.print_help(sys.stderr)
            raise Exception(message)