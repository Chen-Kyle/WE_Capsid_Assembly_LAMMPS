# Table of contents

- [2026-10-22](#2026-10-22)
- [2026-10-16](#2026-10-16)
- [October 6, 2026](#2026-10-06)
- [October 5, 2026](#2026-10-05)

---

# Changes at a glance

[Read the detailed technical log](CHANGES_TECHNICAL.md)

## 2026-10-05

### Measuring assembly more accurately

- **Count dimers:** two joined dimers now count as 2, rather than 4 chains.

- **Look for new attachments:** the distance measurement now looks outside the largest cluster, instead of measuring connections already inside it.

- **Keep connected pieces together:** fixed a problem that could split one connected assembly into overlapping groups during analysis.

- **Use the final frame:** the last reported progress value now describes the end of the saved trajectory, including when only one value is requested.

### Checking that it works

- **Clearer failure handling:** added checks for missing residues or invalid simulation boxes, and distinguished a fully connected system from one with no eligible attachment partner.

- **Real trajectory checked:** the closest eligible distances in the three basis frames were **174.51, 173.04, and 170.18 Å**, with the selected pairs saved for inspection.

- **Tests passed:** all **9 automated checks** passed, and the final-frame selection was checked separately.

### Keeping records clear

- **Supporting files updated:** corrected explanatory comments and allowed the distance script to be included in version control.

- **CHANGES.md:** added a dated history and navigation, then made this file a short, plain-language summary.

- **CHANGES_TECHNICAL.md:** preserved the detailed file-by-file history in a separate log.

### Local tests

- **.gitignore:** added the tests folder to the ignore list so tests stay local.

- **Test file:** removed it from Git's index while keeping the file on disk.

- **Change logs:** updated both versions to record this tracking change.

### Local pilot

- **west.cfg:** limited the run to four iterations and three walkers per occupied bin.

- **pilot_local.py:** added a separate pilot with one segment at a time, one CPU core, memory safeguards, distance bins, and automatic reports.

- **orientation_diagnostics.py:** added distance and orientation records for nearby eligible pairs without changing the progress score.

- **.gitignore:** kept generated pilot runs out of Git.

- **PILOT.md:** added instructions for starting, monitoring, and stopping the local pilot.

- **Change logs:** recorded the pilot setup in both versions.

[See file-by-file details for this date](CHANGES_TECHNICAL.md#2026-10-05)

---

## 2026-10-06

### Pilot launched

- **Local run:** started the four-iteration pilot with three walkers per occupied bin and confirmed about 350 MiB of combined memory use during its first segment.

- **Change logs:** recorded the launch date and added navigation for October 6 in both versions.

---

## 2026-10-16

### Pilot results

- **PILOT.md:** recorded that all four iterations finished in about 1 hour 51 minutes using at most 471 MiB of sampled combined memory, with no close binding encounters to justify an orientation penalty.

- **Reference check:** found that half of the AA reference interfaces fall outside the current shared angle window, which needs investigation before changing the score.

- **CHANGES.md and CHANGES_TECHNICAL.md:** added this dated outcome summary and navigation link.

---

## 2026-10-22

- **.gitignore:** kept the orientation diagnostic script local and excluded it from Git.

- **Change logs:** recorded the orientation-script exclusion in both versions.

- **.gitignore:** excluded extra log formats, scheduler output, and local pilot scripts, notes, and results while keeping reusable analysis code available to commit.

- **Change logs:** recorded the ignore-rule update in both versions.

---

[Back to table of contents](#table-of-contents)
