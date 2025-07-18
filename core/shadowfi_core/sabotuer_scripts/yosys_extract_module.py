import os
import filecmp
import subprocess
import re
from glob import glob


import argparse
parser = argparse.ArgumentParser(description='Setup the testbench by incorporating the sbtr controller')
parser.add_argument('-p','--src-dir', default="Benchmarks/Cores/Adder32/src", type=str, help='Path to file', required=True)
parser.add_argument('-m','--module', default="Adder32", type=str, help='file', required=True)
parser.add_argument('-lf','--src-list-files', nargs='*', default=[], type=str, help='List of files separade by spaces', required=False)
parser.add_argument('-inc','--src-inc-dir', nargs='*', default=[], type=str, help='list of inc directories separated by spaces', required=False)
parser.add_argument('-o','--out-dir', default="Benchmarks/Cores/Adder32/sbtr", type=str, help='poutput directory', required=True)
parser.add_argument('-gv','--noexpr', action="store_true", help='Generate gate-level netlist', required=False)
parser.add_argument('-flt','--flatten', action="store_true", help='poutput directory', required=False)
parser.add_argument('-fno','--file-output', default="", type=str, help='poutput directory', required=False)


def yosys_extract_module(
    SRC_DIR,
    MODULE,
    OUT_DIR,
    SRC_LIST_FILES=[],
    SRC_INC_DIRS=[],
    SM=True,
    FLT=False,
    GV=False,
    FILE_OUT=""
):
    FILE_OUT_NAME = f"{FILE_OUT}_gate.v" if FILE_OUT else f"{MODULE}_gate.v"
    src_files = []
    if len(SRC_LIST_FILES)==0:
        for filename in glob(f"{SRC_DIR}/**/*.v", recursive=True):
            src_files.append(os.path.abspath(filename))
        print(f"YOSYS_RTL_1: The list of files was not given, the {SRC_DIR} path was used to search the files")
    else:        
        src_files=SRC_LIST_FILES

    inc_dirs = []
    if len(SRC_INC_DIRS)==0:
        inc_dirs.append(SRC_DIR)
        print(f"YOSYS_RTL_1: The list of in dirs was not given, the {SRC_DIR} path was used instead")
    else:
        inc_dirs=SRC_INC_DIRS
        

    os.system(f"mkdir -p {os.path.abspath(OUT_DIR)}")
    #os.chdir(f"{os.path.abspath(OUT_DIR)}")

    yosys_script = []
    yosys_script.append("# File: synth_generated.ys\n")

    for file in src_files:
        yosys_script.append(f"read_verilog -defer {file}\n") 

    
    yosys_script.append(f"hierarchy -check -top {MODULE}\n")
    yosys_script.append(f"proc; opt; memory; opt; fsm; opt\n")
    if FLT:
        yosys_script.append(f"flatten; opt\n")
    yosys_script.append("techmap; opt\n") # >> synth_generated.ys
    yosys_script.append("splitnets\n") # >> synth_generated.ys
    yosys_script.append("opt_clean -purge\n") # >> synth_generated.ys
    yosys_script.append("check\n") # >> synth_generated.ys
    yosys_script.append("clean\n") # >> synth_generated.ys
    if SM:
        yosys_script.append(f"select -module {MODULE}\n") # >> synth_generated.ys

    if GV:
        yosys_script.append(f"write_verilog -simple-lhs -selected -noexpr -noattr -attr2comment -renameprefix N_U {os.path.abspath(OUT_DIR)}/{FILE_OUT_NAME}") # >> synth_generated.ys
    else:
        yosys_script.append(f"write_verilog -simple-lhs -selected -noattr -attr2comment -renameprefix N_U {os.path.abspath(OUT_DIR)}/{FILE_OUT_NAME}") # >> synth_generated.ys
    
    yosys_script.append(f"tee -o {os.path.abspath(OUT_DIR)}/{FILE_OUT_NAME}_stats.sta stat") # >> synth_generated.ys

    file_content = " \n".join(yosys_script)
    with open(f"{os.path.abspath(OUT_DIR)}/synth_generated.ys","w") as fp:
        fp.write(file_content)
    print(file_content)

    os.system(f"yosys -s {os.path.abspath(OUT_DIR)}/synth_generated.ys")
    os.system(f"rm {os.path.abspath(OUT_DIR)}/synth_generated.ys")


def extract_verilog_module(SRC_DIR,
    MODULE,
    OUT_DIR,
    SRC_LIST_FILES=[],
    SRC_INC_DIRS=[],
    SM=True,
    FLT=False,
    GV=False,
    FILE_OUT=""
    ):

    if os.path.exists(SRC_DIR):
        print(f"{SRC_DIR} exist!")
    else:
        print(f"{SRC_DIR} does not exist!")
        raise("One of the input files does not exist! please be sure you made correct configuration")
    

    if os.path.exists(OUT_DIR):
        print(f"{OUT_DIR} exist!")
    else:
        print(f"{OUT_DIR} does not exist!")
        raise("One of the input files does not exist! please be sure you made correct configuration")


    src_list_files=[]
    if SRC_LIST_FILES:
        for file in SRC_LIST_FILES:
            if os.path.exists(file):
                print(f"{file} exist!")
                src_list_files.append(file.strip())
            else:
                print(f"{file} does not exist!")
                raise("One of the input files does not exist! please be sure you made correct configuration")

    src_inc_dirs = []
    if SRC_INC_DIRS:
        for dir in SRC_INC_DIRS:
            if os.path.exists(dir):
                print(f"{dir} exist!")
                src_inc_dirs.append(dir.strip())
            else:
                print(f"{dir} does not exist!")
                raise("One of the input inc dirs does not exist! please be sure you made correct configuration")

    yosys_extract_module(SRC_DIR,
                          MODULE,
                          OUT_DIR,
                          SRC_LIST_FILES=src_list_files,
                          SRC_INC_DIRS=src_inc_dirs,
                          FILE_OUT=FILE_OUT,
                          SM=SM,
                          FLT=FLT,
                          GV=GV)


def main():
    args=parser.parse_args()
    SRC_DIR = args.src_dir
    MODULE = args.module
    OUT_DIR = args.out_dir
    FILE_OUT = args.file_output
    GATES = args.noexpr
    FLATTEN = args.flatten



    files_str = args.src_list_files
    SRC_LIST_FILES=[]
    if files_str:
        for file in files_str:
            if os.path.exists(file):
                print(f"{file} exist!")
                SRC_LIST_FILES.append(file.strip())
            else:
                print(f"{file} does not exist!")
                raise("One of the input files does not exist! please be sure you made correct configuration")

    SRC_INC_DIRS=[]
    input_inc_dirs=args.src_inc_dir
    if input_inc_dirs:
        for dir in input_inc_dirs:
            if os.path.exists(dir):
                print(f"{dir} exist!")
                SRC_INC_DIRS.append(dir.strip())
            else:
                print(f"{dir} does not exist!")
                raise("One of the input inc dirs does not exist! please be sure you made correct configuration")


    yosys_extract_module(SRC_DIR,
                          MODULE,
                          OUT_DIR,
                          SRC_LIST_FILES=SRC_LIST_FILES,
                          SRC_INC_DIRS=SRC_INC_DIRS,
                          FILE_OUT=FILE_OUT,
                          SM=False,
                          FLT=FLATTEN,
                          GV=GATES)


if __name__=='__main__':
    main()