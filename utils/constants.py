create_help_str = """
############################################################################################
Help for create comand
Create a shadowfi project
Syntax: create --name <name-project> [--project-dir <path> ] [--design-config <config-file>]
--name: Defines the name of the project
--project-dir: Specifies the absolute path of the project: default: <shadowfi-root>/projects
--design-config: Specifies a yaml file with the project configuration. For more details 
                 regarding the configuration parameters, please refer to the documentation.
Examples:  create --name Projectv1
           create --name Projectv1 --project-dir /home/user/projects
           create --name Projectv1 --design-config /home/user/config/proj_config.yml"
############################################################################################                
"""


load_help_str = """
############################################################################################
Help for load comand
Loads a shadowfi project
Syntax: load --project-dir <path-to-project> 
--project-dir: Specifies the absolute path of the project
Examples:  load --project-dir /home/user/projects/Projectv1
############################################################################################              
"""

elaborate_help_str = """
############################################################################################
Help for elaborate comand
Reads the HDL design and transforms it into a Hierarchical RTL netlist
Syntax: elaboarate 
Examples:  elaborate 
############################################################################################                
"""


pnr_help_str = """
############################################################################################
Help for pnr comand
Places and routes the saboteur circuits in the desgn
Syntax: pnr [--cmp-sel <opt> --user-cmp-sel <config yaml file> --max-sel-cmp <num> ] 
            [--fault-model <opt>] [--fault-sampling <opt>]
--cmp-sel: Indicates the insertion mode of saboteurs: opts = [random, top, hierarchy]; default=random
         random: random selection of components across the design hierarchy
         --max-sel-cmp: Maximum number of intrumented components, default: 4
         top: fatten the complete design and select the top component as fault insertion target
         hierarchy: explicit component selection provided by the user
         --user-cmp-sel: A yaml file containing the selected target components for fault instrumentation
--fault-model: Indicates the fault model. opts = [S@, SET, SEU, MEU], default: S@
         S@: stuck-at fault model
         SET: Single Event Transient
         SEU: Single Event Upset
         MEU: Multibit Even Upsets
--fault-sampling: Indicates the fault insertion sampling. opts=[Full, Statistical]
         Full: inserts saboteurs in all nets of selected components
         Statistical: inserts saboteurs on a subset of nets using statitical samplig
Examples:  pnr 
           pnr --cmp-sel random
           pnr --fault-model SEU 
           pnr --fault-sampling Statistical 
############################################################################################                
"""

tb_setup_help_str = """
############################################################################################
Help for tb_setup comand
Testebench configuration and compile. This command can be used when the CUT is instantiated
directly on the top testbench designs. For more complex design and simulation structures 
please refer to the documentation.
Syntax: tb_setup [--tb-config <config-file>| --kwargs <key1=val key2=val ..>]
--tb-config: configuration file in yaml format, please refer to the documentation to obtain
             further information regarding the condifuration details.
--kwargs: custom configuration values in the form key:val, it support nested key-value pairs, 
          e.g. a.b.c=val
Examples:  tb_setup --tb-config <path-to-tb-config-file.yaml>
           tb_setup --kwargs testbench_config.external_tb_build=True 
############################################################################################                
"""

fsim_setup_help_str = """
############################################################################################
Help for fsim_setup comand
Configures the simulation parameters. Be sure the simulation has been properly compiled and
there is a valid verilator executable. 
Syntax: fsim_setup [--fsim-config <config-file> | --kwargs <key1=val key2=val ..>] 
                   [--noset-run-scripts] [--run-script <path-to-run.sh>]
                   [--sdc-check-script <path-to-sdc-check.sh>]
--fsim-config: configuration file in yaml format, please refer to the documentation to obtain
             further information regarding the condifuration details.
--kwargs: custom configuration values in the form key:val, it support nested key-value pairs, 
          e.g. a.b.c=val
--noset-run-scripts: This flag enables or disables the run scripts configuration, when used 
                    the user must manually copy the scripts to the project. For more details please 
                    refer to the documentation
--run-script: run.sh script to be added to the project
--sdc-check-script: sdc-check.sh script to be added to the project
Examples:  fsim_setup --fsim-config <config-file>
           fsim_setup --kwargs sim_config.jobs=10 sim_config.sim_runtime=2000 --noset-run-scripts
           fsim_setup --fsim-config <config-file>  --run-script <path-to-run.sh>
                      --sdc-check-script <path-to-sdc-check.sh>
############################################################################################                
"""

fsim_exec_help_str = """
############################################################################################
Help for fsim_exec comand
launch a fault injection campaing 
Syntax: fsim_exec 
Examples:  fsim_exec 
############################################################################################                
"""