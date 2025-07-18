from .utils.settings import settings

from .cli.shadowfi_engine import (
    rtl_elaboration_step,
    target_extraction_and_sbrt_insertion,
    final_sbtr_instantiation,
    fault_list_generation,
    testbench_creation,
    simulation_setup,
    run_simulation,
)


def main():
    config = settings()

    """
    1. RTL ELABORATION
    """
    module_hierarchy, verilog_rtl_elab_code = rtl_elaboration_step(config)

    """
    2. TARGET COMPONENT EXTRACTION AND SABOTEUR INSERTION
    """
    faults_per_module = target_extraction_and_sbrt_insertion(config)

    """
    3. FINAL INSTANTIATION OF THE SBTR MODULES TO MAKE VISIBLE THE I/O SBTR PORTS ON THE TOP MODULE OF THE DESIGN
    """
    fi_infrastructure_system = final_sbtr_instantiation(
        config, module_hierarchy, verilog_rtl_elab_code
    )

    """
    4. FAULT LIST GENERATION
    """
    num_target_components, total_bit_shift = fault_list_generation(
        config, fi_infrastructure_system, faults_per_module
    )
    
    """
    5. TEST BENCH MODIFICATION AND MAKEFILE CREATION
    """
    testbench_creation(config)
    
    """
    6. SIMULATION SETUP
    """
    simulation_setup(config)
    
    """
    7. SIMULATION
    """
    run_simulation(config, num_target_components, total_bit_shift)

    

if __name__ == "__main__":
    main()