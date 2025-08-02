import os
import argparse
import re
parser = argparse.ArgumentParser(description="Generate Vivado TCL project script for HyperFPGA benchmark.")
parser.add_argument('--proj-dir', type=str, required=True, help='Output file for the generated TCL script.')

PROJ_NAME = "basic_test-3be11_prj"
IMPORTS = f"/{PROJ_NAME}/{PROJ_NAME}.srcs/utils_1/imports/"


GEN_PROJ_TCL_TEMPLATE = """# Generated Vivado TCL Project Script for HyperFPGA Benchmark
open_project ./{PROJ_NAME}/{PROJ_NAME}.xpr
write_project_tcl -origin_dir_override ./ -paths_relative_to ./ -all_properties -force recreate_project.tcl
close_project
exit
"""

NEW_SOURCES_TEMPLATE = """# This is a template for reading the new sbtr files
set obj [get_filesets sources_1]
set files {}
foreach f [glob -nocomplain -directory "./cut_io_interface" *.v] {
            lappend files [file normalize $f]
        }
foreach f [glob -nocomplain -directory "./sbtr" *.v] {
            lappend files [file normalize $f]
        }
add_files -norecurse -fileset $obj $files

# foreach f [glob -nocomplain -directory "./sbtr" *.v] {
#     set file [file normalize $f]
#     set file_obj [get_files -of_objects [get_filesets sources_1] [list "*$file"]]
#     set_property -name "file_type" -value "Verilog" -objects $file_obj
#     set_property -name "is_enabled" -value "1" -objects $file_obj
#     set_property -name "is_global_include" -value "0" -objects $file_obj
#     set_property -name "library" -value "xil_defaultlib" -objects $file_obj
#     set_property -name "path_mode" -value "RelativeFirst" -objects $file_obj
#     set_property -name "used_in" -value "synthesis implementation simulation" -objects $file_obj
#     set_property -name "used_in_implementation" -value "1" -objects $file_obj
#     set_property -name "used_in_simulation" -value "1" -objects $file_obj
#     set_property -name "used_in_synthesis" -value "1" -objects $file_obj
# }
"""

NEW_FILE_IMPORTS_TEMPLATE = """# Generic loop to import all .v files in ./sbtr if not already present
foreach f [glob -nocomplain ./cut_io_interface/*.v] {
    set fname [file tail $f]
    if { [get_files $fname] == "" } {
        import_files -quiet -fileset sources_1 $f
    }
}
foreach f [glob -nocomplain ./sbtr/*.v] {
    set fname [file tail $f]
    if { [get_files $fname] == "" } {
        import_files -quiet -fileset sources_1 $f
    }
}
"""

BUILD_PROJECT_TCL_TEMPLATE = """# Open the Vivado project

open_project ./{PROJ_NAME}/{PROJ_NAME}.xpr

# Launch synthesis run
launch_runs synth_1
wait_on_run synth_1

# Launch implementation run and generate bitstream
launch_runs impl_1 -to_step write_bitstream
wait_on_run impl_1

# Optional: Generate reports or perform other actions
#report_timing_summary
#report_utilization

write_hw_platform -fixed -include_bit -force -file {HFPGA_NAME}-3be11.xsa

close_project
exit
"""

def extract_sources_section(content:str):
    # Use re.DOTALL to match across newlines
    match = re.search(
        r"# Set 'sources_1' fileset object\n(.*?)# Set 'sources_1' fileset file properties for local files",
        content,
        re.DOTALL
    )
    if match:
        return match.group(1).strip()
    else:
        return None


def extract_bd_sources(content):
    # Match from the marker to the next blank line or end of file
    match = re.search(
        r"# Adding sources referenced in BDs, if not already added\n(.*?)(?:\n\s*\n|$)",
        content,
        re.DOTALL
    )
    if match:
        return match.group(1).strip()
    else:
        return None

def run_cmd(cmd):
    """Run a shell command and print the output."""
    print(f"Running command: {cmd}")
    os.system(cmd)  

def read_generated_tcl_file(file_path):
    """Read the generated TCL file and return its content."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read()
    else:
        print(f"File {file_path} does not exist.")
        return None

def save_modified_tcl_file(file_path, content):
    """Save the modified content to the specified TCL file."""
    with open(file_path, 'w') as file:
        file.write(content)
    print(f"Modified TCL file saved to {file_path}")

def recreate_script_generation():
    args = parser.parse_args()
    proj_dir = args.proj_dir
    if not os.path.exists(os.path.abspath(proj_dir)):
        print(f"The project directory {proj_dir} does not exist.")
        return
    
    with open(os.path.join(proj_dir, "generate_vivado_tcl_prj.tcl"), 'w') as f:
        f.write(GEN_PROJ_TCL_TEMPLATE.format(PROJ_NAME=PROJ_NAME))

    run_cmd(f"cd {proj_dir} ; vivado -mode tcl -source generate_vivado_tcl_prj.tcl")

    recreate_project_tcl = read_generated_tcl_file(os.path.join(proj_dir, "recreate_project.tcl"))
    recreate_project_tcl = recreate_project_tcl.replace(f"{IMPORTS}", "/")
    recreate_project_tcl = recreate_project_tcl.replace(f"{proj_dir}", ".")
    sources_section = extract_sources_section(
       recreate_project_tcl
    )
    if sources_section:
        recreate_project_tcl = recreate_project_tcl.replace(sources_section, NEW_SOURCES_TEMPLATE)

    section_bd = extract_bd_sources(
        recreate_project_tcl
    )
    if section_bd:
        recreate_project_tcl = recreate_project_tcl.replace(section_bd, NEW_FILE_IMPORTS_TEMPLATE)
    recreate_project_tcl = recreate_project_tcl + "\n exit\n"
    save_modified_tcl_file(os.path.join(proj_dir, "recreate_project.tcl"), recreate_project_tcl)

    run_cmd(f"rm -rf {proj_dir}/{PROJ_NAME}")
    run_cmd(f"rm -rf {proj_dir}/.Xil")
    run_cmd(f"rm -rf {proj_dir}/.Xiltemp")
    run_cmd(f"rm -rf {proj_dir}/.git")
    run_cmd(f"rm {proj_dir}/*.log")
    run_cmd(f"rm {proj_dir}/*.jou")
    run_cmd(f"rm {proj_dir}/*.txt")
    run_cmd(f"rm {proj_dir}/*.pdf")
    run_cmd(f"rm {proj_dir}/*.str")
    run_cmd(f"rm -f {proj_dir}/core-comblock/.git")

    with open(os.path.join(proj_dir, "build_project.tcl"), 'w') as f:
        f.write(BUILD_PROJECT_TCL_TEMPLATE.format(PROJ_NAME=PROJ_NAME, HFPGA_NAME="TCU_1_SBTR"))

if __name__ == "__main__":
    # Call the main function to generate the TCL script
    recreate_script_generation()