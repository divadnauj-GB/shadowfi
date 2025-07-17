import os
import filecmp
import subprocess
import re


import argparse
parser = argparse.ArgumentParser(description='Setup the testbench by incorporating the sbtr controller')
parser.add_argument('-c','--component', default=".", type=str, help='Path to file')
parser.add_argument('-f','--file', default="./tb_Adder32.v", type=str, help='file')


def read_file_content(filename):
    with open(filename,"r") as file_testbench:
        file_content = file_testbench.read()
    return(file_content)

def fix_initial_begin(file_content):    
    init_begin_patt = re.compile(r'initial\s+.*?begin',re.DOTALL)
    init_begin_matches=init_begin_patt.findall(file_content)
    filter_init_beg=[]
    if init_begin_matches:
        for init_beg_match in init_begin_matches:
            if init_beg_match not in filter_init_beg:
                filter_init_beg.append(init_beg_match)
        for match in filter_init_beg:    
            file_content = file_content.replace(match,f"{match}\n\
                // wait until the FI configuration ends\n\
                wait(fi_done_sim);")
    else:
        print("Warning: It seems this test bench does not have initial begin,\
            Please check the design files to be sure the system waits \
            until the FI module finishes the FI configuration")
    return(file_content)


def write_top_tb(filename,content):    
    with open(filename,"w") as file_testbench:
        file_testbench.write(content)


def find_top_instance(filecontent,topname):
    comments_pattern = re.compile(r'(/[*].*?[*]/)|(//+.*?[\n])', re.DOTALL)
    match_comment = comments_pattern.findall(filecontent)
    print(match_comment)
    if match_comment:
        for match in match_comment:
            for group in match:
                if group!="":
                    filecontent = filecontent.replace(group,"\n")
        
    initial_pattern=f"[^\\n\s]*({topname}\s+(#\(.+?\)\s*\))?)\s*([^(\s]+).*?(\(.*?\);)"
    print(initial_pattern)
    pattern_to_match = re.compile(initial_pattern,re.DOTALL)
    matches=pattern_to_match.findall(filecontent)
    print(matches)
    if matches:
        for match in matches:
            return (filecontent,match[1],match[2],match[0])
    return None


def extract_module_from_file(file_content):
    general_module = re.compile(r'module.*?endmodule',re.DOTALL)
    modules = general_module.findall(file_content)
    return(modules)


def main():
    # this are the configuration parameters of the accelerator passed trought the TB
    args=parser.parse_args()
    COMPONENT=args.component
    FILE=args.file
    


    file = read_file_content(FILE)
    
    modules = extract_module_from_file(file)
    
    for module in modules:
        (new_module,params,top_instance, params_to_replace) = find_top_instance(module,COMPONENT)
        print(params_to_replace)
        if top_instance:
            inst_sbtr_cntrl=["wire fi_done_sim; // Signal to stall the tb befor the FI to happen\n"]
            inst_sbtr_cntrl.append("/*FI controller: this instance controlls the saboteurs to insert faults.*/\n")
            inst_sbtr_cntrl.append(f"tb_sbtr_cntrl FI(.TFEn( {top_instance}.i_FI_CONTROL_PORT[1]), \n\
                .CLK( {top_instance}.i_FI_CONTROL_PORT[3]), \n\
                .RST( {top_instance}.i_FI_CONTROL_PORT[2]), \n\
                .EN( {top_instance}.i_FI_CONTROL_PORT[0]), \n\
                .SI( {top_instance}.i_SI), \n\
                .DONE(fi_done_sim));\n")
            inst_sbtr_cntrl.append("endmodule\n")

            
            if params:
                new_module=new_module.replace(params_to_replace,f"{COMPONENT}\n")
            inst_added = "".join(inst_sbtr_cntrl)
            new_module=new_module.replace("endmodule",inst_added)
            new_module=fix_initial_begin(new_module)
            print(module)
            print(new_module)
            file = file.replace(module,new_module)
            
            
    fname=FILE.split("/")[-1]
    write_fname=FILE.replace(fname,f"new_{fname}")
    write_top_tb(write_fname, file)
  
    


if __name__=='__main__':
    main()