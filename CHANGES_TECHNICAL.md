# Table of contents

- [2026-10-22](#2026-10-22)
- [2026-10-16](#2026-10-16)
- [2026-10-06](#2026-10-06)
- [2026-10-05](#2026-10-05)

---

# Technical change log

[Read the quick summary](CHANGES.md)

Maintenance: record each file edit as a dated, one-sentence entry here and keep the plain-language summary in `CHANGES.md` current.

## 2026-10-05

### Recruitment distance and cluster connectivity

**common_files/min_eligible_distance.py**

Restricted recruitment distances to eligible pairs between different clusters involving a largest cluster, excluded permanent dimer partners, completed isolated-dimer memberships, validated markers and boxes, and added missing-partner statuses and optional pair reports.

**common_files/full_traj_analysis.py**

Made permanent-dimer connections bidirectional in both cluster builders so connected components are independent of traversal order.

**common_files/get_pcoord.py**

Passed fresh cluster memberships into recruitment-distance analysis, handled unavailable distances using cluster size alone, and used the current Python interpreter for the analysis subprocess.

**.gitignore**

Removed the exclusion of `common_files/min_eligible_distance.py` so the helper can be tracked in version control.

---

### Dimer counting and frame selection

**common_files/get_pcoord.py**

Changed largest-cluster size from chain count to unique permanent AB/CD dimer count, retained size 1 for isolated dimers, and rejected incomplete dimers.

**west.cfg**

Updated the progress-coordinate comment to describe dimer counts rather than chain counts.

**common_files/get_pcoord.py**

Preserved earlier stride samples while forcing the final output to use the last trajectory frame, including single-output basis calculations, and rejected nonpositive sampling sizes.

**westpa_scripts/get_pcoord.sh**

Updated the basis-coordinate comment to reflect final-frame selection.

---

### Tests

**tests/test_recruitment_distance.py**

Added regression tests for recruitment eligibility, largest-cluster selection, periodic wrapping, changing memberships, unavailable distances, input validation, and undirected cluster connectivity.

**tests/test_recruitment_distance.py**

Added checks for isolated dimers, mixed AB/CD assemblies, largest-cluster selection, a 120-dimer assembly, and incomplete-dimer rejection.

---

### Basis-trajectory results

**bstates/min_eligible_distance.txt**

Regenerated residue-135 recruitment distances from the actual basis trajectory, yielding approximately 174.51, 173.04, and 170.18 Angstroms.

**bstates/min_eligible_distance_pairs.txt**

Added the selected chain pairs and eligibility status for each basis-trajectory frame.

---

### Documentation

**CHANGES.md**

Recorded today's edits made in this session, excluding pre-existing changes.

**CHANGES.md**

Added a linked date table of contents and grouped entries with file labels and spacing for easier reading.

---

**CHANGES_TECHNICAL.md**

Created a separate technical log preserving the existing per-file history and linking to the quick summary.

**CHANGES.md**

Replaced the detailed entries with a plain-language summary and links to the technical record.

---

### Test tracking

**.gitignore**

Added `/tests/` to ignore the repository's local test directory.

**tests/test_recruitment_distance.py**

Removed the test file from the Git index with `git rm --cached`, preserving its working-tree copy and leaving the removal staged for the next commit.

**CHANGES.md**

Added a plain-language summary of the test ignore rule and index removal under 2026-10-05.

**CHANGES_TECHNICAL.md**

Recorded the test tracking changes under 2026-10-05.

---

### Local pilot setup

**west.cfg**

Set `max_total_iterations` to 4 and `bin_target_counts` to 3.

**common_files/orientation_diagnostics.py**

Added streaming eligible-encounter CSV output within 260 Angstroms, matching existing binding/spike angle conventions and grouping native-contact-supported reference pairs by AA, BC, CD, and DB interfaces.

**pilot_local.py**

Added isolated run preparation, integer/distance pilot bins through 120 dimers, serial propagation on one CPU core, 2 GiB per-process address-space limits, 6 GiB aggregate RSS and 8 GiB host-availability watchdogs, and automatic weighted occupancy, cost, and orientation summaries.

**.gitignore**

Ignored `/pilots/` to exclude generated pilot snapshots and output.

**PILOT.md**

Documented pilot preparation, launch, monitoring, stop commands, diagnostic interpretation, and resource-limit scope.

**CHANGES.md**

Added plain-language pilot entries under 2026-10-05.

**CHANGES_TECHNICAL.md**

Recorded pilot implementation and verification under 2026-10-05.

Validation: nine existing tests passed; new angle calculations matched the existing implementation for 300 assembled-reference interfaces; the basis trajectory produced 1,036 eligible encounter records; representative WESTPA bin assignments were checked.

---

## 2026-10-06

### Pilot launch verification

Started `hbv-pilot-20261005-160123.service` on October 6 using the directory prepared on October 5; fresh initialization produced three walkers in one bin with total weight 1, and sampled combined RSS during the first segment was approximately 350 MiB.

**CHANGES.md**

Added the dated pilot launch summary and October 6 table-of-contents link.

**CHANGES_TECHNICAL.md**

Recorded the launch verification and added the October 6 table-of-contents link.

---

## 2026-10-16

### Completed pilot review

**PILOT.md**

Documented successful four-iteration completion, 12 segments, 6,655.9-second runtime, 471.4 MiB sampled aggregate peak RSS, unchanged single-bin occupancy, interface-specific minimum distances, and 60 of 120 AA reference interfaces outside the current binding-angle window.

**CHANGES.md**

Added the plain-language pilot outcome and October 16 navigation link.

**CHANGES_TECHNICAL.md**

Recorded the final pilot findings and October 16 navigation link, with orientation weighting left disabled because no reference-range close encounters were observed.

---

## 2026-10-22

**.gitignore**

Added `/common_files/orientation_diagnostics.py` to exclude the local diagnostic script from version control.

**CHANGES.md**

Recorded the orientation-script exclusion under 2026-10-22.

**CHANGES_TECHNICAL.md**

Recorded the exact ignore-rule change under 2026-10-22.

**.gitignore**

Added patterns for `*.logs`, rotated `*.log.*`, `*.err`, `slurm-*.out`, `.logs/`, `logs/`, `/pilot_local.py`, and `/PILOT.md`, retaining the existing `/pilots/` exclusion.

**CHANGES.md**

Added the plain-language ignore-rule summary and October 22 navigation link.

**CHANGES_TECHNICAL.md**

Recorded the exact ignore patterns and October 22 navigation link.

---

[Back to table of contents](#table-of-contents)
