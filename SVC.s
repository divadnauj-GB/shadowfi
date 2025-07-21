# script.s
create --name SVC --design-config /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/stereo_vision_core/design_config.yml
load --project-dir /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/projects/SVC
elaborate
pnr
tb_setup --tb-config /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/stereo_vision_core/tb_config.yml
fsim_setup --fsim-config /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/stereo_vision_core/sim_config.yml --set-run-scripts --run-script /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/stereo_vision_core/run.sh --sdc-check-script /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/stereo_vision_core/sdc_check.sh
fsim_exec
# fi_fpga_setup
# fi_fpga_exec