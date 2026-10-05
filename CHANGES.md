# Table of contents

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

[See file-by-file details for this date](CHANGES_TECHNICAL.md#2026-10-05)

---

[Back to table of contents](#table-of-contents)
