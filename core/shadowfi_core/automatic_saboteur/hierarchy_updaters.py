import copy


def identify_modified_components(module_hierarchy, updates_list):
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
                        "target_module": comp.get("target_module"),
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

    def remove_empty_children_and_null_target(data):
        """
        Recursively removes items where 'children' is an empty array and 'target_module' is null.
        """
        filtered_data = []

        for item in data:
            # Recursively clean children
            item["children"] = remove_empty_children_and_null_target(item["children"])

            # Condition to keep the item:
            # - If 'target_module' is NOT null OR 'children' is NOT empty
            if item["target_module"] is not None or item["children"]:
                filtered_data.append(item)

        return filtered_data

    # Assign an index to each updated component
    def add_index_recursively(components_list):
        for idx, comp in enumerate(components_list):
            if len(comp["children"]) == 0:
                comp["index"] = idx
                continue
            comp["index"] = idx
            add_index_recursively(comp["children"])

    components_to_update_list = remove_empty_children_and_null_target(
        components_to_update_list
    )
    add_index_recursively(components_to_update_list)

    return components_to_update_list
