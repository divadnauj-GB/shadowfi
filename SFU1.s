# script.s
create --name SFU1 --design-config ./config/SFU1/design_config.yml
load --project-dir ./projects/SFU1
elaborate
pnr --cmp-sel hierarchy --user-cmp-sel ./config/SFU1/target_modules_3k.yml
tb_setup --tb-config ./config/SFU1/tb_config.yml
fsim_setup --fsim-config ./config/SFU1/sim_config.yml  --run-script ./config/SFU1/run.sh --sdc-check-script ./config/SFU1/sdc_check.sh
fsim_exec
# fi_fpga_setup
# fi_fpga_exec