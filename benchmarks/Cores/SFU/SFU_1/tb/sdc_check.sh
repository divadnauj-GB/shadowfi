
touch logs/diff.log 

# diff stdout.txt golden_stdout.txt > logs/stdout_diff.log
# diff stderr.txt golden_stderr.txt > logs/stderr_diff.log

# Application specific output: The following check will be performed only if at least one of diff.log, stdout_diff.log, and stderr_diff.log is different

diff output_sin.csv golden_output_sin.csv > logs/special_check.log
diff output_cos.csv golden_output_cos.csv >> logs/special_check.log
diff output_rsqrt.csv golden_output_rsqrt.csv >> logs/special_check.log
diff output_log2.csv golden_output_log2.csv >> logs/special_check.log
diff output_ex2.csv golden_output_ex2.csv >> logs/special_check.log

cp *.csv *.txt  logs/
#cp tb_Adder32.vcd logs/