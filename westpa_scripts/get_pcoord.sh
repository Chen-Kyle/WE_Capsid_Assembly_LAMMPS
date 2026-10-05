#!/bin/bash

# Reports the basis state's initial progress coordinate (executable.get_pcoord
# in west.cfg). Runs the same get_pcoord.py pipeline as runseg.sh, against
# the trajectory init.sh's lammps_oligomer.in run already produced at
# bstates/seg.dcd — a real (final-frame) value, not a placeholder.
#
# A basis state is a single point, not a segment: WESTPA requires exactly
# one pcoord value here (shape (1,)) regardless of the simulation's
# pcoord_len -- unlike runseg.sh, which reports pcoord_len values.

source $WEST_SIM_ROOT/env.sh

if [ -n "$SEG_DEBUG" ]; then
    set -x
    env | sort
fi

cd $WEST_SIM_ROOT || exit 1

python $WEST_SIM_ROOT/common_files/get_pcoord.py \
    --traj       $WEST_SIM_ROOT/bstates/seg.dcd \
    --pdb        "$PDB_FILE" \
    --contactdir $WEST_SIM_ROOT/init_files/contact_files \
    --pcoord_len 1 \
    > $WEST_SIM_ROOT/bstates/pc.dat

cat $WEST_SIM_ROOT/bstates/pc.dat > $WEST_PCOORD_RETURN
