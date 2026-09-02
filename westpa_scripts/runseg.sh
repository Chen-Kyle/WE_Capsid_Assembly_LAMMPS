#!/bin/bash

# Per-segment WE propagator. Invoked by WESTPA once per walker per
# iteration (executable.propagator in west.cfg). Runs a chunk of LAMMPS
# Langevin dynamics from the parent restart (dynamics.in), then extracts
# the largest well-formed-cluster-size progress coordinate from the
# resulting trajectory (get_pcoord.py).

source $WEST_SIM_ROOT/env.sh

if [ -n "$SEG_DEBUG" ]; then
    set -x
    env | sort
fi

cd $WEST_SIM_ROOT
mkdir -pv $WEST_CURRENT_SEG_DATA_REF
cd $WEST_CURRENT_SEG_DATA_REF

if [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_CONTINUES" ]; then
    ln -sv $WEST_PARENT_DATA_REF/seg.restart ./parent.restart
elif [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_NEWTRAJ" ]; then
    ln -sv $WEST_PARENT_DATA_REF ./parent.restart
fi

myseed=$(( (RANDOM % 100000) + 1 ))

lmp -in $WEST_SIM_ROOT/common_files/dynamics.in \
    -var topology_dir   $WEST_SIM_ROOT/init_files/lammps_out \
    -var parent_restart ./parent.restart \
    -var nsteps         10000 \
    -var dump_freq      1000 \
    -var myseed         $myseed

python $WEST_SIM_ROOT/common_files/get_pcoord.py \
    --traj       ./seg.dcd \
    --pdb        "$PDB_FILE" \
    --contactdir $WEST_SIM_ROOT/init_files/contact_files \
    --pcoord_len 3 \
    > pc.dat

cat pc.dat > $WEST_PCOORD_RETURN
echo "Is this working?

rm -f parent.restart
