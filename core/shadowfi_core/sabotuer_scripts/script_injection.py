import argparse
import re
import os
from .f_SEU_injection import inject_SEU
from .f_SABOTUER_Injection import inject_sabotuer


def single_module_single_file_rename(filename, target_sufix="_sbtr"):
    with open(filename,"r") as fp:
        file_content = fp.read()
    pattern = re.compile(r'([^\n\s]*(module)\s+([^\s]+)\s*(#\s*\(.*?\))?\s*(\(.*?\);))')
    matches = pattern.findall(file_content)
    print(matches)
    for match in matches:
        file_content=file_content.replace(match[0],f"{match[1]} {match[2]}{target_sufix} {match[3]} {match[4]}")
    with open(filename,"w") as fp:
        fp.write(file_content)


def get_num_faults_sbtr(filename):
    file_content = []
    with open(filename, "r") as fp:
        file_content = fp.readlines()
    Num_fault_locations = int(file_content[-1].split(",")[0]) + 1
    return Num_fault_locations

# Main function
def module_saboteur_insertion(SRC_FILE, TYPE_VALUE, MODULE, TOP_MODULE=""):
    # Run the selected function
    if TYPE_VALUE == "SEU":
        result = inject_SEU(SRC_FILE, MODULE)
    elif TYPE_VALUE == "SABOTUER":
        result = inject_sabotuer(SRC_FILE, MODULE)
    else:
        print(f"Error: Invalid TYPE value '{TYPE_VALUE}'. Valid options are 'SEU' or 'SABOTUER'.")
        return

    # Print the result
    print(result)

    sbtr_filename = SRC_FILE.replace(".v","_sbtr.v")
    sbtr_workdir = SRC_FILE.replace(SRC_FILE.split("/")[-1],"")
    if MODULE!=TOP_MODULE:
        single_module_single_file_rename(sbtr_filename, f"_sbtr")
    os.system(f"rm {SRC_FILE}")
    num_fault_locations = get_num_faults_sbtr(
            os.path.abspath(f"{os.path.abspath(sbtr_workdir)}/report_detailed_{TYPE_VALUE}_{MODULE}.csv")
        )
    return(num_fault_locations)



# Main function
def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run a function based on input arguments.")
    parser.add_argument('-ts','--type-saboteur', default="SABOTUER", type=str, help="Specify the function type as TYPE=SABOTUER or TYPE=SEU.", required=True)
    parser.add_argument('-f','--file', type=str, help="Specify the file as FILE=filename.", required=True)
    parser.add_argument('-m','--module', default="Adder32", type=str, help='target module', required=True)
    
    # Parse the arguments
    args = parser.parse_args()

    type_value = args.type_saboteur
    file_value = args.file
    module = args.module

    # Run the selected function
    if type_value == "SEU":
        result = inject_SEU(file_value, module)
    elif type_value == "SABOTUER":
        result = inject_sabotuer(file_value, module)
    else:
        print(f"Error: Invalid TYPE value '{type_value}'. Valid options are 'SEU' or 'SABOTUER'.")
        return

    # Print the result
    print(result)

# Check if this file is being run directly
if __name__ == "__main__":
    main()
