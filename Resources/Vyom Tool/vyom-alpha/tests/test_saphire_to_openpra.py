#!/usr/bin/env python
'''
Test the SAPHIRE to OpenPRA converter
'''
import os
import sys
import json
import tempfile

# Add the parent directory to the path so that we can import the vyom module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vyom.schema import saphire, openpra
from vyom import converter

def create_test_saphire_data():
    '''Create test SAPHIRE data for conversion testing'''
    return {
        "version": "1.0.0",
        "project": {
            "name": "Test Project",
            "description": "A test project for conversion",
            "attributes": {
                "mission_time": 24.0,
                "analyst": "Test User"
            }
        },
        "fault_trees": [
            {
                "id": "FT1",
                "name": "First Fault Tree",
                "description": "A test fault tree",
                "gates": [
                    {
                        "id": "G1",
                        "type": "OR",
                        "inputs": ["G2", "BE1"]
                    },
                    {
                        "id": "G2",
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
                "name": "First Event Tree",
                "description": "A test event tree",
                "initiating_event": "IE1",
                "sequences": [
                    {
                        "id": "SEQ1",
                        "end_state": "ES-CD",
                        "path": [
                            {"event": "TOP1", "state": True},
                            {"event": "TOP2", "state": False}
                        ]
                    },
                    {
                        "id": "SEQ2",
                        "end_state": "ES-OK",
                        "path": [
                            {"event": "TOP1", "state": False}
                        ]
                    }
                ]
            }
        ],
        "basic_events": [
            {
                "id": "BE1",
                "name": "First Basic Event",
                "description": "A test basic event",
                "probability": 0.01
            },
            {
                "id": "BE2",
                "name": "Second Basic Event",
                "description": "Another test basic event",
                "probability": 0.02
            },
            {
                "id": "BE3",
                "name": "Third Basic Event",
                "description": "Yet another test basic event",
                "probability": 0.03
            },
            {
                "id": "IE1",
                "name": "Initiating Event",
                "description": "A test initiating event",
                "probability": 1.0e-3
            }
        ],
        "end_states": [
            {
                "id": "ES-CD",
                "name": "Core Damage",
                "description": "A test end state for core damage"
            },
            {
                "id": "ES-OK",
                "name": "Success",
                "description": "A test end state for success"
            }
        ]
    }

def test_direct_saphire_conversion():
    '''Test direct conversion of SAPHIRE data to OpenPRA format'''
    print("Testing direct SAPHIRE to OpenPRA conversion...")
    
    # Create test SAPHIRE data
    saphire_data = create_test_saphire_data()
    
    # Convert to OpenPRA
    openpra_data = converter.to_openpra(saphire_data)
    
    # Validate the generated OpenPRA data
    is_valid, message = openpra.validate_schema(openpra_data)
    assert is_valid, f"Invalid OpenPRA schema: {message}"
    
    # Check specific conversions
    assert openpra_data["metadata"]["title"] == "PRA Model: Test Project"
    assert openpra_data["metadata"]["description"] == "A test project for conversion"
    
    # Check fault trees
    ft = openpra_data["models"]["fault_trees"][0]
    assert ft["id"] == "FT1"
    assert ft["name"] == "First Fault Tree"
    assert len(ft["gates"]) == 2
    
    # Check event trees
    et = openpra_data["models"]["event_trees"][0]
    assert et["id"] == "ET1"
    assert et["name"] == "First Event Tree"
    assert len(et["sequences"]) == 2
    
    # Check basic events
    assert len(openpra_data["models"]["basic_events"]) == 4
    
    # Check end states
    assert len(openpra_data["models"]["end_states"]) == 2
    
    print("Direct conversion test passed!")
    return True

def test_job_data_conversion():
    '''Test conversion of job data to OpenPRA format'''
    print("Testing job data to OpenPRA conversion...")
    
    # Create test job data
    job_data = {
        "job_id": "1234567890",
        "metadata": {
            "total_files": 10,
            "errors": 0,
            "warnings": 0
        },
        "saphire_data": create_test_saphire_data()
    }
    
    # Convert to OpenPRA
    openpra_data = converter.to_openpra(job_data)
    
    # Validate the generated OpenPRA data
    is_valid, message = openpra.validate_schema(openpra_data)
    assert is_valid, f"Invalid OpenPRA schema: {message}"
    
    # Check job-specific metadata
    assert openpra_data["metadata"]["job_id"] == "1234567890"
    assert "file_count" in openpra_data["metadata"]
    
    # Check model content
    assert len(openpra_data["models"]["fault_trees"]) == 1
    assert len(openpra_data["models"]["event_trees"]) == 1
    assert len(openpra_data["models"]["basic_events"]) == 4
    
    print("Job data conversion test passed!")
    return True

def test_saphire_file_reading():
    '''Test the reading and parsing of SAPHIRE files'''
    print("Testing SAPHIRE file reading and parsing...")
    
    # Create a temporary file with test content
    with tempfile.NamedTemporaryFile(suffix='.BEI', mode='w+', delete=False) as f:
        # Create a basic event information file
        f.write("BE1,0.01,First Basic Event\n")
        f.write("BE2,0.02,Second Basic Event\n")
        f.write("BE3,0.03,Third Basic Event\n")
        bei_path = f.name
    
    try:
        # Test parsing the BEI file
        from vyom.schema.saphire import parse_bei_file
        
        with open(bei_path, 'r') as f:
            content = f.read()
            result = parse_bei_file(content)
        
        # Check the parsed data
        assert result["type"] == "basic_event_info"
        assert len(result["data"]["basic_events"]) == 3
        assert result["data"]["basic_events"][0]["id"] == "BE1"
        assert result["data"]["basic_events"][0]["probability"] == 0.01
        assert result["data"]["basic_events"][0]["name"] == "First Basic Event"
        
        print("SAPHIRE file reading test passed!")
        return True
    
    finally:
        # Clean up
        if os.path.exists(bei_path):
            os.unlink(bei_path)

def main():
    '''Main function'''
    # Run all tests
    tests_passed = True
    
    # Test direct conversion
    try:
        if not test_direct_saphire_conversion():
            tests_passed = False
    except Exception as e:
        print(f"Error in direct conversion test: {str(e)}")
        tests_passed = False
    
    # Test job data conversion
    try:
        if not test_job_data_conversion():
            tests_passed = False
    except Exception as e:
        print(f"Error in job data conversion test: {str(e)}")
        tests_passed = False
    
    # Test file reading
    try:
        if not test_saphire_file_reading():
            tests_passed = False
    except Exception as e:
        print(f"Error in file reading test: {str(e)}")
        tests_passed = False
    
    # Return status
    if tests_passed:
        print("All SAPHIRE to OpenPRA converter tests passed!")
        return 0
    else:
        print("Some SAPHIRE to OpenPRA converter tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 