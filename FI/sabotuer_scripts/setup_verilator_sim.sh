# Usage script: verilator_sim.sh <benchmark path> <top module>
# example: bash verilator_sim.sh Cores/Adder32/ Adder32

OSS_CAD_PATH="/home/EDA_tools/oss-cad-suite"

while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "$package - verilator_sim.sh"
      echo " verilator simulation"
      echo " Requirements: <TOP_MODULE>_FI.v, tb_<TOP_MODULE>_FI.tb"
      echo "$package [options] application [arguments]"
      echo " "
      echo "options:"
      echo "-h, --help                       show brief help"
      echo "-p, --path=SRC_FOLDER            specify the path to the verilog design root"
      echo "-t, --top-module=TOP_MODULE      specify the top entity in the design"
      echo "-o, --out-dir=OUT_DIR            specify the output directory"
      echo "-ps, --sbtr-dir=SBTR_DIR         specify the saboteur cells directory"
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
        TOPMODULE=$1
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
    -ps)
      shift
      if test $# -gt 0; then
        SBTR_CELLS=$1
      else
        echo "no argument specified"
        exit 1
      fi
      shift
      ;; 
    -tbp)
      shift
      if test $# -gt 0; then
        TB_PATH=$1
      else
        echo "no argument specified"
        exit 1
      fi
      shift
      ;;
    -tbt)
      shift
      if test $# -gt 0; then
        TB_TOP=$1
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

BASEDIR="$PWD"

if [[ -z "${SRC_FOLDER}" ]]; then
  SRC_FOLDER=Benchmarks/Cores/Adder32
fi

if [[ -z "${TOPMODULE}" ]]; then
  TOPMODULE=Adder32
fi

if [[ -z "${SBTR_CELLS}" ]]; then
  SBTR_CELLS=FI/sbtr_cells
fi

if [[ -z "${OUT_DIR}" ]]; then
  OUT_DIR=${SRC_FOLDER}
fi

if [[ -z "${TB_PATH}" ]]; then
  TB_PATH=${SRC_FOLDER}
fi

if [[ -z "${TB_TOP}" ]]; then
  TB_TOP=tb_${TOPMODULE}
fi
# tb_file=""
# for verilog_file in $(find ${BASEDIR}/${SRC_FOLDER} -type f -name "tb_*.v" | sort); do
#     tb_file+=" ${verilog_file}"
# done

# insert saboteur controller in test_bench if available
#python ${BASEDIR}/FI/sabotuer_scripts/test_bench_setup.py -f ${tb_file}



cmd=""
for verilog_file in $(find ${SBTR_CELLS} -type f -name "*.v" | sort); do
    cmd+=" ${verilog_file}"
done

for verilog_file in $(find ${SRC_FOLDER} -type f -name "*_sbtr.v" | sort); do
    cmd+=" ${verilog_file}"
done 

for verilog_file in $(find ${TB_PATH} -type f -name "*.v" | sort); do
    cmd+=" ${verilog_file}"
done

echo ${cmd}

verilator -sv -O3 --timescale-override 1ps/1ps --timing -Wno-ASSIGNIN -Wno-PINMISSING --top-module ${TB_TOP}\
 -max-num-width 80000 --threads 4 --binary ${cmd} ${OSS_CAD_PATH}/share/yosys/simcells.v ; #--trace --trace-depth 3
make -C obj_dir -f V${TB_TOP}.mk V${TB_TOP}

#time ${BASEDIR}/${OUT_DIR}/obj_dir/Vtb_${TOPMODULE}

cd -

