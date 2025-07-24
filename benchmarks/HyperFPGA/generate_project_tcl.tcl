open_project ./basic_test-3be11_prj/basic_test-3be11_prj.xpr
write_project_tcl -origin_dir_override ./ -paths_relative_to ./ -all_properties -force recreate_project.tcl
close_project
exit