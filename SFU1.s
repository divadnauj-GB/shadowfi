# script.s
create --name SFU1 --design-config /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/SFU1/design_config.yml
load --project-dir /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/projects/SFU1
elaborate
pnr
tb_setup --tb-config /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/SFU1/tb_config.yml
fsim_setup --fsim-config /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/SFU1/sim_config.yml --set-run-scripts --run-script /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/SFU1/run.sh --sdc-check-script /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/SFU1/sdc_check.sh
fsim_exec
# fi_fpga_setup
# fi_fpga_exec