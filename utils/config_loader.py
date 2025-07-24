
import yaml
import argparse
import ast

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def save_config(config, path):
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"Configuration saved to {path}")

class KeyValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        def convert_value(val):
            try:
                parsed = ast.literal_eval(val)
                if isinstance(parsed, (list, tuple)):
                    return list(parsed)
                return parsed
            except (ValueError, SyntaxError):
                pass
            # Try comma-separated list: a,b,c
            if ',' in val:
                return [convert_value(v.strip()) for v in val.split(',')]
            if val.lower() == 'true':
                return True
            if val.lower() == 'false':
                return False
            try:
                return int(val)
            except ValueError:
                try:
                    return float(val)
                except ValueError:
                    return val  # fallback to string
                
        def set_nested(d, dotted_key, value):
            keys = dotted_key.split('.')
            for k in keys[:-1]:
                d = d.setdefault(k, {})
            d[keys[-1]] = convert_value(value)

        result = {}
        for value in values:
            try:
                key, val = value.split('=', 1)
                set_nested(result, key, val)
            except ValueError:
                parser.error(f"Argument '{value}' is not in 'key=value' format.")
        setattr(namespace, self.dest, result)