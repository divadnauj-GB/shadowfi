import copy
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


def identify_modified_components(module_hierarchy, updates_list, top_module_name):
    """
    Marks and updates components in the hierarchy that need to be modified.
    """

    def recursive_update(components_list, instance_names, target_component_name):
        updated_components_list = []

        for comp in components_list:
            new_comp = copy.deepcopy(comp)

            # If the first instance matches this component
            if instance_names and new_comp["module"] == instance_names[0]:
                new_comp["update"] = True

                # If it's the last item in instance_names, apply the 'target_module'
                if len(instance_names) == 1:
                    new_comp["target_module"] = target_component_name

                # If there's a deeper dependency, recurse
                if new_comp.get("dependency"):
                    new_dependency_copy = copy.deepcopy(
                        new_comp["dependency"]["components"]
                    )
                    instance_names.pop(0)
                    new_comp["dependency"]["components"] = recursive_update(
                        new_dependency_copy,
                        instance_names,
                        target_component_name,
                    )

            # Mark if the entire component is the target
            if new_comp["module"] == target_component_name:
                new_comp["update"] = True

            updated_components_list.append(new_comp)

        return updated_components_list

    # Copy the top module
    top_module_copy = copy.deepcopy(module_hierarchy)
    top_module_copy["update"] = True

    # Apply each update rule
    for update_rule in updates_list:
        components_to_update = update_rule["components_to_update"]
        target_component = update_rule["for"]  # from config
        top_module_copy["components"] = recursive_update(
            top_module_copy["components"], components_to_update, target_component
        )

    return top_module_copy


def get_components_to_copy(module_data):
    """
    Retrieves only the updated components (recursively) from `module_data`.
    """
    components_to_update_list = []

    def find_updated_components_recursively(components_list):
        for comp in components_list:
            if comp.get("update"):
                # Keep top-level updated components
                components_to_update_list.append(
                    {
                        "component": comp["component"],
                        "module": comp["module"],
                        "dependency": comp["dependency"],
                    }
                )

    find_updated_components_recursively(module_data["components"])

    def get_unique_children_recursively(components_list):
        unique_children_list = []
        if len(components_list) == 0:
            return unique_children_list

        for comp in components_list:
            child_item = {
                "module": comp["component"],
                "instance": comp["module"],
                "children": [],
                "target_module": comp.get("target_module"),
            }
            if comp.get("dependency"):
                for dep in comp["dependency"]["components"]:
                    if dep.get("update"):
                        children = []
                        target_module_name = None
                        if dep.get("dependency"):
                            children = get_unique_children_recursively(
                                dep["dependency"]["components"]
                            )
                        if dep.get("target_module"):
                            target_module_name = dep["target_module"]
                            # If a node itself is renamed, do not expand deeper
                            children = []
                        child_item["children"].append(
                            {
                                "module": dep["component"],
                                "instance": dep["module"],
                                "target_module": target_module_name,
                                "children": children,
                            }
                        )

            unique_children_list.append(child_item)
        return unique_children_list

    components_to_update_list = get_unique_children_recursively(
        components_to_update_list
    )

    # Assign an index to each updated component
    def add_index_recursively(components_list):
        for idx, comp in enumerate(components_list):
            if len(comp["children"]) == 0:
                comp["index"] = 0
                continue
            comp["index"] = idx
            add_index_recursively(comp["children"])

    add_index_recursively(components_to_update_list)

    return components_to_update_list


def extract_original_components(verilog_code, components_list, top_module_name):
    """
    Generates the new modules with sabotage ports added (for internal submodules).
    """

    def update_module(original_module_name, renamed_module_name, bus_width=0):
        """
        Given a module name in the code, rename and add sabotage ports.
        """
        module_search_pattern = re.compile(
            r"module\s" + original_module_name + r"\s*\((.*?)\)\s*;([\s\S]*?)endmodule",
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
        child_module_index = child_component["index"]

        def _replace_instance(match_obj):
            ports_str = match_obj.group(3)
            # If multiple children, chain SI signals among them; otherwise direct SI->SO
            saboteur_port_out = f"SIwire[{idx}]" if (idx != num_children - 1) else SBTR_SO_NAME
            saboteur_port_in = SBTR_SI_NAME if idx == 0 else f"SIwire[{idx-1}]"

            # If there's only one child, it doesn't need chaining
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
                f"{new_module_name} {child_instance_name}({ports_str}{updated_ports});"
            )

        instance_search_pattern = re.compile(
            rf"({child_module_name})\s+({child_instance_name})\s*\(\s*((?:\.\w+\(\w+(?:\[\d+\])?\),?\s*)+)\s*\);",
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
            module_index = comp["index"]

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
        r"module\s+(" + top_module_name + r")\s*\((.*?)\)\s*;([\s\S]*?)endmodule", re.S
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
        for comp in components_list:
            component_instance = comp["instance"]
            comp_idx = comp["index"]

            def update_instance(match_component_obj):
                found_module_name = match_component_obj.group(1)
                found_instance_name = match_component_obj.group(2)
                found_module_ports = match_component_obj.group(3)

                saboteur_port_out = (
                    f"SIwire[{comp_idx}]" if (comp_idx != num_components - 1) else SBTR_SO_NAME
                )
                saboteur_port_in = SBTR_SI_NAME if comp_idx == 0 else f"SIwire[{comp_idx-1}]"

                # Only replace if it matches our known instance
                if found_instance_name == component_instance:
                    replaced_module = f"""
                    {found_module_name}_{comp_idx} {found_instance_name}  (
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
