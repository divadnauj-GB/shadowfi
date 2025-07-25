
import os
import subprocess
import shutil
import json
import multiprocessing as mp
import itertools
import logging

from core.shadowfi_utils.constants import ROOT
from utils.constants import sbatch_template

def run_cmd(cmd):
    logging.info(f"Running command: {cmd}")
    pr = subprocess.Popen(cmd, shell=True, executable="/bin/bash", preexec_fn=os.setsid)
    wait = True
    while wait:
        returnval = pr.wait()
        if returnval is not None:
            wait = False


def save_file(file_name, mode, data):
    try:
        with open(file_name, mode) as fp:
            for line in data:
                fp.write(line)
    except OSError as err:
        print(f"The file was not saved due to {err}")

def create_fault_descriptor(fi_structure):
    modules = fi_structure["modules"]
    sr_leght = fi_structure["sr_lenght"]
    component = fi_structure["component"]
    start_bit_pos = fi_structure["start_bit_pos"]
    end_bit_pos = fi_structure["end_bit_pos"]
    bit_pos = fi_structure["bit_pos"]
    f_cntrl = fi_structure["f_model"]
    seu_time = fi_structure["seu_time"]
    
    with open("fault_descriptor.txt", "w") as file:
        file.write(f"{f_cntrl}\n")
        file.write(f"{modules}\n")
        file.write(f"{component}\n")
        file.write(f"{sr_leght}\n")
        file.write(f"{seu_time}\n")
        file.write(f"{start_bit_pos}\n")
        file.write(f"{end_bit_pos}\n")
        for idx in range(fi_structure["sr_lenght"]):
            absolute_bit_pos = bit_pos + start_bit_pos
            if idx>= start_bit_pos and idx < end_bit_pos:
                if idx == absolute_bit_pos:
                    file.write(f"{1}\n")
                else:
                    if idx == end_bit_pos-2:
                        file.write(f"{f_cntrl&1}\n")
                        f_cntrl = f_cntrl >> 1
                    elif idx == end_bit_pos -1:
                        file.write(f"{f_cntrl&1}\n")
                        f_cntrl = f_cntrl >> 1
                    else:
                        file.write(f"{0}\n")                                
            else:
                file.write(f"{0}\n")


def fault_classification(work_dir, fi_structure, fi_config={}):
    component = fi_structure["component"]
    bit_pos = fi_structure["bit_pos"]
    fault_model = fi_structure["f_model"]

    f_model_str = fi_config.get('project',{}).get('sbtr_config').get('fault_model',"S@")

    sim_config = fi_config.get('project',{}).get('sim_config', {})

    tb_sdc_check_ags = sim_config.get('tb_sdc_check_info', {}).get('tb_sdc_check_args', '')
    tb_sdc_check_env_vars = sim_config.get('tb_sdc_check_info', {}).get('tb_sdc_check_env_vars', [])
    if not isinstance(tb_sdc_check_env_vars, list):
        tb_sdc_check_env_vars = []
    tb_run_env_vars_str = " ".join([f"export {var};" for var in tb_sdc_check_env_vars])
    tb_sdc_check_script = sim_config.get('tb_sdc_check_info',{}).get('tb_sdc_check_script', 'sdc_check.sh')

    tb_sdc_check_script_path = os.path.abspath(os.path.join(work_dir,tb_sdc_check_script))

    run_cmd(f"{tb_run_env_vars_str} bash {tb_sdc_check_script_path} {tb_sdc_check_ags}")
    res_message = "Masked"
    if os.path.getsize("logs/special_check.log") == 0:
        res_message = "Masked"
        os.system(f"rm -r logs")
    else:
        res_message = "SDC"
        tmp_dir = f"C{component}_B{bit_pos}_F{fault_model}"
        shutil.rmtree(tmp_dir, True)
        os.system(f"mv logs {tmp_dir}")
        shutil.make_archive(tmp_dir, "gztar", tmp_dir)  # archieve the outputs
        os.system(f"mv *.gz {f_model_str}_logs/")
        shutil.rmtree(tmp_dir, True)

    return res_message


def run_fault_free_simulation(work_dir,fi_config={}):
    sbtr_config = fi_config.get('project',{}).get('sbtr_config', {})
    sim_config = fi_config.get('project',{}).get('sim_config', {})

    fault_model = sbtr_config.get('fault_model', 'S@')
    num_target_components = int(sim_config.get('num_target_components', 0))
    total_bit_shift = int(sim_config.get('total_bit_shift', 0))
    tb_run_ags = sim_config.get('tb_run_info', {}).get('tb_run_args', '')
    tb_run_env_vars = sim_config.get('tb_run_info', {}).get('tb_run_env_vars', [])
    if not isinstance(tb_run_env_vars, list):
        tb_run_env_vars = []
    tb_run_env_vars_str = " ".join([f"export {var};" for var in tb_run_env_vars])
    tb_run_script = sim_config.get('tb_run_info',{}).get('tb_run_script', 'run.sh')

    tb_run_script_path = os.path.abspath(os.path.join(work_dir, tb_run_script))

    fi_structure = {
        "modules": num_target_components,  # 
        "sr_lenght": total_bit_shift,  # 
        "f_model": 3,  # fault model: 0-> stuck-at-0, 1: stuck-at-1, 2: bit-flip
        "component": 0,
        "start_bit_pos": 0,
        "end_bit_pos": 0,
        "bit_pos": 0,
        "seu_time": 0,
    }

    work_sim_dir = sim_config.get('work_sim_dir', '')
    golden_work_dir = os.path.abspath(os.path.join(work_dir,work_sim_dir))

    os.chdir(golden_work_dir)
    os.system(f"rm -r {fault_model}_logs")
    os.system(f"mkdir -p {fault_model}_logs")
    create_fault_descriptor(fi_structure)  # all disabled
    run_cmd(f"export GOLDEN=1; {tb_run_env_vars_str} bash {tb_run_script_path} {tb_run_ags}" )
    
    root_dir = fi_config.get('shadowfi_root',"")
    os.chdir(root_dir)
    return


def run_one_injection_job(work_dir, fi_structure, fi_config={}):
    sbtr_config = fi_config.get('project',{}).get('sbtr_config', {})
    sim_config = fi_config.get('project',{}).get('sim_config', {})

    fault_model = sbtr_config.get('fault_model', 'S@')
    tb_run_ags = sim_config.get('tb_run_info', {}).get('tb_run_args', '')
    tb_run_env_vars = sim_config.get('tb_run_info', {}).get('tb_run_env_vars', [])
    if not isinstance(tb_run_env_vars, list):
        tb_run_env_vars = []
    tb_run_env_vars_str = " ".join([f"export {var};" for var in tb_run_env_vars])
    tb_run_script = sim_config.get('tb_run_info',{}).get('tb_run_script', 'run.sh')

    tb_run_script_path = os.path.abspath(os.path.join(work_dir,tb_run_script))

    create_fault_descriptor(fi_structure)
    os.system(f"mkdir -p logs")
    run_cmd(f"{tb_run_env_vars_str} bash {tb_run_script_path} {tb_run_ags}")
    fault_class = fault_classification(work_dir,fi_structure, fi_config=fi_config)
    return fault_class



def run_one_job_fault_simulation(work_dir, fi_config={}):
    sbtr_config = fi_config.get('project',{}).get('sbtr_config', {})
    sim_config = fi_config.get('project',{}).get('sim_config', {})

    fault_list_name = fi_config.get('project', {}).get('fault_list_name', 'fault_list.csv')
    fault_model = sbtr_config.get('fault_model', 'S@')
    fault_list_name = f"{fault_model}_{fault_list_name}"
    F_sim_report = fi_config.get('project', {}).get('fault_sim_report', 'fsim_report.csv')
    max_num_inj = sim_config.get('max_num_faults', -1)
    num_target_components = int(sim_config.get('num_target_components', 0))
    total_bit_shift = int(sim_config.get('total_bit_shift', 0))
    
    work_sim_dir = sim_config.get('work_sim_dir', '')
    work_path_dir = os.path.abspath(os.path.join(work_dir,work_sim_dir))

    os.chdir(work_path_dir)
    with open(fault_list_name, "r") as f:
        fault_list = f.readlines()
    if len(fault_list) > 0:
        fault_list = [fault.strip().split(",") for fault in fault_list]
    else:
        print("No fault list found")
        return
    
    sdc_count = 0
    masked = 0
    simulation_report = []
    fi_structure = {
        "modules": num_target_components,  # 
        "sr_lenght": total_bit_shift,  # 
        "f_model": 3,  # fault model: 0-> stuck-at-0, 1: stuck-at-1, 2: bit-flip
        "component": 0,
        "start_bit_pos": 0,
        "end_bit_pos": 0,
        "bit_pos": 0,
        "seu_time": 0,
    }
    for idx, fault_info in enumerate(fault_list):
        # generate one fault descriptor
        # List_injections.append([idx, inst, module, start_bit_pos, end_bit_pos, fault_index, ftype, seutime])
        fi_structure["component"] = int(fault_info[0])
        fi_structure["start_bit_pos"] = int(fault_info[3])
        fi_structure["end_bit_pos"] = int(fault_info[4])
        fi_structure["bit_pos"] = int(fault_info[5])
        fi_structure["f_model"] = int(fault_info[6])
        fi_structure["seu_time"] = int(fault_info[7])
        result_sim = run_one_injection_job(work_dir, fi_structure, fi_config)
        if result_sim == "Masked":
            masked += 1
        else:
            sdc_count += 1
        result = f"{fault_info[0]},{fault_info[1]},{fault_info[2]},{fault_info[3]},{fault_info[4]},{fault_info[5]},{fault_info[6]},{fault_info[7]},{result_sim}\n"
        simulation_report.append(result)
        print(result)
        if idx>=max_num_inj and max_num_inj>0:
            break

    print(f"SDC: {sdc_count}, Masked: {masked}")
    save_file(f"{fault_model}_{F_sim_report}", "w", simulation_report)
    root_dir = fi_config.get('shadowfi_root',"")
    os.chdir(root_dir)


def run_fault_simulation(work_dir, fi_config={}, slurm_jobid="./"):
    #if WORK_DIR[-1] == "/":
    #    work_dir_clean = WORK_DIR[:-1]
    #else:
    #    work_dir_clean = WORK_DIR
    
    sbtr_config = fi_config.get('project',{}).get('sbtr_config', {})
    sim_config = fi_config.get('project',{}).get('sim_config', {})
    fault_list_name = fi_config.get('project', {}).get('fault_list_name', 'fault_list.csv')
    fault_model = sbtr_config.get('fault_model', 'S@')
    fault_list_name = f"{fault_model}_{fault_list_name}"

    F_sim_report = fi_config.get('project', {}).get('fault_sim_report', 'fsim_report.csv')
    num_jobs = sim_config.get('jobs', 1)
    num_workers = sim_config.get('workers', 10)
    work_sim_dir = sim_config.get('work_sim_dir', '')

    #work_dir_clean = os.path.abspath(fi_config.get('project', {}).get('work_dir', ''))
    work_dir_clean = work_dir
    src_work_path_dir = os.path.abspath(os.path.join(work_dir_clean,work_sim_dir))
    #work_dir_rel = work_dir_clean.split("/")[-1]
    work_dir_rel = os.path.abspath(fi_config.get('project', {}).get('root_proj_dir', ''))
    parallel_sims_path = os.path.abspath(os.path.join(work_dir_rel,slurm_jobid,".parsims"))
    os.system(f"rm -r {parallel_sims_path}")
    os.system(f"mkdir -p {parallel_sims_path}")
    # check if multiple jobs are required
    if num_jobs > 1:
        # read the fault list
        fault_list_job = []
        with open(f"{os.path.abspath(src_work_path_dir)}/{fault_list_name}", "r") as f:
            fault_list = f.readlines()
            if len(fault_list) == 0:
                print("No fault list found")
                return
            else:
                fault_list_job = [fault_list[job_id::num_jobs] for job_id in range(num_jobs)]
        
        # create hidden work directories       
        list_work_dir = []
        for job_id in range(num_jobs):
            new_work_dir = os.path.abspath(f"{parallel_sims_path}/.job{job_id}")
            list_work_dir.append(new_work_dir)
            os.system(f"cp -rf {work_dir_clean} {new_work_dir}")
            new_work_sim_dir = os.path.abspath(os.path.join(new_work_dir, work_sim_dir))
            save_file(f"{os.path.abspath(new_work_sim_dir)}/{fault_list_name}", "w", fault_list_job[job_id])
            
        # run the jobs
        with mp.Pool(processes=num_workers) as pool:
            pool.starmap_async(run_one_job_fault_simulation, zip(list_work_dir, itertools.repeat(fi_config)))
            pool.close()
            pool.join()
           
        # merge the results
        os.system(f"echo  > {os.path.abspath(src_work_path_dir)}/{fault_model}_{F_sim_report}")
        for job_work_dir in list_work_dir:
            new_work_sim_dir = os.path.abspath(os.path.join(job_work_dir, work_sim_dir))
            os.system(f"cat {new_work_sim_dir}/{fault_model}_{F_sim_report} >> {os.path.abspath(src_work_path_dir)}/{fault_model}_{F_sim_report}")
            os.system(f"cp -rf {new_work_sim_dir}/{fault_model}_logs {os.path.abspath(src_work_path_dir)}")
            os.system(f"rm -r {job_work_dir}")
            print(f"rm -r {job_work_dir}")
        os.system(f"rm -r {parallel_sims_path}")
        print("Fault simulation finished")               

    else:
        # run the fault simulation in one job
        new_work_dir = os.path.abspath(f"{parallel_sims_path}/.job0")
        os.system(f"cp -rf {work_dir_clean} {new_work_dir}")
        run_one_job_fault_simulation(new_work_dir, fi_config)
        new_work_sim_dir = os.path.abspath(os.path.join(new_work_dir, work_sim_dir))
        os.system(f"echo  > {os.path.abspath(src_work_path_dir)}/{fault_model}_{F_sim_report}")
        os.system(f"cat {new_work_sim_dir}/{fault_model}_{F_sim_report} >> {os.path.abspath(src_work_path_dir)}/{fault_model}_{F_sim_report}")
        os.system(f"cp -rf {new_work_sim_dir}/{fault_model}_logs {os.path.abspath(src_work_path_dir)}")
        os.system(f"rm -r {new_work_dir}")
        os.system(f"rm -r {parallel_sims_path}")
        print("Fault simulation finished")

    logs_path_dir = os.path.abspath(os.path.join(work_dir_rel,"logs"))
    os.system(f"cp -r {src_work_path_dir}/*_logs {logs_path_dir}")
    os.system(f"cp {src_work_path_dir}/*.csv {logs_path_dir}")
    return
    ...
    
    
if __name__ == "__main__":
    
    fi_config = {
        "FAULT_LIST_NAME": "S@_fault_list.csv",
        "FAULT_MODEL": "S@",
        "F_SIM_REPORT": "fsim_report.csv",
        "MAX_NUM_INJ": 1,
        "NUM_TARGET_COMPONENTS": 64,
        "TOTAL_BIT_SHIFT": 5800,
        "JOBS": 2
    }
    
    WORK_DIR = "/home/juancho/Documents/GitHub/EmuFaultSim/BenchpyRTLFIv1/Benchmarks/Cores/stereo_vision_core/TestBench"
    #WORK_DIR = "/home/juancho/Documents/GitHub/EmuFaultSim/BenchpyRTLFIv1/Benchmarks/Cores/Adder32/tb"
    run_fault_simulation(WORK_DIR, fi_config)


def split_fault_injection_task(work_dir, fi_config):
    sbtr_config = fi_config.get('project',{}).get('sbtr_config', {})
    sim_config = fi_config.get('project',{}).get('sim_config', {})
    fault_list_name = fi_config.get('project', {}).get('fault_list_name', 'fault_list.csv')
    fault_model = sbtr_config.get('fault_model', 'S@')
    fault_list_name = f"{fault_model}_{fault_list_name}"

    num_jobs = sim_config.get('slurm_jobs', 1)
    work_sim_dir = sim_config.get('work_sim_dir', '')

    #work_dir_clean = os.path.abspath(fi_config.get('project', {}).get('work_dir', ''))
    work_dir_clean = work_dir
    src_work_path_dir = os.path.abspath(os.path.join(work_dir_clean,work_sim_dir))
    #work_dir_rel = work_dir_clean.split("/")[-1]
    work_dir_rel = os.path.abspath(fi_config.get('project', {}).get('root_proj_dir', ''))
    parallel_sims_path = os.path.abspath(work_dir_rel) #os.path.abspath(os.path.join(work_dir_rel,"./"))
    #os.system(f"rm -r {parallel_sims_path}")
    #os.system(f"mkdir -p {parallel_sims_path}")
    # check if multiple jobs are required
    # read the fault list
    fault_list_job = []
    with open(f"{os.path.abspath(src_work_path_dir)}/{fault_list_name}", "r") as f:
        fault_list = f.readlines()
        if len(fault_list) == 0:
            print("No fault list found")
            return
        else:
            fault_list_job = [fault_list[job_id::num_jobs] for job_id in range(num_jobs)]
    
    # create hidden work directories       
    list_work_dir = []
    for job_id in range(num_jobs):
        new_work_dir = os.path.abspath(f"{parallel_sims_path}/.slurm_job{job_id}")
        list_work_dir.append(new_work_dir)
        os.system(f"cp -rf {work_dir_clean} {new_work_dir}")
        new_work_sim_dir = os.path.abspath(os.path.join(new_work_dir, work_sim_dir))
        save_file(f"{os.path.abspath(new_work_sim_dir)}/{fault_list_name}", "w", fault_list_job[job_id])

        timeout=sim_config.get('slurm',{}).get('time',"4:00:00")
        nodes =sim_config.get('slurm',{}).get('nodes',1)
        task_per_node = sim_config.get('slurm',{}).get('tasks_per_node',10)
        mem = sim_config.get('slurm',{}).get('mem',"4G")
        email = sim_config.get('slurm',{}).get('email',"juand.guerrero@polito.it")

        os.system(f"echo 'load --project-dir {work_dir_rel}' > {new_work_dir}/script.s")
        os.system(f"echo 'fsim_exec --work-dir-root {new_work_dir} --slurm-jobid .slurm_job{job_id}' >> {new_work_dir}/script.s")

        slurm_script=sbatch_template.format(TIMEOUT=timeout, 
                               NODES=nodes, 
                               TASK_PER_NODE=task_per_node, 
                               JOB_NAME=f".slurm_job{job_id}",
                               MEM=mem,
                               EMAIL=email,
                               PATH_TO_FILE=new_work_dir
                               )
        os.system(f"echo '{slurm_script}' > {new_work_dir}/sbatch.sh")
        os.system(f"bash {new_work_dir}/sbatch.sh")

        #os.system(f"python shadowfi_shell.py -s {new_work_dir}/script.s")