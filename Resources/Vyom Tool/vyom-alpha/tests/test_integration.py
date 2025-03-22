#!/usr/bin/env python
'''
Integration tests for Vyom

These tests check that multiple components of the application work
together correctly.
'''
import os
import sys
import json
import tempfile
import shutil

# Add the parent directory to the path so that we can import the vyom module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vyom import extractor, converter
from vyom.schema import saphire, openpra

# Use the test file from the SAPHIRE schema tests
def test_extract_and_convert_workflow():
    '''Test the full workflow from extracting files to converting to OpenPRA'''
    print("Testing extract and convert workflow...")
    
    # Get the test ZIP file path
    zip_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          'HTGR_PRA_10162024_Final.zip')
    
    if not os.path.exists(zip_path):
        print(f"Test ZIP file not found at {zip_path}, skipping integration test")
        return True  # Skip test but don't fail
    
    try:
        # Create a temporary directory for extraction
        output_dir = tempfile.mkdtemp(prefix='vyom_test_integration_')
        
        # 1. Extract the ZIP file
        print("1. Extracting ZIP file...")
        extract_dir = extractor.extract_zip(zip_path, output_dir=output_dir)
        assert os.path.exists(extract_dir), "Extraction directory should exist"
        
        # 2. Analyze the files
        print("2. Analyzing files...")
        job_id = "test_integration_job"
        schema_data = extractor.analyze_files(extract_dir, job_id)
        
        # 3. Check if SAPHIRE data was found
        assert "saphire_data" in schema_data, "SAPHIRE data should be extracted"
        saphire_data = schema_data["saphire_data"]
        
        # 4. Validate the SAPHIRE data structure
        is_valid, message = saphire.validate_schema(saphire_data)
        print(f"SAPHIRE schema validation: {message}")
        assert is_valid, f"SAPHIRE data should be valid: {message}"
        
        # 5. Check that the essential components are present
        assert "project" in saphire_data, "Project info should be present"
        assert "name" in saphire_data["project"], "Project name should be present"
        
        # Count elements
        ft_count = len(saphire_data.get("fault_trees", []))
        et_count = len(saphire_data.get("event_trees", []))
        be_count = len(saphire_data.get("basic_events", []))
        print(f"Found {ft_count} fault trees, {et_count} event trees, {be_count} basic events")
        
        # 6. Convert to OpenPRA format
        print("6. Converting to OpenPRA format...")
        openpra_data = converter.to_openpra(schema_data)
        
        # 7. Validate the OpenPRA data
        is_valid, message = openpra.validate_schema(openpra_data)
        print(f"OpenPRA schema validation: {message}")
        assert is_valid, f"OpenPRA data should be valid: {message}"
        
        # 8. Check OpenPRA metadata
        assert "metadata" in openpra_data, "Metadata should be present in OpenPRA data"
        assert openpra_data["metadata"]["job_id"] == job_id, "Job ID should be preserved"
        assert "models" in openpra_data, "Models should be present in OpenPRA data"
        
        # Count OpenPRA elements
        ft_count = len(openpra_data["models"]["fault_trees"])
        et_count = len(openpra_data["models"]["event_trees"])
        be_count = len(openpra_data["models"]["basic_events"])
        print(f"Converted to {ft_count} fault trees, {et_count} event trees, {be_count} basic events")
        
        # 9. Save to file to verify serialization
        test_output_file = os.path.join(output_dir, "test_openpra_output.json")
        with open(test_output_file, 'w') as f:
            json.dump(openpra_data, f, indent=2)
        
        assert os.path.exists(test_output_file), "Output file should exist"
        
        # 10. Read back the file to verify it's valid JSON
        with open(test_output_file, 'r') as f:
            reloaded_data = json.load(f)
        
        assert "version" in reloaded_data, "Version should be present in reloaded data"
        
        print("Extract and convert workflow test passed!")
        return True
        
    except Exception as e:
        print(f"Error in integration test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        if os.path.exists(output_dir):
            try:
                shutil.rmtree(output_dir)
            except Exception as e:
                print(f"Warning: Cleanup failed: {str(e)}")

def test_direct_file_conversion():
    '''Test direct conversion of a SAPHIRE JSON file to OpenPRA format'''
    print("Testing direct file conversion...")
    
    # Get the test SAPHIRE JSON file
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'htgr_saphire_data.json')
    
    if not os.path.exists(json_path):
        print(f"Test JSON file not found at {json_path}, skipping direct conversion test")
        return True  # Skip test but don't fail
    
    try:
        # 1. Load the SAPHIRE JSON file
        print("1. Loading SAPHIRE JSON file...")
        with open(json_path, 'r') as f:
            saphire_data = json.load(f)
        
        # 2. Validate the SAPHIRE data
        is_valid, message = saphire.validate_schema(saphire_data)
        print(f"SAPHIRE schema validation: {message}")
        assert is_valid, f"SAPHIRE data should be valid: {message}"
        
        # 3. Convert to OpenPRA format
        print("3. Converting to OpenPRA format...")
        openpra_data = converter.to_openpra(saphire_data)
        
        # 4. Validate the OpenPRA data
        is_valid, message = openpra.validate_schema(openpra_data)
        print(f"OpenPRA schema validation: {message}")
        assert is_valid, f"OpenPRA data should be valid: {message}"
        
        # 5. Check the conversion results
        project_name = saphire_data["project"]["name"]
        assert openpra_data["metadata"]["title"] == f"PRA Model: {project_name}", "Project name should be in title"
        
        # Compare counts
        saphire_ft_count = len(saphire_data.get("fault_trees", []))
        openpra_ft_count = len(openpra_data["models"]["fault_trees"])
        assert saphire_ft_count == openpra_ft_count, "Fault tree count should match"
        
        saphire_et_count = len(saphire_data.get("event_trees", []))
        openpra_et_count = len(openpra_data["models"]["event_trees"])
        assert saphire_et_count == openpra_et_count, "Event tree count should match"
        
        saphire_be_count = len(saphire_data.get("basic_events", []))
        openpra_be_count = len(openpra_data["models"]["basic_events"])
        assert saphire_be_count == openpra_be_count, "Basic event count should match"
        
        print("Direct file conversion test passed!")
        return True
        
    except Exception as e:
        print(f"Error in direct conversion test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    '''Main function'''
    tests_passed = True
    
    # Test extract and convert workflow
    if not test_extract_and_convert_workflow():
        tests_passed = False
    
    # Test direct file conversion
    if not test_direct_file_conversion():
        tests_passed = False
    
    # Return status
    if tests_passed:
        print("All integration tests passed!")
        return 0
    else:
        print("Some integration tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 