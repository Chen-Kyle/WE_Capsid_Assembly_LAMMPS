#!/bin/bash

# Per-iteration housekeeping (executable.post_iteration in west.cfg): tar up
# this iteration's per-segment stdout/stderr logs and remove the loose files.

if [ -n "$SEG_DEBUG" ]; then
    set -x
    env | sort
fi

cd "$WEST_SIM_ROOT" || exit 1

if [[ -z "${OUTPUT_DIR:-}" || -z "${WEST_CURRENT_ITER:-}" ]]; then
    echo "OUTPUT_DIR and WEST_CURRENT_ITER must be set" >&2
    exit 1
fi

ITER=$(printf "%06d" "$WEST_CURRENT_ITER")
LOG_DIR="$OUTPUT_DIR/seg_logs"
shopt -s nullglob
LOG_FILES=("$LOG_DIR/$ITER-"*.log)

if ((${#LOG_FILES[@]} == 0)); then
    echo "No segment logs found for iteration $ITER in $LOG_DIR" >&2
    exit 1
fi

tar -cf "seg_logs/$ITER.tar" -C "$LOG_DIR" -- "${LOG_FILES[@]##*/}" || exit $?
rm -f -- "${LOG_FILES[@]}"
