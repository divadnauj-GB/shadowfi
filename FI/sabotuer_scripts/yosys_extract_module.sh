# Usage script: bash yosys_extract_module.sh -p <src directory> -t <top module> -m <target module> [-gv 1] [-flt 1]
# example: bash yosys_extract_module.sh -p Cores/Adder32 -t Adder32 -m Adder32 

while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "$package - yosys_extract_module.sh"
      echo " Module extraction, synthesis and saboteur insertion"
      echo " Input: <TOP_MODULE>_stage1.v"
      echo " Output: <MODULE>_gate_extracted.v, <MODULE>_sbtr.v"
      echo " "
      echo "$package [options] application [arguments]"
      echo " "
      echo "options:"
      echo "-h, --help                       show brief help"
      echo "-p, --path=SRC_FOLDER            specify the path to the verilog design root"
      echo "-t, --top-module=TOP_MODULE      specify the top entity in the design"
      echo "-m, --module-to-extract=MODULE   specify the component to be extracted"
      echo "-o, --out-dir=OUT_DIR            specify the output directory"
      echo "-gv, --gen-netlist=NETLIST       specify wheter generates the new file as a netlist or verilog statements"
      echo "-flt, --flatten=FLATTEN          flatten the selected design merging all sub components in the hierarchy"
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
    -m)
      shift
      if test $# -gt 0; then
        MODULE=$1
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
    -gv)
      shift
      if test $# -gt 0; then
        NETLIST=$1
      else
        echo "no argument specified"
        exit 1
      fi
      shift
      ;;
    -flt)
      shift
      if test $# -gt 0; then
        FLATTEN=$1
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

if [[ -z "${MODULE}" ]]; then
  MODULE=Adder32
fi

if [[ -z "${OUT_DIR}" ]]; then
  OUT_DIR=${SRC_FOLDER}
fi

BASEDIR="$PWD"

mkdir -p ${OUT_DIR}
cd ${OUT_DIR}

echo "read_verilog ${SRC_FOLDER}/${TOP_MODULE}_stage1.v" >> synth_generated.ys
echo "hierarchy -check -top ${MODULE}" >> synth_generated.ys
echo "proc; opt; memory; opt; fsm; opt" >> synth_generated.ys
if [[ -z "${FLATTEN}" ]]; then
  echo "no flatten"
else
  echo "flatten; opt" >> synth_generated.ys
fi
echo "techmap; opt" >> synth_generated.ys
echo "splitnets" >> synth_generated.ys
echo "opt_clean -purge" >> synth_generated.ys
echo "check" >> synth_generated.ys
echo "clean" >> synth_generated.ys

if [[ -z "${NETLIST}" ]]; then
  echo "write_verilog -noattr -simple-lhs -renameprefix N_U ${OUT_DIR}/${MODULE}_gate_extracted.v" >> synth_generated.ys  
else
  echo "write_verilog -noexpr -noattr -attr2comment -renameprefix N_U ${OUT_DIR}/${MODULE}_gate_extracted.v" >> synth_generated.ys
fi
yosys -s synth_generated.ys
rm synth_generated.ys

#python insert_saboteur.py




