import logging
import os

from core.shadowfi_core.fault_emulation.fault_emu_fpga import(
    run_fault_emulation,
    run_golden_emulation
)


def fpga_execute(config):
    project_name = config.get('project', {}).get('name', 'unknown')
    logging.info(f'Executing FPGA execute {project_name}')
    # Simulated logic here

    work_dir_root = config.get('project', {}).get('work_dir', '')

    #run_fault_free_simulation(work_dir=work_dir_root, fi_config=config)
    run_golden_emulation(work_dir=work_dir_root, fi_config=config)
    run_fault_emulation(work_dir=work_dir_root, fi_config=config)

    logging.info(' FPGA execution complete.')