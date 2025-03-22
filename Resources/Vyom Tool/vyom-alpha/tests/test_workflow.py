import os
import json
import zipfile
import tempfile
import shutil
import uuid
import subprocess
import pytest
from pathlib import Path

# Add parent directory to path so we can import vyom
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vyom import db, extractor, converter


def create_sample_saphire_data():
    """Create sample SAPHIRE data for testing"""
    return {
        "version": "1.0.0",
        "project": {
            "name": "Sample Project",
            "description": "A sample SAPHIRE project for testing"
        },
        "fault_trees": [
            {
                "id": "FT1",
                "name": "Sample Fault Tree",
                "gates": [
                    {
                        "id": "TOP",
                        "type": "OR",
                        "inputs": ["G1", "BE1"]
                    },
                    {
                        "id": "G1",
                        "type": "AND",
                        "inputs": ["BE2", "BE3"]
                    }
                ],
                "basic_events": ["BE1", "BE2", "BE3"]
            }
        ],
        "event_trees": [
            {
                "id": "ET1",
                "name": "Sample Event Tree",
                "initiating_event": "IE1",
                "sequences": [
                    {
                        "id": "SEQ1",
                        "path": [
                            {"event": "FT1", "state": True},
                            {"event": "FT2", "state": False}
                        ],
                        "end_state": "ES1"
                    }
                ]
            }
        ],
        "basic_events": [
            {
                "id": "BE1",
                "name": "Basic Event 1",
                "probability": 0.01,
                "description": "Sample basic event 1"
            },
            {
                "id": "BE2",
                "name": "Basic Event 2",
                "probability": 0.02,
                "description": "Sample basic event 2"
            },
            {
                "id": "BE3",
                "name": "Basic Event 3",
                "probability": 0.03,
                "description": "Sample basic event 3"
            }
        ],
        "end_states": [
            {
                "id": "ES1",
                "name": "End State 1",
                "description": "Sample end state"
            }
        ]
    }


def create_test_zip():
    """Create a test ZIP file with SAPHIRE data"""
    temp_dir = tempfile.mkdtemp(prefix="vyom_test_")
    zip_path = os.path.join(temp_dir, "test_saphire.zip")
    
    # Create a directory to hold the test files
    test_files_dir = os.path.join(temp_dir, "test_files")
    os.makedirs(test_files_dir, exist_ok=True)
    
    # Create a sample SAPHIRE file
    saphire_data = create_sample_saphire_data()
    saphire_file_path = os.path.join(test_files_dir, "saphire_model.json")
    
    with open(saphire_file_path, 'w') as f:
        json.dump(saphire_data, f, indent=2)
    
    # Create a ZIP file with the SAPHIRE file
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write(saphire_file_path, arcname="saphire_model.json")
    
    return zip_path, temp_dir


def test_extract_and_process():
    """Test extracting and processing SAPHIRE data"""
    zip_path, temp_dir = create_test_zip()
    try:
        # Create a job ID for testing
        job_id = "test_" + str(uuid.uuid4())
        
        # Create a job and process the ZIP file
        db.create_job(job_id, zip_path)
        
        # Extract the ZIP file
        extract_dir = extractor.extract_zip(zip_path)
        
        # Analyze the files
        result = extractor.analyze_files(extract_dir, job_id)
        
        # Check if the correct number of files was processed
        assert result["file_count"] == 1, "Expected 1 file to be processed"
        assert len(result["errors"]) == 0, f"Unexpected errors: {result['errors']}"
        
        # Get the job data
        job_data = db.get_job_data(job_id)
        assert job_data is not None, "Job data should not be None"
        assert "files" in job_data, "Job data should contain 'files'"
        
        # Check if the SAPHIRE file was correctly identified
        saphire_files = [f for f, info in job_data.get("files", {}).items() 
                        if "saphire" in info]
        assert len(saphire_files) == 1, "Expected 1 SAPHIRE file"
        
        # Convert to OpenPRA format
        openpra_data = converter.to_openpra(job_data)
        assert openpra_data is not None, "OpenPRA data should not be None"
        
        # Basic validation of OpenPRA data
        assert "version" in openpra_data, "OpenPRA data should have 'version'"
        assert "metadata" in openpra_data, "OpenPRA data should have 'metadata'"
        assert "models" in openpra_data, "OpenPRA data should have 'models'"
        
        print("Test extract_and_process passed successfully!")
        return True
    
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False
    
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_cli_workflow():
    """Test the CLI workflow"""
    zip_path, temp_dir = create_test_zip()
    try:
        # Run the CLI command to import the ZIP file
        result = subprocess.run(
            ["python", "-m", "vyom.cli", "import", zip_path],
            capture_output=True,
            text=True
        )
        
        # Check if the command was successful
        assert result.returncode == 0, f"CLI import command failed: {result.stderr}"
        
        # Extract the job ID from the output
        output_lines = result.stdout.strip().split("\n")
        job_id_line = next((line for line in output_lines if "Job ID:" in line), None)
        assert job_id_line is not None, "Could not find job ID in output"
        
        job_id = job_id_line.split("Job ID:")[1].split("-")[0].strip()
        
        # Check the job status
        result = subprocess.run(
            ["python", "-m", "vyom.cli", "show", job_id],
            capture_output=True,
            text=True
        )
        
        # Check if the command was successful
        assert result.returncode == 0, f"CLI show command failed: {result.stderr}"
        assert "COMPLETED" in result.stdout, "Job status should be COMPLETED"
        
        # Export the job data
        export_path = os.path.join(temp_dir, "export.json")
        result = subprocess.run(
            ["python", "-m", "vyom.cli", "export", job_id, "--output", export_path],
            capture_output=True,
            text=True
        )
        
        # Check if the command was successful
        assert result.returncode == 0, f"CLI export command failed: {result.stderr}"
        assert os.path.exists(export_path), "Export file should exist"
        
        # Convert to OpenPRA format
        convert_path = os.path.join(temp_dir, "openpra.json")
        result = subprocess.run(
            ["python", "-m", "vyom.cli", "convert", job_id, "--output", convert_path],
            capture_output=True,
            text=True
        )
        
        # Check if the command was successful
        assert result.returncode == 0, f"CLI convert command failed: {result.stderr}"
        assert os.path.exists(convert_path), "Convert file should exist"
        
        # List all jobs
        result = subprocess.run(
            ["python", "-m", "vyom.cli", "list"],
            capture_output=True,
            text=True
        )
        
        # Check if the command was successful
        assert result.returncode == 0, f"CLI list command failed: {result.stderr}"
        assert job_id in result.stdout, "Job ID should be in the list output"
        
        print("Test cli_workflow passed successfully!")
        return True
    
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False
    
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Create the tests directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    # Run the tests
    test_extract_and_process()
    test_cli_workflow() 