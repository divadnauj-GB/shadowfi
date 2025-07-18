
import logging

def execute_fault_injection(config):
    project_name = config.get('project', {}).get('name', 'unknown')
    logging.info(f'Executing simulation for project: {project_name}')
    # Simulated logic here
    logging.info('Simulation execution complete.')
