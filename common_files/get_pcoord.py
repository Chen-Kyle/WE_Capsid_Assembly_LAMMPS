import os
import sys
import argparse
import pickle
import subprocess
import warnings
import math
from contextlib import redirect_stdout
warnings.filterwarnings("ignore")
from min_eligible_distance import dimer_partner, min_eligible_distance_and_box_limit_per_frame

# This file is going to take an input trajectory (seg.dcd) file, run
# full_traj_analysis.py on it to build the cluster pickle, and then write a
# combined cluster-size and normalized-distance coordinate for sampled frames.

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
                   help='Number of stride-sampled pcoord values, ending at the final frame '
                        '(one combined coordinate per sampled frame)')
    p.add_argument('--distance_resid',
                   type=int,
                   default=135,
                   help='Residue used for eligible-pair distance (default: 135)')
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
        sys.executable, f'{WE_HBV_ENM_PATH}/common_files/full_traj_analysis.py',
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
    """Return the number of permanent dimers in the largest well-formed cluster.

    Analysis memberships contain chains. AB and CD pairs with matching
    numeric suffixes each represent one dimer. A frame without assembled
    interfaces contains isolated dimers, so its largest cluster has size 1.
    """
    frame_clusters = pkl_data['all_well_formed_clusters'].get(frame)
    if not frame_clusters:
        return 1

    sizes = []
    for cluster in frame_clusters:
        segids = set(cluster['segids'])
        dimers = set()
        for segid in segids:
            partner = dimer_partner(segid)
            if partner not in segids:
                raise ValueError(f'Incomplete dimer in frame {frame}: '
                                 f'{segid} is missing partner {partner}')
            dimers.add(tuple(sorted((segid, partner))))
        sizes.append(len(dimers))
    return max(1, max(sizes))


def sample_frame_indices(n_frames, pcoord_len):
    """Keep existing stride samples, replacing the last with the final frame.

    The number of output values is unchanged. A single requested value
    describes the final frame (also used for the basis-state restart).
    """
    if n_frames < 1 or pcoord_len < 1:
        raise ValueError('n_frames and pcoord_len must both be positive')
    stride = max(n_frames // pcoord_len, 1)
    frames = [min(i * stride, n_frames - 1) for i in range(pcoord_len)]
    frames[-1] = n_frames - 1
    return frames


def get_progress_coordinate(cluster_size, min_distance, box_limit, *, distance_status=None):
    """Combine cluster size and box-normalized minimum-distance progress."""
    if min_distance is None and distance_status in ('fully_connected', 'no_eligible_partner'):
        # No attachment-distance bonus when there is no measurable encounter.
        # A fully connected cluster is not necessarily a closed capsid.
        if distance_status == 'no_eligible_partner':
            print('No eligible partner for the largest cluster; using size alone.', file=sys.stderr)
        return float(cluster_size)
    if (min_distance is None or not math.isfinite(float(min_distance))
            or min_distance < 0):
        raise ValueError(f'minimum eligible distance must be non-negative and finite; got {min_distance}')
    if not math.isfinite(float(box_limit)) or box_limit <= 0:
        raise ValueError(f'box distance limit must be positive and finite; got {box_limit}')

    closeness = max(0.0, min(1.0, 1.0 - min_distance / box_limit))
    return cluster_size + closeness * 0.99


if __name__ == '__main__':
    args = parse_args()
    pkl_path = run_full_traj_analysis(args.pdb, args.traj, args.contactdir, args.contacts)
    pkl_data = load_pickle(pkl_path)

    # Keep helper progress messages out of stdout, which callers use as pcoord data.
    with redirect_stdout(sys.stderr):
        measurements = min_eligible_distance_and_box_limit_per_frame(
            args.pdb, args.traj, args.distance_resid,
            pkl_data['all_well_formed_clusters'], return_details=True)

    n_frames = len(measurements)
    if n_frames == 0:
        raise ValueError('trajectory contains no frames')

    for frame in sample_frame_indices(n_frames, args.pcoord_len):
        cluster_size = get_cluster_size(pkl_data, frame)
        measurement = measurements[frame]
        print(get_progress_coordinate(
            cluster_size, measurement['distance'], measurement['box_limit'],
            distance_status=measurement['status']))
