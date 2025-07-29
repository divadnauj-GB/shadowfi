import logging
import os

from core.hyperfpga.fault_emu_fpga import(
    run_fault_emulation,
    run_golden_emulation
)


def fpga_execute(config):
    project_name = config.get('project', {}).get('name', 'unknown')
    logging.info(f'Executing FPGA execute {project_name}')
    # Simulated logic here

    work_dir_root = config.get('project', {}).get('work_dir', '')

    #run_fault_free_simulation(work_dir=work_dir_root, fi_config=config)
    golden_results=run_golden_emulation(work_dir=work_dir_root, fi_config=config)
    run_fault_emulation(work_dir=work_dir_root, fi_config=config, golden_data=golden_results)

    logging.info(' FPGA execution complete.')