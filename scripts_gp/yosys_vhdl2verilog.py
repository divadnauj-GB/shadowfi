import os
import filecmp
import subprocess
import re
from glob import glob


import argparse
parser = argparse.ArgumentParser(description='Setup the testbench by incorporating the sbtr controller')
parser.add_argument('-p','--src-dir', default="Benchmarks/Cores/Adder32/src", type=str, help='Path to file', required=True)
parser.add_argument('-t','--top-module', default="Adder32", type=str, help='file', required=True)
parser.add_argument('-lf','--src-list-files', nargs='*', default=[], type=str, help='List of files separade by spaces', required=False)
parser.add_argument('-par','--params', nargs='*', default=[], type=str, help='list of parameters assignments separated by spaces', required=False)
parser.add_argument('-inc','--src-inc-dir', nargs='*', default=[], type=str, help='list of inc directories separated by spaces', required=False)
parser.add_argument('-o','--out-dir', default="Benchmarks/Cores/Adder32/sbtr", type=str, help='poutput directory', required=True)
parser.add_argument('-fno','--file-output', default="", type=str, help='poutput directory', required=False)
parser.add_argument('-ghdl','--ghdl', nargs='+', help='poutput directory', required=False)




def yosys_rtl_elaboration(
    SRC_DIR,
    TOP_MODULE,
    OUT_DIR,
    GHDL="",
    SRC_LIST_FILES=[],
    PARAMS=[],
    SRC_INC_DIRS=[],
    FILE_OUT=""
):
    
    FILE_OUT_NAME = FILE_OUT if FILE_OUT else f"{TOP_MODULE}_rtl_elab.v"
    
    src_files = []
    if len(SRC_LIST_FILES)==0:
        for filename in glob(f"{SRC_DIR}/**/*.vhd", recursive=True):
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
    os.system(f"rm {os.path.abspath(OUT_DIR)}/*.v")
    #os.chdir(f"{os.path.abspath(OUT_DIR)}")

    yosys_script = []
    yosys_script.append("# File: synth_generated.ys\n")


    if GHDL:
        ghdlargs=" ".join(GHDL)
    else:
        ghdlargs=""
    yosys_script.append(f"ghdl --std=08 --work=work --workdir=build {ghdlargs} ")


    for param in PARAMS:
        yosys_script.append(f"-g{param[0]}={param[1]} ")
    
    yosys_script.append(f"-Pbuild ")

    for file in src_files:
        yosys_script.append(f" {file} ")
    
    yosys_script.append(f" -e {TOP_MODULE}\n")
       
    
    yosys_script.append(f"hierarchy -check -top {TOP_MODULE}\n")
    yosys_script.append(f"proc; opt\n")
    yosys_script.append(f"opt_clean -purge\n")
    yosys_script.append(f"write_verilog -noattr -attr2comment -simple-lhs -renameprefix ghdl_rtil_signal {os.path.abspath(OUT_DIR)}/{FILE_OUT_NAME}\n")

    file_content = "".join(yosys_script)
    with open(f"{os.path.abspath(OUT_DIR)}/synth_generated.ys","w") as fp:
        fp.write(file_content)
    print(file_content)

    os.system(f"yosys -m ghdl -s {os.path.abspath(OUT_DIR)}/synth_generated.ys")
    os.system(f"rm {os.path.abspath(OUT_DIR)}/synth_generated.ys")

    yosys_script = []
    yosys_script.append(f"read_verilog {os.path.abspath(OUT_DIR)}/{FILE_OUT_NAME}\n")# >> synth_generated.ys
    yosys_script.append(f"proc\n")# >> synth_generated.ys
    yosys_script.append(f"write_json {os.path.abspath(OUT_DIR)}/{FILE_OUT_NAME}.json\n") # >> synth_generated.ys

    file_content = "".join(yosys_script)
    with open(f"{os.path.abspath(OUT_DIR)}/synth_generated.ys","w") as fp:
        fp.write(file_content)
    print(file_content)

    os.system(f"yosys -s {os.path.abspath(OUT_DIR)}/synth_generated.ys")
    os.system(f"rm {os.path.abspath(OUT_DIR)}/synth_generated.ys")





def rtl_elaboration(SRC_DIR,
    TOP_MODULE,
    OUT_DIR,
    SRC_LIST_FILES=[],
    PARAMS=[],
    SRC_INC_DIRS=[],
    FILE_OUT=""
    ):

    if os.path.exists(SRC_DIR):
        print(f"{SRC_DIR} exist!")
    else:
        print(f"{SRC_DIR} does not exist!")
        raise("One of the input files does not exist! please be sure you made correct configuration")
    

    src_lits_files=[]
    if SRC_LIST_FILES:
        for file in SRC_LIST_FILES:
            if os.path.exists(file):
                print(f"{file} exist!")
                src_lits_files.append(file.strip())
            else:
                print(f"{file} does not exist!")
                raise("One of the input files does not exist! please be sure you made correct configuration")
    
    module_params=[]
    if PARAMS:
        for param_assign in PARAMS:
            fields = param_assign.split("=")
            if len(fields)==2:
                print(f"{param_assign} corect!")
                module_params.append(fields)
            else:
                print(f"{param_assign} seems to not be correct")
                raise("One of the input parameters is not correct, please be sure you enter the right configuration!")

    input_inc_dirs=[]
    if SRC_INC_DIRS:
        for dir in SRC_INC_DIRS:
            if os.path.exists(dir):
                print(f"{dir} exist!")
                input_inc_dirs.append(dir.strip())
            else:
                print(f"{dir} does not exist!")
                raise("One of the input inc dirs does not exist! please be sure you made correct configuration")


    yosys_rtl_elaboration(SRC_DIR,
                          TOP_MODULE,
                          OUT_DIR,
                          SRC_LIST_FILES=src_lits_files,
                          PARAMS=module_params,
                          SRC_INC_DIRS=input_inc_dirs,
                          FILE_OUT=FILE_OUT)









def main():
    args=parser.parse_args()
    SRC_DIR = args.src_dir
    TOP_MODULE = args.top_module
    OUT_DIR = args.out_dir
    FILE_OUT = args.file_output
    files_str = args.src_list_files
    ghdl = args.ghdl  # call ghdl argument as -ghdl="ghdl commands separated by spaces"

    SRC_LIST_FILES=[]
    if files_str:
        for file in files_str:
            if os.path.exists(file):
                print(f"{file} exist!")
                SRC_LIST_FILES.append(file.strip())
            else:
                print(f"{file} does not exist!")
                raise("One of the input files does not exist! please be sure you made correct configuration")
    
    PARAMS=[]
    input_params = args.params
    if input_params:
        for param_assign in input_params:
            fields = param_assign.split("=")
            if len(fields)==2:
                print(f"{param_assign} corect!")
                PARAMS.append(fields)
            else:
                print(f"{param_assign} seems to not be correct")
                raise("One of the input parameters is not correct, please be sure you enter the right configuration!")

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


    yosys_rtl_elaboration(SRC_DIR,
                          TOP_MODULE,
                          OUT_DIR,
                          GHDL=ghdl,
                          SRC_LIST_FILES=SRC_LIST_FILES,
                          PARAMS=PARAMS,
                          SRC_INC_DIRS=SRC_INC_DIRS,
                          FILE_OUT=FILE_OUT)


if __name__=='__main__':
    main()