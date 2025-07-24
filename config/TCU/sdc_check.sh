
touch logs/diff.log 

# diff stdout.txt golden_stdout.txt > logs/stdout_diff.log
# diff stderr.txt golden_stderr.txt > logs/stderr_diff.log

# Application specific output: The following check will be performed only if at least one of diff.log, stdout_diff.log, and stderr_diff.log is different

diff output_dot_product.csv golden_output_dot_product.csv > logs/special_check.log

cp stdout.txt stderr.txt output_dot_product.csv logs/
#cp tb_Adder32.vcd logs/