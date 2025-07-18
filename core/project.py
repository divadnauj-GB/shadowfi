
import os
import shutil
import yaml
import logging
from utils.config_loader import load_config,save_config

def create_project(project_name, base_dir='projects', template_config='config/project_config.yaml'):
    project_path = os.path.join(base_dir, project_name)
    os.makedirs(project_path, exist_ok=True)
    os.makedirs(os.path.join(project_path, 'src'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'work'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'logs'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'sbtr'), exist_ok=True)

    config_dst = os.path.join(project_path, 'config.yaml')
    if os.path.exists(template_config):
        shutil.copy(template_config, config_dst)
        logging.info(f'Config copied to {config_dst}')
        project_config = load_config(config_dst)
        project_config['shadowfi_root'] = os.getenv('SHADOWFI_ROOT', os.path.join(os.path.dirname(os.path.abspath(__file__)),"/.."))
        project_config['project']["name"] = project_name
        project_config['project']["root_proj_dir"] = project_path
        project_config['project']["work_dir"] = os.path.join(project_path, 'work')
        project_config['project']["sbtr_config"]["sbtr_dir"] = os.path.join(project_path, 'sbtr')
        project_config['project']["proj_config_file"] = config_dst
        save_config(project_config, config_dst)
        
    else:
        logging.warning(f'Template config not found: {template_config}')
    logging.info(f'Project {project_name} created at {project_path}')



def load_project_config(project_dir):
    config_path = os.path.join(project_dir, 'config.yaml')
    if not os.path.exists(config_path):
        logging.error(f'Config file not found in {project_dir}')
        return None
    return config_path