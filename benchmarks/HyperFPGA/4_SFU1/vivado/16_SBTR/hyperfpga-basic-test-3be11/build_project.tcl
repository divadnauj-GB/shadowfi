# Open the Vivado project

open_project ./basic_test-3be11_prj/basic_test-3be11_prj.xpr

# Launch synthesis run
launch_runs synth_1
wait_on_run synth_1

# Launch implementation run and generate bitstream
launch_runs impl_1 -to_step write_bitstream
wait_on_run impl_1

# Optional: Generate reports or perform other actions
#report_timing_summary
#report_utilization

write_hw_platform -fixed -include_bit -force -file FSU1_16_SBTR-3be11.xsa

close_project
exit