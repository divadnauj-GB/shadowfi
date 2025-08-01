import re
from .constants import (
    MODULE_TEMPLATE,
    SABOTEOUR_MODULE_PORTS_TEMPLATE,
    SABOTEOUR_MODULE_PORTS_DEFINITION_TEMPLATE,
    SABOTEOUR_MODULE_ADD_PORTS_TEMPLATE,
    UPDATE_TOP_MODULE,
    COMPONENT_PATTERN,
    SBTR_SI_NAME,
    SBTR_CNTRL_NAME,
    SBTR_SO_NAME,
)


def extract_original_components(verilog_code, components_list):
    """
    Generates the new modules with sabotage ports added (for internal submodules).
    """

    def update_module(original_module_name, renamed_module_name, bus_width=0):
        """
        Given a module name in the code, rename and add sabotage ports.
        """
        module_search_pattern = re.compile(
            r"module\s"
            + re.escape(original_module_name)
            + r"\s*\((.*?)\)\s*;([\s\S]*?)endmodule",
            re.S,
        )

        for module_match_obj in module_search_pattern.finditer(verilog_code):
            found_module_ports = module_match_obj.group(1)
            found_module_body = module_match_obj.group(2)

            updated_module_str = MODULE_TEMPLATE.format(
                module_name=renamed_module_name,
                module_ports=f"{found_module_ports}{SABOTEOUR_MODULE_PORTS_TEMPLATE}",
                module_implementation="{saboteur}{implementation}".format(
                    saboteur=SABOTEOUR_MODULE_PORTS_DEFINITION_TEMPLATE.format(
                        saboteur_input_bits=(
                            f"[{bus_width-1}:0]" if bus_width > 1 else ""
                        )
                    ),
                    implementation=found_module_body,
                ),
            )
            return updated_module_str

    updated_module_list = []

    def update_content(child_component, module_body, idx, num_children):
        """
        For each child, rename the instance ports, hooking them up to sabotage signals.
        """
        child_module_name = child_component["module"]
        child_instance_name = child_component["instance"]
        renamed_module = child_component["target_module"]
        child_module_index = child_component["index_c"]

        def _replace_instance(match_obj):
            ports_str = match_obj.group(3)
            # If multiple children, chain SI signals among them; otherwise direct SI->SO
            saboteur_port_out = f"SIwire[{idx}]" if (idx != num_children - 1) else SBTR_SO_NAME
            saboteur_port_in = SBTR_SI_NAME if idx == 0 else f"SIwire[{idx-1}]"

            # If there's only one child, no need for chaining
            if num_children == 1:
                saboteur_port_out = SBTR_SO_NAME

            # If the user specified a new module name (rename), use it; otherwise module_index
            new_module_name = (
                renamed_module
                if renamed_module
                else f"{child_module_name}_{child_module_index}"
            )

            updated_ports = SABOTEOUR_MODULE_ADD_PORTS_TEMPLATE.format(
                saboteur_si=saboteur_port_in, saboteur_so=saboteur_port_out
            )

            return (
                f"{new_module_name} {child_instance_name} ({ports_str}{updated_ports});"
            )

        normalized_child_instance_name = re.escape(child_instance_name)
        instance_search_pattern = re.compile(
            rf"({re.escape(child_module_name)})\s+({normalized_child_instance_name})\s*\((:?\s*((:?\.(?:\w+)\((:?.*?)\))+,?\s*)+)\);",
            re.S,
        )

        updated_module_body = re.sub(
            instance_search_pattern, _replace_instance, module_body
        )
        return updated_module_body

    def update_modules_recursively(component_list):
        """
        Recursively update each component's submodules.
        """
        for comp in component_list:
            module_name = comp["module"]
            child_list = comp["children"]
            module_index = comp["index_c"]

            # Recursively update child submodules
            if len(child_list) > 0:
                update_modules_recursively(child_list)
                # Create a new module definition with sabotage ports
                new_module_body = update_module(
                    module_name, f"{module_name}_{module_index}", len(child_list)
                )
                if not new_module_body:
                    # If the module_name wasn't found in verilog_code, skip
                    continue

                # For each child, embed sabotage port connections
                for i, child in enumerate(child_list):
                    new_module_body = update_content(
                        child, new_module_body, i, len(child_list)
                    )

                updated_module_list.append(new_module_body)

    # Start recursion
    update_modules_recursively(components_list)

    # Combine them all, removing duplicates (dict.fromkeys preserves insertion order)
    combined = "\n".join(list(dict.fromkeys(updated_module_list)))
    return combined


def update_top_module(verilog_code, components_list, top_module_name):
    """
    Inject sabotage wiring into the top module's ports and update instances accordingly.
    """
    top_module_pattern = re.compile(
        r"module\s+("
        + re.escape(top_module_name)
        + r")\s*\((.*?)\)\s*;([\s\S]*?)endmodule",
        re.S,
    )

    num_components = len(components_list)

    def replace_top_module(match_obj):
        top_module_ports = match_obj.group(2)
        top_module_body = match_obj.group(3)

        # Insert sabotage ports into top module definition
        updated_top_module = UPDATE_TOP_MODULE.format(
            top=top_module_name,
            ports=f"{top_module_ports}{SABOTEOUR_MODULE_PORTS_TEMPLATE}",
            description="{saboteur}{implementation}".format(
                saboteur=SABOTEOUR_MODULE_PORTS_DEFINITION_TEMPLATE.format(
                    saboteur_input_bits=(
                        f"[{num_components-1}:0]" if num_components > 1 else ""
                    )
                ),
                implementation=top_module_body,
            ),
        )

        # For each updated component, rename the instance & connect SI->SO accordingly
        for top_idx_inst,comp in enumerate(components_list):
            component_instance = comp["instance"]
            comp_idx = comp["index_c"]
            comp_target = comp["target_module"] if comp.get("target_module") else None

            def update_instance(match_component_obj):
                found_module_name = match_component_obj.group(1)
                found_instance_name = match_component_obj.group(2)
                found_module_ports = match_component_obj.group(3)

                saboteur_port_out = (
                    f"SIwire[{top_idx_inst}]" if (top_idx_inst != num_components - 1) else SBTR_SO_NAME
                )
                saboteur_port_in = SBTR_SI_NAME if top_idx_inst == 0 else f"SIwire[{top_idx_inst-1}]"
                renamed_name = (
                    comp_target if comp_target else f"{found_module_name}_{comp_idx}"
                )

                # Only replace if it matches our known instance
                if found_instance_name == component_instance:
                    replaced_module = f"""
                    {renamed_name} {found_instance_name}  (
                        {found_module_ports}{SABOTEOUR_MODULE_ADD_PORTS_TEMPLATE.format(
                            saboteur_si=saboteur_port_in,
                            saboteur_so=saboteur_port_out
                        )}
                    );"""
                    return replaced_module

                return match_component_obj.group(0)

            updated_top_module = re.sub(
                COMPONENT_PATTERN, update_instance, updated_top_module
            )

        return updated_top_module

    return re.sub(top_module_pattern, replace_top_module, verilog_code)


def sort_by_component_count(component_data_list):
    """
    Sort the list of modules by the number of components (descending).
    """
    return sorted(
        component_data_list, key=lambda x: len(x.get("components", [])), reverse=True
    )


def sbtr_interconnect_sequence(list_of_components,comp_interc_list):
    """
    This function is used to get the sequence of the interconnects in the SBTR.
    """
    root_path = comp_interc_list[-1]["path"]
    base_idx = comp_interc_list[-1]["index"]    
    for comp in list_of_components:
        if len(comp["children"])==0:
            comp_interc_list[-1]["path"] = root_path + comp["instance"]
            comp_interc_list[-1]["module"] = comp["module"]
            comp_interc_list[-1]["index"] = base_idx + comp["index"]
            comp_interc_list.append({"index":base_idx + comp["index"]+1,"path":root_path,"module":""})   
            print(comp_interc_list[-1]["index"])
        else:
            children = comp["children"]
            comp_interc_list[-1]["path"] = comp_interc_list[-1]["path"] + comp["instance"] + "@"
            sbtr_interconnect_sequence(children,comp_interc_list)
            comp_interc_list[-1]["path"] = comp_interc_list[-1]["path"].split('@')[:-2]  # Remove last module
            comp_interc_list[-1]["path"] = '@'.join(comp_interc_list[-1]["path"]) + '@'  # Rebuild the path
            comp_interc_list[-1]["path"] = comp_interc_list[-1]["path"][1:] if comp_interc_list[-1]["path"].startswith('@') else comp_interc_list[-1]["path"]  # Remove leading slash
            
            
def fi_infrastructure_interconnect_sequence(list_of_components):
    """
    This function is used to get the sequence of the interconnects in the FI infrastructure.
    """
    final_list = [{"index":0,"path":"","module":""}]
    sbtr_interconnect_sequence(list_of_components,final_list)
    
    fi_infrastructure_list=[]
    for comp in final_list:
        fi_infrastructure_list.append([comp["index"], comp["path"], comp["module"]])
    return (fi_infrastructure_list[:-1],final_list[:-1])