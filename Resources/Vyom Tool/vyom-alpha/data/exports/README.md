# Exports Directory

This directory contains exported data files from Vyom processing operations. Files are automatically named with timestamps.

## Contents

- SAPHIRE data exports
- OpenPRA format exports
- Other processed data exports

## Naming Convention

Files in this directory follow this naming convention:

`[project]_[type]_[timestamp].[extension]`

Where:
- `project` is the project identifier (e.g., htgr, lwr)
- `type` is the export type (e.g., saphire, openpra)
- `timestamp` is the ISO timestamp (YYYYMMDD_HHMMSS)
- `extension` is typically json

Example: `htgr_openpra_20231015_143022.json`

## Notes

- This directory is typically not committed to version control
- Files may be automatically cleaned up by the application to prevent disk space issues 