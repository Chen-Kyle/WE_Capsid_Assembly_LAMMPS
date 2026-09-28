import os
import pandas as pd
import sys
import argparse
import pickle
import subprocess
import warnings
warnings.filterwarnings("ignore")
import MDAnalysis as mda

# This file is going to take an input trajectory (seg.dcd) file, run
# full_traj_analysis.py on it to build the cluster pickle, and then write
# the max cluster size into the pc.dat file for capturing

WE_HBV_ENM_PATH = os.environ.get("WE_HBV_ENM_PATH", "/home/kyle/2026_Research/WE_HBV_enm")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--traj',
                   type=str,
                   help='Path to the trajectory file (seg.dcd)',
                   required=True)
    p.add_argument('--pdb',
                   type=str,
                   default=os.environ.get(
                       "PDB_FILE",
                       f'{WE_HBV_ENM_PATH}/init_files/important_oligomer_pdbs/pentamer_box.pdb'),
                   help='Simulation-start PDB matching traj')
    p.add_argument('--contactdir',
                   type=str,
                   default=f'{WE_HBV_ENM_PATH}/init_files/contact_files',
                   help='Directory containing A_contacts.txt ... D_contacts.txt')
    p.add_argument('--contacts',
                   type=int,
                   default=1,
                   help='The number of contacts to be considered bonded')
    p.add_argument('--pcoord_len',
                   type=int,
                   default=3,
                   help='Number of evenly-sampled pcoord values to report '
                        '(one largest-cluster-size value per sampled frame)')
    return p.parse_args()


def run_full_traj_analysis(pdb, traj, contactdir, contacts):
    """
    Runs full_traj_analysis.py on traj and returns the path to the
    complete_cluster_data.pkl it writes alongside traj
    """
    # full_traj_analysis.py prints its own progress messages to stdout;
    # redirect those to stderr so they don't end up mixed into this
    # script's stdout, which callers (get_pcoord.sh/runseg.sh) redirect
    # straight into WEST_PCOORD_RETURN and parse as floats.
    subprocess.run([
        'python', f'{WE_HBV_ENM_PATH}/common_files/full_traj_analysis.py',
        '--pdb', pdb,
        '--traj', traj,
        '--contactdir', contactdir,
        '--contacts', str(contacts),
    ], check=True, stdout=sys.stderr)

    return traj.replace('seg.dcd', 'complete_cluster_data.pkl')


def load_pickle(path):
    """
    Loads the data from the pickle file
    """
    with open(path, 'rb') as f:
        return pickle.load(f)


def get_cluster_size(pkl_data, frame):
    """
    From the given frame of the pickle file, gets the size of the largest
    cluster. A frame with zero well-formed clusters anywhere in the whole
    trajectory is dropped from the dict entirely by full_traj_analysis.py
    (not stored as an empty list), so a missing key means the same thing
    as an empty list: nothing is bonded yet, i.e. every subunit is its own
    cluster of size 1.
    """
    frame_clusters = pkl_data['all_well_formed_clusters'].get(frame)

    if not frame_clusters:
        return 1

    return max(len(cluster['segids']) for cluster in frame_clusters)


def sample_frame_indices(n_frames, pcoord_len):
    """
    Evenly samples pcoord_len frame indices across [0, n_frames), by
    striding every (n_frames // pcoord_len) frames from frame 0.
    """
    stride = max(n_frames // pcoord_len, 1)
    return [min(i * stride, n_frames - 1) for i in range(pcoord_len)]


if __name__ == '__main__':
    args = parse_args()
    pkl_path = run_full_traj_analysis(args.pdb, args.traj, args.contactdir, args.contacts)
    pkl_data = load_pickle(pkl_path)

    # Read the true frame count directly from the trajectory rather than
    # from all_well_formed_clusters' keys -- that dict has no entry at all
    # for a frame with zero well-formed clusters (see get_cluster_size),
    # so if the whole trajectory is unbonded (e.g. a dissociated basis
    # state) its keys() would be empty even though real frames exist.
    n_frames = len(mda.Universe(args.pdb, args.traj).trajectory)
    for frame in sample_frame_indices(n_frames, args.pcoord_len):
        print(get_cluster_size(pkl_data, frame))