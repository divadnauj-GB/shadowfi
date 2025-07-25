# script.s
create --name SVC --design-config ./config/SVC/design_config.yml
load --project-dir ./projects/SVC
elaborate
pnr --cmp-sel hierarchy --user-cmp-sel ./config/SVC/target_modules_3k.yml
tb_setup --tb-config ./config/SVC/tb_config.yml
fsim_setup --fsim-config ./config/SVC/sim_config.yml --run-script ./config/SVC/run.sh --sdc-check-script ./config/SVC/sdc_check.sh
fsim_exec
# fi_fpga_setup
# fi_fpga_exec