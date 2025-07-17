import json
from .args import get_config

# Parsing functions
from .parsers import get_components, get_hierarchy

# Hierarchy update functions
from .hierarchy_updaters import identify_modified_components, get_components_to_copy

# Sabotage injector functions
from .sabotage_injectors import extract_original_components, update_top_module


def main():
    config = get_config()

    # Read original Verilog
    with open(config["verilog_file"], "r") as f:
        verilog_code = f.read()

    # Step 1: Extract components from top-level code
    parsed_components_list = get_components(verilog_code, config)

    # Step 2: Extract hierarchy for the top module
    module_hierarchy = get_hierarchy(parsed_components_list, config["top_module"])

    # Step 3: Save hierarchy to JSON
    with open("hierarchy.json", "w") as f:
        json.dump(module_hierarchy, f, indent=4)
    print("Hierarchy saved to hierarchy.json")

    # Step 4: Identify which components need updating
    updated_hierarchy = identify_modified_components(
        module_hierarchy, config["hierarchical_component"]
    )

    # Step 5: Save updated components hierarchy to JSON
    with open("updated.json", "w") as f:
        json.dump(updated_hierarchy, f, indent=4)
    print("Updated components saved to updated.json")

    # Step 6: Get the flattened list of updated components (with children)
    updated_component_list = get_components_to_copy(updated_hierarchy)

    with open("components.json", "w") as f:
        json.dump(updated_component_list, f, indent=4)
    print("Updated component list saved to components.json")

    # Step 7: Create sabotage-augmented copies of original modules that need updating
    augmented_modules = extract_original_components(
        verilog_code, updated_component_list
    )
    # Append the new module definitions at the end of the file
    verilog_code += f"\n{augmented_modules}"

    # Step 8: Update the top module definition to wire the sabotage signals
    verilog_code = update_top_module(
        verilog_code, updated_component_list, config["top_module"]
    )

    # Finally, write the modified Verilog back out
    with open(config["verilog_file_output"], "w+") as f:
        f.writelines(verilog_code)

    print("Saved updated Verilog.")


if __name__ == "__main__":
    main()
