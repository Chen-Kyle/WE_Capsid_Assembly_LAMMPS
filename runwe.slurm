#!/bin/bash
#SBATCH --account=hagan-lab
#SBATCH --partition=hagan-compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --output=slurm_%j.out
#
# run.sh
#
# Run the weighted ensemble simulation. Make sure you ran init.sh first!
#

module purge
source env.sh

# WESTPA parallelizes across walkers; avoid nested numerical-library threads.
# Export before w_run imports NumPy so workers and analysis children inherit it.
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1


rm -f west.log
w_run --work-manager processes "$@" &> west-${SLURM_JOB_ID}.log

# ./analysis.sh $SLURM_WESTOUTPUT_COPY >> west.log
