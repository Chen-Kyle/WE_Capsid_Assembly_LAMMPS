#!/bin/bash

# YOU NEED TO SOURCE THIS source init.sh FOR THE ENVIRONMENTAL VARIABLES TO WORK     

# Set up simulation environment
source env.sh
mkdir $WEST_SIM_ROOT/west_files

# Binding Energy Strength
read -p "Enative: [1]" Enative
Enative=${Enative:-"1"}
echo "$Enative"
export ENATIVE=$Enative

read -p "Seed: [42]" seed
seed=${seed:-"42"}
echo "$seed"

pdb_file=$WEST_SIM_ROOT/init_files/important_oligomer_pdbs/pentamer_box.pdb

export PDB_FILE=$pdb_file

# Runs generate lammps
python $WEST_SIM_ROOT/init_files/generate_lammps_data.py --pdb $PDB_FILE --Enative $Enative

# Run lammps_oligomer.in
lmp -in ${WE_HBV_ENM_PATH}/init_files/lammps_oligomer.in   \
    -var output_dir $WEST_SIM_ROOT/bstates \
    -var input_dir $WEST_SIM_ROOT/init_files/lammps_out  \
    -var nsteps 10000         \

topology_dir=$WEST_SIM_ROOT/init_files/lammps_out
export TOPOLOGY_DIR=$topology_dir
# Describe the basis state to WESTPA: seg.restart (written by
# lammps_oligomer.in's write_restart) is what dynamics.in reads via
# read_restart for every new trajectory.
echo "0 1 seg.restart" > $WEST_SIM_ROOT/bstates/bstates.txt

# Target state: fully assembled == every chain in one cluster.
echo "assembled $N_CHAINS" > $WEST_SIM_ROOT/tstate.file

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

# rm $init_file_path $WEST_SIM_ROOT/bstates/cluster.dat
