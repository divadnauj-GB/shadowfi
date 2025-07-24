# script.s
create --name SFU0 --design-config ./config/SFU0/design_config.yml
load --project-dir ./projects/SFU0
elaborate
pnr
tb_setup --tb-config ./config/SFU0/tb_config.yml
fsim_setup --fsim-config ./config/SFU0/sim_config.yml --run-script ./config/SFU0/run.sh --sdc-check-script ./config/SFU0/sdc_check.sh
fsim_exec
# fi_fpga_setup
# fi_fpga_exec