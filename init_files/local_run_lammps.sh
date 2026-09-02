#!/bin/bash

# HBV Decamer CG Oligomer Simulation
#
# This script runs both:
#         generate_lammps_data.py
#         lammps_oligomer.in
# Number of seeds passed as first argument (default 5)
nseed=1

PDB="${WE_HBV_ENM_PATH}/init_files/important_oligomer_pdbs/abcd_capsid.pdb"
output_dir="${WE_HBV_ENM_PATH}/bstates/main_bstate"
Enative=1
nsteps=1000
#nsteps=100000000

# ---------------------------------------------------------------------------
# Main loop: for each Enative, run nseed independent simulations
# ---------------------------------------------------------------------------

# Generates the LAMMPS files
echo "$(printf '%0.s-' {1..100})"
echo -e "\npython generate_lammps_data.py --pdb ${PDB} --output_dir ${output_dir} --Enative ${Enative}\n"
echo "$(printf '%0.s-' {1..100})"
python ${WE_HBV_ENM_PATH}/init_files/generate_lammps_data.py  \
    --pdb        "${PDB}"       \
    --output_dir "${output_dir}"\
    --Enative    "${Enative}"   \

# Runs the LAMMPS simulation
echo -e "Finished running generate_lammps_data.py\n"
echo "$(printf '%0.s-' {1..100})"
echo -e "\nmpirun -n 1 lmp -in lammps_oligomer.in -var output_dir ${output_dir} -var nsteps ${nsteps}\n"
echo "$(printf '%0.s-' {1..100})"
time lmp -in ${WE_HBV_ENM_PATH}/init_files/lammps_oligomer.in   \
    -var output_dir ${output_dir} \
    -var input_dir ${output_dir}  \
    -var nsteps ${nsteps}         \

echo -e "Running full_traj_analysis.py"
echo -e "python full_traj_analysis.py --pdb ${PDB} --traj ${output_dir}/seg.dcd"
python ${WE_HBV_ENM_PATH}/common_files/full_traj_analysis.py --pdb ${PDB} --traj ${output_dir}/seg.dcd
echo "All runs complete."
