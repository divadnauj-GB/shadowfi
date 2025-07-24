import os
import argparse
import json
from memory_profiler import memory_usage

parser = argparse.ArgumentParser(
    description="Setup the testbench by incorporating the sbtr controller"
)

parser.add_argument(
    "--mprofile",
    default="mprofile.dat",
    type=str,
    help="Input file with the configuration in yaml format",
)

parser.add_argument(
    "--timestampfile",
    default="timestamps.json",
    type=str,
    help="Input file with the configuration in yaml format",
)

parser.add_argument(
    "--output",
    default="mperformance.csv",
    type=str,
    help="Input file with the configuration in yaml format",
)


parser.add_argument(
    "-j",
    "--num-jobs",
    default=1,
    type=int,
    help="Select the max number of injections",
    required=False
)

def load_file(file_path):
    """
    Load the file and return its content.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")
    with open(file_path, "r") as file:
        content = file.readlines()
    return content

def load_json_file(file_path):
    """
    Load the JSON file and return its content.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")
    with open(file_path, "r") as file:
        content = json.load(file)
    return content

def mem_stats(list_vals):
    """
    Get memory usage statistics.
    """
    if len(list_vals) == 0:
        return (0, 0, 0)
    minv=min(list_vals)
    maxv=max(list_vals)
    avg=sum(list_vals)/len(list_vals)
    return (minv,maxv,avg)

def ex_time_stats(list_vals):
    """
    Get memory usage statistics.
    """
    if len(list_vals) == 0:
        return (0)
    elapsed=list_vals[-1]-list_vals[0]
    return (elapsed)

def main():
    args = parser.parse_args()
    mprofile_file = args.mprofile
    timestamp_file = args.timestampfile
    output_file = args.output
    NUM_JOBS = args.num_jobs
    try:
        mprofile_content = load_file(mprofile_file)
        timestamp_content = load_json_file(timestamp_file)
    except FileNotFoundError as e:
        print(e)
        return
    
    
    rtl_elab_prof=[]
    sbtr_place_route_prof=[]
    fault_list_gen_prof=[]
    fi_tb_compile_prof=[]
    fi_golden_sim_prof=[]
    fi_fault_sim_prof=[]



    ref_mprof=float(mprofile_content[1].strip().split()[2])
    fram_ref=timestamp_content["0_start"]

    for idx,line in enumerate(mprofile_content[1:]):
        fields_line = line.strip().split()
        val=float(fields_line[2])
        fields_line[2]=val-fram_ref
        fields_line[1]=float(fields_line[1])
        if val<timestamp_content["2_rtl_elab_end"]:
            rtl_elab_prof.append(fields_line)
        elif timestamp_content["2_rtl_elab_end"]<=val<timestamp_content["3_sbtr_place_route_end"]:
            sbtr_place_route_prof.append(fields_line)
        elif timestamp_content["3_sbtr_place_route_end"]<=val<timestamp_content["4_fault_list_gen_end"]:
            fault_list_gen_prof.append(fields_line)
        elif timestamp_content["4_fault_list_gen_end"]<=val<timestamp_content["5_fi_tb_compile_end"]:
            fi_tb_compile_prof.append(fields_line)
        elif timestamp_content["5_fi_tb_compile_end"]<=val<timestamp_content["6_fi_golden_sim_end"]:
            fi_golden_sim_prof.append(fields_line)
        elif timestamp_content["6_fi_golden_sim_end"]<=val<timestamp_content["7_fi_fault_sim_end"]:
            fi_fault_sim_prof.append(fields_line)

    with open(output_file, "w") as f:
        f.write(f"stage, min_mem, peak_mem, avg_mem, elapsed_time\n")
        (min_,max_,avg)=mem_stats([val[1] for val in rtl_elab_prof])
        elapsed_time=ex_time_stats([val[2] for val in rtl_elab_prof])
        print(f"RTL Elaboration: min={min_}, max={max_}, avg={avg}, elapsed_time={elapsed_time}")
        f.write(f"RTL Elaboration,{min_}, {max_}, {avg}, {elapsed_time}\n")
        (min_,max_,avg)=mem_stats([val[1] for val in sbtr_place_route_prof])
        elapsed_time=ex_time_stats([val[2] for val in sbtr_place_route_prof])
        print(f"SBTR Place Route: min={min_}, max={max_}, avg={avg}, elapsed_time={elapsed_time}")
        f.write(f"SBTR Place Route,{min_}, {max_}, {avg}, {elapsed_time}\n")
        (min_,max_,avg)=mem_stats([val[1] for val in fault_list_gen_prof])
        elapsed_time=ex_time_stats([val[2] for val in fault_list_gen_prof])
        print(f"Fault List Generation: min={min_}, max={max_}, avg={avg}, elapsed_time={elapsed_time}")
        f.write(f"Fault List Generation,{min_}, {max_}, {avg}, {elapsed_time}\n")
        (min_,max_,avg)=mem_stats([val[1] for val in fi_tb_compile_prof])
        elapsed_time=ex_time_stats([val[2] for val in fi_tb_compile_prof])
        print(f"Fault Injection TB Compilation: min={min_}, max={max_}, avg={avg}, elapsed_time={elapsed_time}")
        f.write(f"Fault Injection TB Compilation,{min_}, {max_}, {avg}, {elapsed_time}\n")
        (min_,max_,avg)=mem_stats([val[1] for val in fi_golden_sim_prof])
        elapsed_time=ex_time_stats([val[2] for val in fi_golden_sim_prof])
        print(f"Fault Injection Golden Simulation: min={min_}, max={max_}, avg={avg}, elapsed_time={elapsed_time}")
        f.write(f"Fault Injection Golden Simulation,{min_}, {max_}, {avg}, {elapsed_time}\n")
        (min_,max_,avg)=mem_stats([val[1] for val in fi_fault_sim_prof])
        elapsed_time=ex_time_stats([val[2] for val in fi_fault_sim_prof])
        print(f"Fault Injection Fault Simulation: min={min_}, max={max_}, avg={avg}, elapsed_time={elapsed_time/(NUM_JOBS*2)}")
        f.write(f"Fault Injection Fault Simulation,{min_}, {max_}, {avg}, {elapsed_time/(NUM_JOBS*2)}\n")

    # Process the content of the files


if __name__ == "__main__":
    main()

