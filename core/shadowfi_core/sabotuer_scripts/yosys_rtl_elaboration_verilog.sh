# Usage script: bash yosys_rtl_elaboration_verilog.sh -p <src directory> -t <top module> 
# example: bash yosys_rtl_elaboration_verilog.sh -p Cores/Adder32 -t Adder32



while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "$package - yosys_rtl_elaboration_verilog.sh"
      echo " RTL elaboration"
      echo " Input: verilog design files"
      echo " Output: A single RTL file named as <TOP_MODULE>_stage1.v"
      echo " "
      echo "$package [options] application [arguments]"
      echo " "
      echo "options:"
      echo "-h, --help                       show brief help"
      echo "-p, --path=SRC_FOLDER            specify the path to the verilog design root"
      echo "-t, --top-module=TOP_MODULE      specify the top entity in the design"
      echo "-o, --out-dir=OUT_DIR            specify the output directory"
      exit 0
      ;;
    -p)
      shift
      if test $# -gt 0; then
        SRC_FOLDER=$1
      else
        echo "no argument specified"
        exit 1
      fi
      shift
      ;;
    -t)
      shift
      if test $# -gt 0; then
        TOP_MODULE=$1
      else
        echo "no argument specified"
        exit 1
      fi
      shift
      ;;
    -o)
      shift
      if test $# -gt 0; then
        OUT_DIR=$1
      else
        echo "no argument specified"
        exit 1
      fi
      shift
      ;;
    *)
      break
      ;;
  esac
done



if [[ -z "${SRC_FOLDER}" ]]; then
  SRC_FOLDER=Benchmarks/Cores/Adder32
fi

if [[ -z "${TOP_MODULE}" ]]; then
  TOP_MODULE=Adder32
fi

if [[ -z "${OUT_DIR}" ]]; then
  OUT_DIR=${SRC_FOLDER}
fi

mkdir -p ${OUT_DIR}
cd ${OUT_DIR}
# Create a new Yosys script
cat > synth_generated.ys << EOF
# File: synth_generated.ys

# Read all VHDL files with GHDL
EOF

cmd="read_verilog -defer "

for verilog_file in $(find ${SRC_FOLDER} -type f -name "*.v"  | sort); do
    cmd+=" $verilog_file"
done
echo ${cmd} >> synth_generated.ys
echo "hierarchy -check -top $TOP_MODULE" >> synth_generated.ys
echo "proc; opt; memory; opt; fsm; opt" >> synth_generated.ys
echo "opt_clean -purge" >> synth_generated.ys
echo "write_verilog -noattr -simple-lhs -renameprefix rtil_signal ${OUT_DIR}/${TOP_MODULE}_stage1.v" >> synth_generated.ys
echo "exit">> synth_generated.ys

# Elaborate the top-level entity
# echo "ghdl -e $TOP_MODULE" >> synth_generated.ys

# Add synthesis and netlist output commands
cat >> synth_generated.ys << EOF

# Synthesize the top module
# synth -top $TOP_MODULE

# Write the synthesized netlist to a Verilog file
# write_verilog synthesized_netlist.v
EOF

# Run the generated Yosys script
yosys -s synth_generated.ys

# Clean up the generated script if you don't need it afterwards
rm synth_generated.ys

echo "read_verilog ${OUT_DIR}/${TOP_MODULE}_stage1.v" >> synth_generated.ys
echo "proc" >> synth_generated.ys
echo "write_json ${OUT_DIR}/${TOP_MODULE}_stage1.json" >> synth_generated.ys

yosys -s synth_generated.ys
rm synth_generated.ys

