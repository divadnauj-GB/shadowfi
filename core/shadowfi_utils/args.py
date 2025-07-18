import argparse

parser = argparse.ArgumentParser(
    description="Setup the testbench by incorporating the sbtr controller"
)

parser.add_argument(
    "-cfg",
    "--config-file",
    default="bench_config.yml",
    type=str,
    help="Input file with the configuration in yaml format",
)

parser.add_argument(
    "-b",
    "--benchmark",
    default="SFU0",
    type=str,
    help="name of the benchmark as in the bench_config.yml file",
)

parser.add_argument(
    "-m",
    "--target-instances",
    default="Config_files/target_modules_original.yml",
    type=str,
    help="configuration file containing the target modules to be used",
    required=False
)

parser.add_argument(
    "-fm",
    "--fault-model",
    default="S@",
    type=str,
    help="Fault model S@ for stuck-at SET for single envent transcient and and SEU for single event upset",
    required=False
)


parser.add_argument(
    "-nf",
    "--num-faults",
    default=10,
    type=int,
    help="Select the max number of injections",
    required=False
)

parser.add_argument(
    "-j",
    "--num-jobs",
    default=1,
    type=int,
    help="Select the max number of injections",
    required=False
)

parser.add_argument(
    "-os",
    "--only-sim",
    action="store_true",
    help="enable to run the simulation only",
    required=False
)