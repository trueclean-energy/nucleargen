# Changelog

All notable changes to the Vyom project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Improved and more intuitive CLI command structure:
  - Added `import` command (replaces `process`)
  - Added `list` command (replaces `jobs`)
  - Added `show` command (replaces `status`)
  - Added `view` command (replaces `visualize`)
  - Updated all single-letter aliases to match new command names
  - Added support for `-` or `last` to refer to the most recent job ID
  - Added consistent `--output` and `--format` options across commands
- Improved file organization structure with dedicated directories:
  - `data/inputs/` for original SAPHIRE ZIP files
  - `data/samples/` for sample SAPHIRE data files
  - `data/exports/` for exported data files
  - `data/examples/` for example files used in documentation
  - `data/visual/` for visualization outputs
- Interactive browser-based visualization of SAPHIRE schema:
  - Added `view` command to CLI with alias `v`
  - Monaco-based JSON editor for viewing raw data
  - Tabbed interface for exploring model components
  - Dynamic rendering of basic events, fault trees, and event trees
- Standardized file naming convention for all data files
- Created README files for each data directory
- Added `.gitignore` rules to exclude large input and export files
- Schema versioning system with support for versions 1.0.0, 1.1.0, and 2.0.0
- Script for processing the HTGR PRA example file
- Schema versioning tool for managing OpenPRA schemas
- ESA-compliant OpenPRA schema definition

### Changed
- Enhanced OpenPRA schema with LMP support and versioning
- Improved SAPHIRE file processing with dedicated parsers
- Updated README with detailed file organization information
- Reorganized existing files to follow the new structure
- Renamed CLI commands to be more intuitive and consistent:
  - `process` → `import`
  - `jobs` → `list`
  - `status` → `show`
  - `visualize` → `view`
- Maintained temporary backward compatibility for old command names

### Fixed
- Corrected issues with test file template generation
- Resolved linter errors in run_tests.py
- Fixed issues with parsing certain SAPHIRE file formats

## [0.1.0] - 2024-03-01

### Added
- Initial project structure
- Basic SAPHIRE ZIP extraction capability
- Simple OpenPRA schema definition
- Command-line interface for basic operations
- Database layer using DuckDB 