#!/bin/bash -l
#SBATCH --job-name=ipcluster
#SBATCH --nodes=16
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task=1
#SBATCH --mail-user=juan.guerrero@polito.it
#SBATCH --mail-type=ALL
#SBATCH --time=04:00:00
#SBATCH --qos=normal
#SBATCH --partition=boost_usr_prod
#SBATCH --account=IscrC_HardNet
#SBATCH --output=ipcluster-log-%J.out
#SBATCH --error=ipcluster-err-%J.out

profile=shadowfi_parsims

while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "$package - run_world.sh"
      echo "$package [options] application [arguments]"
      echo " "
      echo "options:"
      echo "-h, --help                       show brief help"
      echo "-e, --engines=ENGINES           specify the Number of parallel engines for sim"
      echo "-hpc, --hpc=HPC                 HPC configuration"
      echo "-s, --stop=STOP                 Stop cluster "
      exit 0
      ;;
    -e)
      shift
      if test $# -gt 0; then
        ENGINES=$1
      else
        echo "no argument specified"
        exit 1
      fi
      shift
      ;;
    -s)
      STOP="1"
      shift
      ;;
    -hpc)
      HPC=$1
      shift
      ;;
    *)
      break
      ;;
  esac
done

if [[ -z "${ENGINES}" ]]; then
  ENGINES=1
fi

if [[ -z "${STOP}" ]]; then
  STOP="0"
fi

if [[ -n "${HPC}" ]]; then
    echo "creating profile: ${profile}"
    singularity exec shadowfi_v1.sif ipython profile create  ${profile}
    echo "Launching controller"
    singularity exec shadowfi_v1.sif  ipcontroller --ip="*" --profile=${profile} &
    sleep 10
    echo "Launching engines"
    srun singularity exec shadowfi_v1.sif ipengine --profile=${profile} --location=$(hostname) 
else
    if [[ "$STOP" = "1" ]]; then 
        echo "Stop ipcluster ${profile}"
        singularity exec shadowfi_v1.sif  ipcluster stop --profile=${profile} &
    else
        echo "creating profile: ${profile}"
        singularity exec shadowfi_v1.sif ipython profile create  ${profile}
        echo "Launching cluster"
        singularity exec shadowfi_v1.sif  ipcluster start -n=${ENGINES} --profile=${profile} &
    fi
fi
#sleep 60

#singularity run shadowfi_v1.sif -s TCU.s > stdout.txt 2> stderr.txt



