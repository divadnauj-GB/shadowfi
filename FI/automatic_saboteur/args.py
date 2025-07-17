import configparser


def get_config():
    config = configparser.ConfigParser()
    config.read("settings.ini")

    path = config["Settings"]["path"]
    hierarchical_component_str = config["Settings"]["hierarchical_component"]
    verilog_file = config["Settings"]["verilog"]
    verilog_file_output = config["Settings"]["verilog_output"]
    saboteur = str(config["Settings"]["saboteur"])
    top_module = config["Settings"]["top_module"]
    regex = config["Settings"].get("regex", None)

    hierarchical_components = []
    for component in hierarchical_component_str.split(" "):
        parts = component.split("->")
        if len(parts) == 2:
            hierarchical_components.append(
                {"components_to_update": parts[0].split("@"), "for": parts[1]}
            )

    return {
        "path": path,
        "hierarchical_component": hierarchical_components,
        "verilog_file": verilog_file,
        "verilog_file_output": verilog_file_output,
        "top_module": top_module,
        "regex": regex,
        "saboteur": saboteur,
    }
