#!/bin/bash
#SBATCH --account=hagan-lab
#SBATCH --partition=hagan-compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --output=slurm_init_%j.out
#
# Submit with: sbatch init.sh
#
# Vars set here (PDB_FILE, N_SUBUNITS, ENATIVE, TOPOLOGY_DIR) are written to
# run_config.sh at the end of this script. env.sh sources run_config.sh if
# present, and run.sh/runwe.slurm both source env.sh -- so a later
# `sbatch run.sh` picks these up automatically with no manual exporting,
# even though it's a separate job on its own node.
#
# To override N_SUBUNITS/seed without an interactive prompt (e.g. for sbatch),
# pass them in: sbatch --export=N_SUBUNITS=336,seed=7 init.sh

module purge

# sbatch runs this in a fresh, non-interactive shell that does NOT
# activate your conda env the way an interactive terminal does -- without
# this, python/lmp/w_init below can silently resolve to the wrong (or no)
# installs. Adjust the conda.sh path if the cluster's miniconda/anaconda
# lives somewhere other than ~/miniconda3.
source ~/miniconda3/etc/profile.d/conda.sh
conda activate westpa2

# Set up simulation environment
source env.sh
mkdir $WEST_SIM_ROOT/west_files

# Sends the segment trajectories to this directory
# Must be an absolute path
OUTPUT_DIR=/scratch0/kylechen/WE_HBV_ENM
mkdir -p $OUTPUT_DIR/traj_segs $OUTPUT_DIR/seg_logs

Enative=1
echo "$Enative"

seed=42
echo "seed: $seed"

N_SUBUNITS=120
echo "N_SUBUNITS: $N_SUBUNITS"

pdb_file=$WEST_SIM_ROOT/init_files/lattice_pdbs/lattice=cubic_Ndimers=120_blength=1258.pdb

# Runs generate lammps
python $WEST_SIM_ROOT/init_files/generate_lammps_data.py --pdb $pdb_file --Enative $Enative
export PDB_FILE="$pdb_file"
# Run lammps_oligomer.in
lmp -in ${WE_HBV_ENM_PATH}/init_files/lammps_oligomer.in   \
    -var output_dir $WEST_SIM_ROOT/bstates \
    -var input_dir $WEST_SIM_ROOT/init_files/lammps_out  \
    -var nsteps 100000         \

topology_dir=$WEST_SIM_ROOT/init_files/lammps_out
# Describe the basis state to WESTPA: seg.restart (written by
# lammps_oligomer.in's write_restart) is what dynamics.in reads via
# read_restart for every new trajectory.
echo "0 1 seg.restart" > $WEST_SIM_ROOT/bstates/bstates.txt

# Target state: fully assembled == every chain in one cluster.
echo "assembled $N_SUBUNITS" > $WEST_SIM_ROOT/tstate.file

rm -rf $WEST_SIM_ROOT/seg_logs
mkdir   $WEST_SIM_ROOT/seg_logs

# Set pointer to bstate and tstate
BSTATE_ARGS="--bstate-file $WEST_SIM_ROOT/bstates/bstates.txt"

# Run w_init
w_init \
  $BSTATE_ARGS \
  --verbose \
  --segs-per-state 5 \
  --work-manager=threads "$@"

# Persist per-run model choice so env.sh (sourced by run.sh, runwe.slurm,
# and westpa_scripts/*) picks it up regardless of what process/node runs
# them -- this is how vars set here reach a later `sbatch run.sh`.
cat > "$WE_HBV_ENM_PATH/run_config.sh" <<EOF
export PDB_FILE="$pdb_file"
export N_SUBUNITS=$N_SUBUNITS
export ENATIVE=$Enative
export TOPOLOGY_DIR="$topology_dir"
export OUTPUT_DIR="$OUTPUT_DIR"
EOF

# rm $init_file_path $WEST_SIM_ROOT/bstates/cluster.dat
