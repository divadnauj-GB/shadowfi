# script.s
create --name TCU --design-config ./config/TCU/design_config.yml
load --project-dir ./projects/TCU
elaborate
pnr --cmp-sel hierarchy --user-cmp-sel ./config/TCU/target_modules_3k.yml
tb_setup --tb-config ./config/TCU/tb_config.yml
fsim_setup --fsim-config ./config/TCU/sim_config.yml --run-script ./config/TCU/run.sh --sdc-check-script ./config/TCU/sdc_check.sh
fsim_exec
# fi_fpga_setup
# fi_fpga_exec