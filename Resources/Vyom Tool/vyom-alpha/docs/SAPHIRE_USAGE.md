# Vyom SAPHIRE Processing Guide

This guide explains how to use Vyom to extract, analyze, and convert SAPHIRE probabilistic risk assessment (PRA) model files.

## Overview

The Vyom application provides robust capabilities for working with SAPHIRE PRA models:

1. **Extract** - Extract files from SAPHIRE ZIP archives
2. **Analyze** - Analyze SAPHIRE file structures and content
3. **Convert** - Convert SAPHIRE data to the OpenPRA intermediate representation (IR)
4. **Export** - Export processed data for further analysis

## SAPHIRE File Types

Vyom supports processing the following SAPHIRE file types:

| Extension | Description |
|-----------|-------------|
| .MARD     | Master Relational Database file |
| .BEI      | Basic Event Information file |
| .FTL      | Fault Tree Logic file |
| .ETL      | Event Tree Logic file |
| .FAD      | Project Description file |
| .ESL      | End State List file |
| .ESD      | End State Description file |
| .STL      | Sequence List file |
| .STD      | Sequence Description file |
| .GDL      | Graphical Description file |
| .IDX      | Index file |

## Basic Usage

### Processing a SAPHIRE ZIP File

To process a SAPHIRE ZIP file, use the `process` command:

```bash
vyom process path/to/saphire.zip
```

This command will:
1. Extract the ZIP file to a temporary directory
2. Analyze all files and categorize them
3. Identify and parse SAPHIRE-specific files
4. Create a complete SAPHIRE model structure
5. Return a job ID for further operations

### Checking Job Status

To check the status of a processing job:

```bash
vyom status <job_id>
```

### Exploring Processed Data

To explore the data extracted from a SAPHIRE model:

```bash
vyom explore <job_id>
```

You can use JSONPath queries to filter the data:

```bash
vyom explore <job_id> --query $.metadata
vyom explore <job_id> --query $.files[?(@.type=='saphire')]
```

### Converting to OpenPRA Format

To convert the SAPHIRE data to OpenPRA format:

```bash
vyom convert <job_id> --output openpra_result.json
```

### Direct File Conversion

If you already have a SAPHIRE JSON file (perhaps from a previous export), you can convert it directly:

```bash
vyom convert-file saphire_data.json --output openpra_result.json
```

### Exporting Raw Data

To export the raw job data for further analysis:

```bash
vyom export <job_id> --output raw_data.json
```

## Shortcuts and Aliases

For convenience, Vyom provides command aliases:

| Command | Alias |
|---------|-------|
| process | p     |
| status  | s     |
| explore | e     |
| convert | c     |
| convert-file | cf |
| export  | x     |
| jobs    | j     |
| help    | h     |

## OpenPRA Schema

The OpenPRA schema is an intermediate representation that standardizes PRA data for further processing. When converting from SAPHIRE, the following elements are mapped:

- **Project Information** → OpenPRA Metadata
- **Fault Trees** → OpenPRA Fault Tree Models
- **Event Trees** → OpenPRA Event Tree Models
- **Basic Events** → OpenPRA Basic Event Models
- **End States** → OpenPRA End State Models

## Advanced Usage

### Processing Large Models

For large SAPHIRE models (>1GB), specify an output directory to avoid using temporary storage:

```bash
vyom process large_model.zip --output /path/to/extraction/dir
```

### Custom Workflow Integration

Vyom can be integrated into larger workflows:

1. Process a SAPHIRE ZIP to get a job ID
2. Convert to OpenPRA format
3. Use the OpenPRA data with other tools

Example workflow script:

```bash
#!/bin/bash
# Process the SAPHIRE model
JOB_ID=$(vyom process saphire_model.zip | grep "Job ID:" | cut -d' ' -f3)

# Check if processing completed successfully
STATUS=$(vyom status $JOB_ID | grep "Status:" | cut -d' ' -f2)
if [ "$STATUS" != "COMPLETED" ]; then
    echo "Processing failed with status: $STATUS"
    exit 1
fi

# Convert to OpenPRA format
vyom convert $JOB_ID --output model_openpra.json

# Further processing with other tools
# ...
```

## Troubleshooting

### Common Issues

1. **Missing SAPHIRE data in conversion**
   - Check if the ZIP file contains valid SAPHIRE files
   - Use `vyom explore <job_id>` to examine the extracted files

2. **Conversion errors**
   - Ensure the SAPHIRE model is complete and valid
   - Check for warnings in the processing output

3. **Incomplete extraction**
   - Verify the ZIP file is not corrupted
   - Check for adequate disk space

### Getting Help

For more information, use the built-in help:

```bash
vyom help
```

Or get specific command help:

```bash
vyom process --help
```

## Development and Extension

To extend Vyom's SAPHIRE processing capabilities:

1. Add new SAPHIRE file types in `extractor.py`
2. Implement parsers for new file types in `saphire.py`
3. Update the schema mapping in `converter.py`

## References

- [SAPHIRE Documentation](https://saphire.inl.gov/)
- [OpenPRA Schema Documentation](link_to_openpra_docs) 