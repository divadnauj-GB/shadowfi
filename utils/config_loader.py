
import yaml

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def save_config(config, path):
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"Configuration saved to {path}")