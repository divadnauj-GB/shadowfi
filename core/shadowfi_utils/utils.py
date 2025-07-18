import json, yaml, os

from glob import glob

from .constants import (
    SCRIPTS_PATH,
    MAKEFILE_SBTR,
)


def read_yaml_file(file_name, mode):
    yaml_file = {}
    try:
        with open(file_name, mode) as fp:
            yaml_file = yaml.safe_load(fp)
    except OSError as err:
        print(f"The file was not saved due to {err}")
    return yaml_file


def read_verilog_file(file_name):
    with open(file_name, "r") as f:
        verilog_code = f.read()
    return verilog_code


def write_verilog_file(file_name, data):
    with open(file_name, "w") as f:
        f.write(data)


def write_json(hierarchy, file_name="hierarchy.json"):
    with open(file_name, "w") as f:
        json.dump(hierarchy, f, indent=4)
    print("Hierarchy saved to hierarchy.json")

def read_json(file_name):
    with open(file_name, "r") as f:
        hierarchy = json.load(f)
    return hierarchy


def create_makefile_tb_sbtr(
    SBTR_PATH,
    TOP_MODULE,
    SBTR_LIST_FILES=[],
    TB_PATH="",
    TB_TARGET_FILE="",
    TB_TOP="",
    TB_LIST_FILES=[],
    INC_DIRS=[],
    VERILATOR_PARAMS="--timing"
):
    if TB_TARGET_FILE == "":
        print(
            "SMS: No target TB file was selected, Please be sure you create your custom makefiles"
        )
        return

    if len(TB_LIST_FILES) == 0:
        print(
            f"SMS: The list of TB files was not provided, Searching for files in {TB_PATH}"
        )
        test_bench_files = []
        for filename in glob(f"{TB_PATH}/**/*.v", recursive=True):
            test_bench_files.append(os.path.abspath(filename))
    else:
        test_bench_files = TB_LIST_FILES

    target_tb_file = ""
    for file in test_bench_files:
        get_fname_from_path = file.split("/")[-1]
        if get_fname_from_path in TB_TARGET_FILE:
            target_tb_file = file
    test_bench_files.remove(target_tb_file)

    os.system(
        f"python {SCRIPTS_PATH}/test_bench_setup.py -f {target_tb_file} -c {TOP_MODULE}"
    )
    target_tb_file_name = target_tb_file.split("/")[-1]
    target_tb_file = target_tb_file.replace(
        target_tb_file_name, f"new_{target_tb_file_name}"
    )

    if len(SBTR_LIST_FILES) == 0:
        print(
            f"SMS: The list of SBTR files was not provided, Searching for files in {SBTR_PATH}"
        )
        sbtr_files = []
        for filename in glob(f"{SBTR_PATH}/**/*.v", recursive=True):
            sbtr_files.append(os.path.abspath(filename))
    else:
        sbtr_files = SBTR_LIST_FILES

    try:
        with open(
            os.path.abspath(os.path.join(TB_PATH, "verilator_sbtr.f")), "w"
        ) as fp:
            if len(INC_DIRS) > 0:
                for inc_dir in INC_DIRS:
                    fp.write(f"-I{os.path.abspath(inc_dir)}\n")
            else:
                fp.write(f"-I{os.path.abspath(SBTR_PATH)}\n")
                fp.write(f"-I{os.path.abspath(TB_PATH)}\n")
            for file in sbtr_files:
                fp.write(f" {os.path.abspath(file)}\n")
            if len(test_bench_files) > 0:
                for file in test_bench_files:
                    fp.write(f" {os.path.abspath(file)}\n") #it is possible to add -v or -sv to the config
            fp.write(f"{os.path.abspath(target_tb_file)}\n")
            fp.write(f"-Wno-moddup\n")
            fp.write(f"-Wno-fatal\n")
            fp.write(f"--top-module {TB_TOP}\n")
            fp.write(f"-o V{TB_TOP}\n")
    except OSError as err:
        print(f"The file was not created due to {err}")

    try:
        with open(os.path.abspath(os.path.join(TB_PATH, "Makefile_sbtr")), "w") as fp:
            fp.write(MAKEFILE_SBTR.format(verilator_params=VERILATOR_PARAMS))
    except OSError as err:
        print(f"The file was not created due to {err}")