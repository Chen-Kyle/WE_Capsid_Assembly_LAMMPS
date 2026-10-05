"""
min_eligible_distance.py
For each frame of a trajectory, finds the shortest distance between a given
residue on any two subunits that are eligible to bond with each other, and
writes one value per frame to a text file.

Eligible bonding pairs (by chain type letter, e.g. 'A1' and 'A2' are both
chain type 'A'):
    A - A
    B - C, B - D
    C - B, C - D
    D - B, D - C

Input arguments:
    path_to_pdb_file             -- atom positions + bond topology
    path_to_trajectory_file      -- trajectory data
    resid                        -- residue number to measure (same on both chains)
    output_directory_path        -- output directory

Output
    A text file (min_eligible_distance.txt by default) with one line per
    frame: "{frame} {distance}", where distance is the minimum, over all
    eligible inter-cluster pairs involving a largest cluster, of the resid-resid
    distance (minimum-image convention applied).
"""

import argparse
import sys
from contextlib import redirect_stdout
import os
import numpy as np
import MDAnalysis as mda
from itertools import combinations

import warnings
warnings.filterwarnings("ignore")

WE_HBV_ENM_PATH = os.environ.get("WE_HBV_ENM_PATH", "/home/kyle/2026_Research/WE_HBV_enm")

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--pdb',        default=os.environ.get(
                       "PDB_FILE",
                       f'{WE_HBV_ENM_PATH}/init_files/important_oligomer_pdbs/pentamer_box.pdb'),
                   help='Simulation-start PDB (separated decamer)')
    p.add_argument('--traj',       default=f'{WE_HBV_ENM_PATH}/init_files/lammps_out/seg.dcd',
                   help='trajectory file for pdb')
    p.add_argument('--resid',      type=int, required=True,
                   help='Residue number to measure the distance between on eligible subunits')
    p.add_argument('--output_dir', default='',
                   help=r'By default the txt file is sent to traj_file dir' \
                   r'This argument adds a path: {output_dir}{traj_file_dir}')
    p.add_argument('--contactdir', default=f'{WE_HBV_ENM_PATH}/init_files/contact_files')
    p.add_argument('--contacts', type=int, default=1)
    p.add_argument('--report_pairs', action='store_true',
                   help='Write a separate pair/status diagnostics file')
    return p.parse_args()

# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------

# Which chain types are eligible to bond with a given chain type
ELIGIBLE_BOND_PARTNERS = {
    'A': {'A'},
    'B': {'C', 'D'},
    'C': {'B', 'D'},
    'D': {'B', 'C'},
}

DIMER_PARTNER = {'A': 'B', 'B': 'A', 'C': 'D', 'D': 'C'}


def dimer_partner(segid):
    if len(segid) < 2 or segid[0] not in DIMER_PARTNER or not segid[1:].isdigit():
        raise ValueError(f'Expected a chain ID such as A1/B1/C1/D1; got {segid!r}')
    return DIMER_PARTNER[segid[0]] + segid[1:]


def is_eligible_pair(segid1, segid2):
    """Eligible chain types, excluding self and permanent dimer partners."""
    partner = dimer_partner(segid1)
    dimer_partner(segid2)
    return (segid1 != segid2 and segid2 != partner
            and segid2[0] in ELIGIBLE_BOND_PARTNERS[segid1[0]])


def cluster_membership(segids, frame_clusters):
    """Complete a frame's partition with permanent dimers, including isolated ones.

    Cluster IDs are local to this frame. Unioning memberships also repairs
    overlapping components from older analysis pickles with directed dimer edges.
    """
    segids = sorted(set(segids))
    if not segids:
        raise ValueError('No CA chains found')
    parent = {s: s for s in segids}

    def find(s):
        while parent[s] != s:
            parent[s] = parent[parent[s]]
            s = parent[s]
        return s

    def union(s, t):
        parent[find(t)] = find(s)

    for s in segids:
        partner = dimer_partner(s)
        if partner not in parent:
            raise ValueError(f'Missing permanent dimer partner {partner} for {s}')
        union(s, partner)
    for cluster in frame_clusters:
        members = sorted(cluster['segids'])
        if not members or any(s not in parent for s in members):
            raise ValueError(f'Invalid cluster membership: {members}')
        for s in members[1:]:
            union(members[0], s)
    membership = {s: find(s) for s in segids}
    sizes = {}
    for cid in membership.values():
        sizes[cid] = sizes.get(cid, 0) + 1
    largest = {cid for cid, size in sizes.items() if size == max(sizes.values())}
    return membership, largest


# ---------------------------------------------------------------------------
# Distance Functions
# ---------------------------------------------------------------------------

def build_eligible_pair_selections(u, resid):
    """Validate one CA marker per chain and build inter-dimer candidate pairs."""
    segids = sorted(set(u.select_atoms('name CA').segids))
    cluster_membership(segids, [])  # Validate complete permanent dimers.
    sel = {seg: u.select_atoms(f'name CA and resid {resid} and segid {seg}')
           for seg in segids}
    for seg, atoms in sel.items():
        if len(atoms) != 1:
            raise ValueError(f'Expected exactly one CA at residue {resid} in {seg}; '
                             f'found {len(atoms)}')
    return [(s, t, sel[s], sel[t]) for s, t in combinations(segids, 2)
            if is_eligible_pair(s, t)]


def validate_box(dimensions):
    """The componentwise minimum-image calculation requires an orthorhombic box."""
    if dimensions is None:
        raise ValueError('Trajectory has no periodic box')
    dimensions = np.asarray(dimensions, dtype=float)
    if (dimensions.shape != (6,) or not np.all(np.isfinite(dimensions))
            or np.any(dimensions[:3] <= 0)
            or not np.allclose(dimensions[3:], 90.0, rtol=0, atol=1e-3)):
        raise ValueError(f'Expected a finite, positive orthorhombic box; got {dimensions}')
    return dimensions[:3]


def min_eligible_distance_and_box_limit_per_frame(
        pdb_file, traj_file, resid, clusters_by_frame, *, return_details=False):
    """Measure recruitment to any largest well-formed cluster, in Angstroms.

    clusters_by_frame is the analysis's all_well_formed_clusters mapping;
    missing frames mean no assembled interfaces (isolated permanent dimers).
    Returns {frame: (distance, box_limit)} by default. Distance is None when
    no recruitment pair exists. With return_details=True each value instead
    contains distance, box_limit, pair, and status. Status distinguishes
    fully_connected from no_eligible_partner; neither implies capsid closure.
    """
    if clusters_by_frame is None:
        raise ValueError('Per-frame cluster memberships are required')
    print('Computing minimum eligible recruitment distance per frame...', file=sys.stderr)
    u = mda.Universe(pdb_file, traj_file)
    pair_selections = build_eligible_pair_selections(u, resid)
    segids = sorted(set(u.select_atoms('name CA').segids))
    distances = {}
    for ts in u.trajectory:
        box = validate_box(u.dimensions)
        box_limit = float(np.linalg.norm(box / 2.0))
        membership, largest = cluster_membership(
            segids, clusters_by_frame.get(ts.frame, []))
        if not np.all(np.isfinite(u.select_atoms(f'name CA and resid {resid}').positions)):
            raise ValueError(f'Non-finite marker coordinates in frame {ts.frame}')
        min_dist, best_pair = None, None
        for s, t, ag1, ag2 in pair_selections:
            if membership[s] == membership[t]:
                continue
            if membership[s] not in largest and membership[t] not in largest:
                continue
            diff = ag1.positions[0].astype(float) - ag2.positions[0]
            diff -= box * np.round(diff / box)
            dist = float(np.linalg.norm(diff))
            if min_dist is None or dist < min_dist:
                min_dist, best_pair = dist, (s, t)
        status = ('eligible' if best_pair is not None else
                  'fully_connected' if len(set(membership.values())) == 1 else
                  'no_eligible_partner')
        details = dict(distance=min_dist, box_limit=box_limit,
                       pair=best_pair, status=status)
        distances[ts.frame] = details if return_details else (min_dist, box_limit)
    return distances


def min_eligible_distance_per_frame(pdb_file, traj_file, resid, clusters_by_frame):
    """Return distances only; None means no eligible recruitment pair."""
    measurements = min_eligible_distance_and_box_limit_per_frame(
        pdb_file, traj_file, resid, clusters_by_frame)
    return {frame: distance for frame, (distance, _) in measurements.items()}


def save_min_eligible_distance(pdb_file, traj_file, resid, output_dir,
                               clusters_by_frame, *, report_pairs=False):
    """Write distances (nan if unavailable) and optional pair/status diagnostics."""
    measurements = min_eligible_distance_and_box_limit_per_frame(
        pdb_file, traj_file, resid, clusters_by_frame, return_details=True)
    directory = os.path.dirname(f'{output_dir}{traj_file}') or '.'
    os.makedirs(directory, exist_ok=True)
    output_path = os.path.join(directory, 'min_eligible_distance.txt')
    with open(output_path, 'w') as f:
        for frame, data in sorted(measurements.items()):
            value = data['distance'] if data['distance'] is not None else 'nan'
            f.write(f'{frame} {value}\n')
    if report_pairs:
        with open(os.path.join(directory, 'min_eligible_distance_pairs.txt'), 'w') as f:
            f.write('# frame segid1 segid2 status\n')
            for frame, data in sorted(measurements.items()):
                s, t = data['pair'] or ('-', '-')
                f.write(f"{frame} {s} {t} {data['status']}\n")
    print(f'Saved recruitment distances to {output_path}', file=sys.stderr)
    return {frame: data['distance'] for frame, data in measurements.items()}


if __name__ == '__main__':
    args = parse_args()
    # Recompute memberships for this trajectory rather than silently using a
    # potentially stale pickle. The pcoord caller supplies its fresh analysis.
    from full_traj_analysis import (parse_frames_computed_cutoffs,
                                    build_interface_angle_data,
                                    build_all_well_formed_clusters)
    with redirect_stdout(sys.stderr):
        bonds, _ = parse_frames_computed_cutoffs(args.pdb, args.traj, args.contactdir)
        angles = build_interface_angle_data(args.pdb, args.traj, bonds, args.contacts)
        clusters = build_all_well_formed_clusters(bonds, angles, args.contacts)
    save_min_eligible_distance(args.pdb, args.traj, args.resid, args.output_dir,
                               clusters, report_pairs=args.report_pairs)
