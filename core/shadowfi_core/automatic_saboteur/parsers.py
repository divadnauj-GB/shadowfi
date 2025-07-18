from .constants import (
    MODULE_PATTERN,
    COMPONENT_PATTERN,
    PORTS_PATTERN,
)
import re

def get_components(verilog_code, config):
    """
    Extracts hierarchical instances of components from Verilog code.
    Returns a list of dicts, each having:
        {
            "top": <top_level_module_name>,
            "components": [
                {
                    "component": <component_module_name>,
                    "module": <instance_name>,
                    "ports": [
                        {
                            "port_name": <name_of_port_in_instance>,
                            "connected_signal": <signal_connected_to_that_port>,
                            "raw_port_definition": <entire_port_definition_string>
                        },
                        ...
                    ]
                },
                ...
            ]
        }
    """
    parsed_components_list = []

    # Search for each module
    for module_match_obj in MODULE_PATTERN.finditer(verilog_code):
        current_module_name = module_match_obj.group(1)
        current_module_content = module_match_obj.group(2)

        components_in_module = []

        # Search for internal components and extract their details
        for component_match_obj in COMPONENT_PATTERN.finditer(current_module_content):
            component_name = component_match_obj.group(1)
            instance_name = component_match_obj.group(2)
            ports_list_str = component_match_obj.group(3)
            ports_list_str_n = re.sub(r"\)\s*,\s*",")@",ports_list_str)

            # Split out individual port connection strings            
            ports = [
                port.strip()
                for port in ports_list_str_n.split("@")
                if port.strip()
            ]

            port_info_list = []
            for port_def in ports:
                for port_match in PORTS_PATTERN.finditer(port_def):
                    raw_port_definition = port_match.group(0)
                    port_name = port_match.group(1)
                    connected_signal = port_match.group(2)
                    port_info_list.append(
                        {
                            "port_name": port_name,
                            "connected_signal": connected_signal,
                            "raw_port_definition": raw_port_definition,
                        }
                    )

            instance_info = {
                "component": component_name,  # e.g., 'adder'
                "module": instance_name,  # e.g., '\genblk1[0].full_adder'
                "ports": port_info_list,
            }

            components_in_module.append(instance_info)

        parsed_components_list.append(
            {"top": current_module_name, "components": components_in_module}
        )

    return parsed_components_list


def get_objects_by_module(parsed_components_list, top_module_name):
    """
    Filters the objects in `parsed_components_list` where 'top' matches `top_module_name`.
    """
    matching_modules_list = [
        obj for obj in parsed_components_list if obj["top"] == top_module_name
    ]    
    return matching_modules_list


def get_hierarchy(parsed_components_list, module_name):
    """
    Recursively constructs the hierarchy for a given module.
    """
    current_module = get_objects_by_module(parsed_components_list, module_name)[0]
    for comp in current_module["components"]:
        comp["dependency"] = get_hierarchy(parsed_components_list, comp["component"])        
    return current_module
