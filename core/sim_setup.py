
import logging

def setup_fault_injection(config):
    project_name = config.get('project', {}).get('name', 'unknown')
    logging.info(f'Setting up simulation for project: {project_name}')
    # Simulated logic here
    logging.info('Simulation setup complete.')
