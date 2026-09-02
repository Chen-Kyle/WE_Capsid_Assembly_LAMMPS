#!/bin/bash

# HBV Decamer CG Oligomer — WESTPA Basis State Generator
#
# This script runs both:
#         generate_lammps_data.py
#         common_files/make_basis_state.in
#
# Same two-step pattern as HBV_enm/scripts/local_run_lammps.sh, except the
# LAMMPS half only builds a minimized restart (no production run) — this is
# a ONE-TIME setup step per PDB/Enative, not something that runs per WE
# segment. common_files/ is shared read-only input for every walker's
# dynamics.in call (see westpa_scripts/runseg.sh).
#
# generate_lammps_data.py and important_oligomer_pdbs/ are local copies
# (this sim root is self-contained) -- --conndir/--contactdir still default
# into HBV_enm/scripts since ENM bond connectivity and native contact
# definitions are shared, PDB-independent force-field inputs.
#
# This produces, once, in common_files/:
#   decamer.lammps                      atom/bond topology
#   gaussian_native_{A,B,C,D}.table     tabulated Gaussian potentials
#   harmonic_bond_coeffs.lammps         bond_coeff lines for ENM bonds
#   native_contact_pair_coeffs.lammps   pair_coeff lines for native contacts
#
# And in bstates/, the restart WESTPA seeds iteration 1 from:
#   bstate.restart

# conda activate westpa2

WE_SIM_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
common_files="${WE_SIM_ROOT}/common_files"
bstates="${WE_SIM_ROOT}/bstates"

# PDB file (local copy, default matches HBV_enm/scripts/local_run_lammps.sh)
pdb_default="${WE_SIM_ROOT}/important_oligomer_pdbs/abcd_capsid.pdb"
PDB=${1:-${pdb_default}}

# Enative (default value = 1.0)
Enative=${2:-1.0}

# Langevin seed for the minimization/relaxation fix
seed=${3:-42}

# ---------------------------------------------------------------------------
# Generates the shared LAMMPS topology + table files from the PDB
# ---------------------------------------------------------------------------

echo "$(printf '%0.s-' {1..100})"
echo -e "\npython ${WE_SIM_ROOT}/generate_lammps_data.py --pdb ${PDB} --output_dir ${common_files} --Enative ${Enative}\n"
echo "$(printf '%0.s-' {1..100})"

python ${WE_SIM_ROOT}/generate_lammps_data.py \
    --pdb        "${PDB}"          \
    --output_dir "${common_files}" \
    --Enative    "${Enative}"      \

# ---------------------------------------------------------------------------
# Minimizes the starting structure and writes the basis-state restart
# ---------------------------------------------------------------------------

echo -e "Finished running generate_lammps_data.py\n"
echo "$(printf '%0.s-' {1..100})"
echo -e "\nlmp -in ${common_files}/make_basis_state.in -var topology_dir ${common_files} -var bstate_dir ${bstates} -var myseed ${seed}\n"
echo "$(printf '%0.s-' {1..100})"

time lmp -in ${common_files}/make_basis_state.in \
    -var topology_dir "${common_files}" \
    -var bstate_dir   "${bstates}"      \
    -var myseed       "${seed}"         \

echo -e "\nBasis state ready: ${bstates}/bstate.restart\n"
