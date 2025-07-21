# script.s
create --name TCU --design-config /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/TCU/design_config.yml
load --project-dir /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/projects/TCU
elaborate
pnr
tb_setup --tb-config /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/TCU/tb_config.yml
fsim_setup --fsim-config /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/TCU/sim_config.yml --set-run-scripts --run-script /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/TCU/run.sh --sdc-check-script /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/TCU/sdc_check.sh
fsim_exec
# fi_fpga_setup
# fi_fpga_exec