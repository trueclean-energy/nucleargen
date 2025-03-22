# Input Files Directory

This directory contains original SAPHIRE ZIP files and other input files that need to be processed.

## Contents

- Original SAPHIRE ZIP exports
- Raw SAPHIRE data files
- Other input data sources

## Usage

Files in this directory are used as inputs for the Vyom processing:

```bash
vyom process data/inputs/HTGR_PRA_10162024_Final.zip
```

## Naming Convention

Files should follow this naming convention:

`[project]_[type]_[date].[extension]`

Where:
- `project` is the project identifier (e.g., htgr, lwr)
- `type` is the data type (e.g., saphire, raw)
- `date` is the date in YYYYMMDD format
- `extension` is typically zip for SAPHIRE files

Example: `HTGR_PRA_10162024_Final.zip`

## Notes

- Large files in this directory should not be committed to version control
- Original files should be preserved and not modified 