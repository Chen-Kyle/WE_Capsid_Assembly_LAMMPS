# Table of contents

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

[Back to table of contents](#table-of-contents)
