#!/usr/bin/env python
"""
Process the HTGR PRA example file.

This script processes the HTGR PRA sample zip file in the inputs directory
and demonstrates the full Vyom workflow.
"""
import os
import sys
import json
import time
import subprocess
from pathlib import Path

# Get the project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Set paths
input_file = os.path.join(project_root, "data", "inputs", "HTGR_PRA_10162024_Final.zip")
sample_data = os.path.join(project_root, "data", "samples", "HTGR_PRA_saphire_20240320.json")

def run_command(cmd, description):
    """Run a command and print its output."""
    print(f"\n----- {description} -----")
    print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    return True

def main():
    """Main function to process the HTGR PRA example."""
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        print("Please place the HTGR_PRA_10162024_Final.zip file in the data/inputs directory.")
        return False
    
    # Import the zip file
    job_id = str(int(time.time()))
    import_cmd = ["vyom", "import", input_file]
    if not run_command(import_cmd, "Importing HTGR PRA ZIP file"):
        return False
    
    # Get the job ID from the output
    # This is a simplistic approach; in practice, the job ID would be parsed
    # from the command output
    
    # Check job status
    show_cmd = ["vyom", "show", job_id]
    if not run_command(show_cmd, f"Showing job status for {job_id}"):
        return False
    
    # Export raw data
    export_cmd = ["vyom", "export", job_id]
    if not run_command(export_cmd, f"Exporting raw data for {job_id}"):
        return False
    
    # Convert to OpenPRA format
    convert_cmd = ["vyom", "convert", job_id]
    if not run_command(convert_cmd, f"Converting to OpenPRA format for {job_id}"):
        return False
    
    # Alternative: Convert from sample file
    print("\n----- Converting from sample file -----")
    if os.path.exists(sample_data):
        convert_file_cmd = ["vyom", "convert-file", sample_data]
        if not run_command(convert_file_cmd, "Converting sample file to OpenPRA format"):
            return False
    else:
        print(f"Sample file not found: {sample_data}")
    
    # List all jobs
    list_cmd = ["vyom", "list"]
    if not run_command(list_cmd, "Listing all jobs"):
        return False
    
    # Try the visualization (if not headless)
    view_cmd = ["vyom", "view", job_id, "--no-browser"]
    if not run_command(view_cmd, f"Creating visualization for {job_id}"):
        print("Visualization step skipped or failed - this is not critical")
    
    print("\n----- Process completed successfully -----")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 