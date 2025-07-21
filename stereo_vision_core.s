# script.s
#create --name stereo_vision_core --design-config /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/stereo_vision_core/stereo_vision_core_design_config.yml
load --project-dir /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/projects/stereo_vision_core
#elaborate
#pnr
#b_setup --tb-config /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/stereo_vision_core/stereo_vision_core_tb_config.yml
#fsim_setup --fsim-config /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/stereo_vision_core/stereo_vision_core_sim_config.yml --run-script /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/stereo_vision_core/run.sh --sdc-check-script /home/juancho/Documents/GitHub/EmuFaultSim/shadowfi/config/stereo_vision_core/sdc_check.sh
fsim_exec
# fi_fpga_setup
# fi_fpga_exec