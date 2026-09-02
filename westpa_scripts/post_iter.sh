#!/bin/bash

# Per-iteration housekeeping (executable.post_iteration in west.cfg): tar up
# this iteration's per-segment stdout/stderr logs and remove the loose files.

if [ -n "$SEG_DEBUG" ]; then
    set -x
    env | sort
fi

cd $WEST_SIM_ROOT || exit 1

ITER=$(printf "%06d" $WEST_CURRENT_ITER)
tar -cf seg_logs/$ITER.tar seg_logs/$ITER-*.log
rm  -f  seg_logs/$ITER-*.log
