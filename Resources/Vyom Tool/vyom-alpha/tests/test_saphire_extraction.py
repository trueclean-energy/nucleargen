"""
Test SAPHIRE file extraction and parsing workflow
"""
import os
import json
import zipfile
import tempfile
import shutil
import uuid
from pathlib import Path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vyom import db, extractor

def create_test_files():
    """Create various test files that might be found in a SAPHIRE export"""
    temp_dir = tempfile.mkdtemp(prefix="vyom_test_files_")
    
    # Create a variety of file types that might be in a SAPHIRE export
    
    # 1. Create a basic event file (.BEI format)
    bei_file = os.path.join(temp_dir, "SYSTEM.BEI")
    with open(bei_file, 'w') as f:
        f.write("BE1,0.01,Basic Event 1,RANDOM\n")
        f.write("BE2,0.02,Basic Event 2,RANDOM\n")
        f.write("BE3,0.03,Basic Event 3,RANDOM\n")
    
    # 2. Create a fault tree file (.FTL format)
    ftl_file = os.path.join(temp_dir, "SYSTEM.FTL")
    with open(ftl_file, 'w') as f:
        f.write("TOP,OR,BE1,G1\n")
        f.write("G1,AND,BE2,BE3\n")
    
    # 3. Create an event tree file (.ETG format)
    etg_file = os.path.join(temp_dir, "SYSTEM.ETG")
    with open(etg_file, 'w') as f:
        f.write("LOSP,Initiating Event\n")
        f.write("RPS,Top Event 1\n")
        f.write("AFW,Top Event 2\n")
        f.write("SEQ1,OK,SUCCESS,SUCCESS\n")
        f.write("SEQ2,CD,SUCCESS,FAILURE\n")
        f.write("SEQ3,CD,FAILURE\n")
    
    # 4. Create a project file (.FAD format)
    fad_file = os.path.join(temp_dir, "SYSTEM.FAD")
    with open(fad_file, 'w') as f:
        f.write("Test SAPHIRE Project,This is a test project for Vyom\n")
    
    # 5. Create a descriptive JSON file that might be included
    json_file = os.path.join(temp_dir, "project_info.json")
    project_info = {
        "name": "Test SAPHIRE Project",
        "description": "Test project for SAPHIRE export",
        "created_date": "2023-01-01",
        "version": "8.2.0"
    }
    with open(json_file, 'w') as f:
        json.dump(project_info, f, indent=2)
    
    return temp_dir

def create_test_zip():
    """Create a test ZIP file with SAPHIRE-like files"""
    # Create test files
    files_dir = create_test_files()
    
    # Create a temporary directory for the ZIP file
    temp_dir = tempfile.mkdtemp(prefix="vyom_test_zip_")
    zip_path = os.path.join(temp_dir, "saphire_export.zip")
    
    # Create a ZIP file with all the test files
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for root, _, files in os.walk(files_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, files_dir)
                zip_file.write(file_path, arcname=arcname)
    
    # Clean up the test files
    shutil.rmtree(files_dir)
    
    return zip_path, temp_dir

def test_extraction_workflow():
    """Test the extraction and parsing workflow"""
    zip_path, temp_dir = create_test_zip()
    try:
        # Create a job ID for testing
        job_id = f"test_{uuid.uuid4()}"
        
        # Create a job in the database
        db.create_job(job_id, zip_path)
        
        # Extract files from the ZIP
        extract_dir = extractor.extract_zip(zip_path)
        print(f"Extracted files to: {extract_dir}")
        
        # List the extracted files
        print("Extracted files:")
        for root, _, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                print(f"  {os.path.relpath(file_path, extract_dir)}")
        
        # Analyze the extracted files
        result = extractor.analyze_files(extract_dir, job_id)
        print(f"Analysis result: {json.dumps(result, indent=2)}")
        
        # Check if files were processed
        assert result["file_count"] > 0, "No files were processed"
        assert len(result["errors"]) == 0, f"Errors during processing: {result['errors']}"
        
        # Get the processed data
        job_data = db.get_job_data(job_id)
        assert job_data is not None, "Job data not found"
        
        # Examine the job data structure
        print(f"Files in job data: {len(job_data.get('files', {}))}")
        
        # Check if file types were identified correctly
        file_types = {}
        for file_path, file_info in job_data.get("files", {}).items():
            file_type = file_info.get("type", "unknown")
            if file_type not in file_types:
                file_types[file_type] = 0
            file_types[file_type] += 1
        
        print(f"File types identified: {file_types}")
        
        # Check for SAPHIRE-specific parsing
        saphire_files = []
        for file_path, file_info in job_data.get("files", {}).items():
            if "saphire" in file_info:
                saphire_files.append(file_path)
        
        print(f"Files identified as SAPHIRE: {saphire_files}")
        
        return True
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_is_saphire_file_detection():
    """Test the SAPHIRE file detection logic"""
    # Test with a project info JSON that should be detected as SAPHIRE
    project_data = {
        "project": {
            "name": "Test Project",
            "description": "A test project"
        },
        "fault_trees": [
            {
                "id": "FT1",
                "name": "Sample Fault Tree"
            }
        ],
        "event_trees": [],
        "basic_events": []
    }
    
    # Create a temporary file
    temp_dir = tempfile.mkdtemp(prefix="vyom_test_detection_")
    file_path = os.path.join(temp_dir, "saphire_project.json")
    
    try:
        with open(file_path, 'w') as f:
            json.dump(project_data, f)
        
        # Test detection
        is_saphire = extractor.is_saphire_file(file_path, project_data)
        assert is_saphire, "Failed to detect valid SAPHIRE JSON file"
        
        # Test with non-SAPHIRE JSON
        non_saphire_data = {
            "name": "Not a SAPHIRE file",
            "data": {
                "some_field": "some_value"
            }
        }
        
        non_saphire_path = os.path.join(temp_dir, "not_saphire.json")
        with open(non_saphire_path, 'w') as f:
            json.dump(non_saphire_data, f)
        
        is_saphire = extractor.is_saphire_file(non_saphire_path, non_saphire_data)
        assert not is_saphire, "Incorrectly detected non-SAPHIRE file as SAPHIRE"
        
        # Test with filename-based detection
        saphire_name_path = os.path.join(temp_dir, "saphire_model_export.json")
        with open(saphire_name_path, 'w') as f:
            json.dump(non_saphire_data, f)
        
        is_saphire = extractor.is_saphire_file(saphire_name_path, non_saphire_data)
        assert is_saphire, "Failed to detect SAPHIRE file based on filename"
        
        return True
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_file_type_detection():
    """Test file type detection logic"""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="vyom_test_filetype_")
    
    try:
        # Create files of different types
        file_types = {
            "test.json": "json",
            "test.xml": "xml",
            "test.csv": "csv",
            "test.txt": "text",
            "test.dat": "text",
            "test.pdf": "unknown",
            "test.exe": "unknown",
            "test.BEI": "text",  # SAPHIRE-specific format
            "test.FTL": "text"   # SAPHIRE-specific format
        }
        
        for filename, expected_type in file_types.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write("Test content")
            
            detected_type = extractor.determine_file_type(file_path)
            assert detected_type == expected_type, f"Expected {expected_type} for {filename}, got {detected_type}"
        
        return True
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    print("\nTesting file type detection...")
    test_file_type_detection()
    
    print("\nTesting SAPHIRE file detection...")
    test_is_saphire_file_detection()
    
    print("\nTesting extraction workflow...")
    test_extraction_workflow()
    
    print("\nAll tests completed.") 