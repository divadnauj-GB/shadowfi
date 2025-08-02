
import logging
import os
from core.shadowfi_core.fault_simulation.fault_sim_main import (
    run_fault_free_simulation,
    run_fault_simulation,
    split_fault_injection_task,
    run_fault_simulation_hpc
)
from utils.constants import prompt_msg


def run_simulation(config):
    """
    7. FAULT INJECTION CAMPIGN:
    This step perform eht fault injection by selecting the target bit to be corrupted inside the circuit. This Fault injection can be paralelized
    """

    sbtr_config = config.get('project',{}).get('sbtr_config', {})
    sim_config = config.get('project',{}).get('sim_config', {})

    FAULT_MODEL = sbtr_config.get('fault_model', 'S@')
    MAX_NUM_INJ = sim_config.get('max_num_faults', -1)
    F_LIST_NAME = config.get('project', {}).get('fault_list_name', 'fault_list.csv')
    F_SIM_REPORT = config.get('project', {}).get('fault_sim_report', 'fsim_report.csv')
    NUM_JOBS = sim_config.get('tasks', 1)    

    work_dir_root = config.get('project', {}).get('work_dir', '')
    work_dir = sim_config.get('work_sim_dir', '')
    WORK_DIR = os.path.abspath(os.path.join(work_dir_root, work_dir))

    num_target_components = int(sim_config.get('num_target_components', 0))
    total_bit_shift = int(sim_config.get('total_bit_shift', 0)) 

    fi_config = {
        "FAULT_LIST_NAME": f"{FAULT_MODEL}_{F_LIST_NAME}",
        "FAULT_MODEL": f"{FAULT_MODEL}",
        "F_SIM_REPORT": f"{F_SIM_REPORT}",
        "MAX_NUM_INJ": MAX_NUM_INJ,
        "NUM_TARGET_COMPONENTS": num_target_components,
        "TOTAL_BIT_SHIFT": total_bit_shift,
        "JOBS": NUM_JOBS,
    }

    run_fault_free_simulation(WORK_DIR=WORK_DIR, fi_config=fi_config)

    run_fault_simulation(WORK_DIR=WORK_DIR, fi_config=fi_config)



def execute_fault_injection(config,args={}):
    project_name = config.get('project', {}).get('name', 'unknown')
    logging.info(prompt_msg.format(msg=f'Executing simulation for project: {project_name}'))
    # Simulated logic here
    sim_config = config.get('project',{}).get('sim_config', {})

    work_dir_root = config.get('project', {}).get('work_dir', '')

    #run_fault_free_simulation(work_dir=work_dir_root, fi_config=config)

    if not args.hpc:
        """
        print(args.work_dir_root)
        if args.work_dir_root:
            work_dir_root = args.work_dir_root
            run_fault_simulation(work_dir=work_dir_root, fi_config=config, slurm_jobid=args.slurm_jobid)
        else:
            work_dir_root = config.get('project', {}).get('work_dir', '')
            run_fault_free_simulation(work_dir=work_dir_root, fi_config=config)
            run_fault_simulation(work_dir=work_dir_root, fi_config=config)
        """
        run_fault_free_simulation(work_dir=work_dir_root, fi_config=config)
        run_fault_simulation(work_dir=work_dir_root, fi_config=config)
    else:
        run_fault_free_simulation(work_dir=work_dir_root, fi_config=config)
        run_fault_simulation_hpc(work_dir=work_dir_root, fi_config=config)

    logging.info(prompt_msg.format(msg='Simulation execution complete.'))


