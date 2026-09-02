#!/bin/bash

# WE_HBV_enm simulation environment.
# Sourced by init.sh (and friends) to set up path variables. Self-locating
# so it works no matter what directory you're in when you `source init.sh`.

export WE_HBV_ENM_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export WEST_SIM_ROOT="$WE_HBV_ENM_PATH"

# Per-run model choice (PDB_FILE, N_CHAINS) written by init.sh — re-sourced
# here so every westpa_scripts/*.sh subprocess picks it up too, regardless
# of which work-manager/process spawned it.
[ -f "$WE_HBV_ENM_PATH/run_config.sh" ] && source "$WE_HBV_ENM_PATH/run_config.sh"

