"""
Tests for converter functionality
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vyom import converter
from vyom.schema import saphire, openpra

def test_to_openpra():
    """Test converting SAPHIRE data to OpenPRA format"""
    # Create sample job data
    job_data = {
        "files": {
            "model.json": {
                "type": "json",
                "saphire": {
                    "type": "fault_tree",
                    "data": {
                        "id": "FT1",
                        "name": "Sample Fault Tree",
                        "gates": [
                            {
                                "id": "TOP",
                                "type": "OR",
                                "inputs": ["G1", "BE1"]
                            }
                        ],
                        "basic_events": ["BE1", "BE2"]
                    }
                }
            }
        }
    }
    
    # Convert to OpenPRA
    openpra_data = converter.to_openpra(job_data)
    
    # Basic validation
    assert openpra_data is not None, "OpenPRA data should not be None"
    assert "version" in openpra_data, "OpenPRA data should have version"
    assert "metadata" in openpra_data, "OpenPRA data should have metadata"
    assert "models" in openpra_data, "OpenPRA data should have models"
    
    # Check metadata
    assert openpra_data["metadata"]["title"] == "Converted from SAPHIRE", "Title should be set"
    assert openpra_data["metadata"]["source"] == "SAPHIRE Import", "Source should be set"

def test_convert_fault_tree():
    """Test converting a SAPHIRE fault tree to OpenPRA format"""
    # Create a sample OpenPRA data structure
    openpra_data = openpra.create_empty_schema()
    
    # Create a sample SAPHIRE fault tree
    saphire_data = {
        "type": "fault_tree",
        "data": {
            "id": "FT1",
            "name": "Sample Fault Tree",
            "gates": [
                {
                    "id": "TOP",
                    "type": "OR",
                    "inputs": ["G1", "BE1"]
                }
            ],
            "basic_events": ["BE1", "BE2"]
        }
    }
    
    # Convert the fault tree
    converter.convert_fault_tree(saphire_data, openpra_data)
    
    # Check if the fault tree was added
    assert len(openpra_data["models"]["fault_trees"]) == 1, "Fault tree should be added"
    fault_tree = openpra_data["models"]["fault_trees"][0]
    assert fault_tree["id"] == "FT1", "Fault tree ID should match"
    assert fault_tree["name"] == "Sample Fault Tree", "Fault tree name should match"

def test_convert_event_tree():
    """Test converting a SAPHIRE event tree to OpenPRA format"""
    # Create a sample OpenPRA data structure
    openpra_data = openpra.create_empty_schema()
    
    # Create a sample SAPHIRE event tree
    saphire_data = {
        "type": "event_tree",
        "data": {
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
    }
    
    # Convert the event tree
    converter.convert_event_tree(saphire_data, openpra_data)
    
    # Check if the event tree was added
    assert len(openpra_data["models"]["event_trees"]) == 1, "Event tree should be added"
    event_tree = openpra_data["models"]["event_trees"][0]
    assert event_tree["id"] == "ET1", "Event tree ID should match"
    assert event_tree["name"] == "Sample Event Tree", "Event tree name should match"
    assert event_tree["initiating_event"] == "IE1", "Initiating event should match"

def test_convert_basic_event():
    """Test converting a SAPHIRE basic event to OpenPRA format"""
    # Create a sample OpenPRA data structure
    openpra_data = openpra.create_empty_schema()
    
    # Create a sample SAPHIRE basic event
    saphire_data = {
        "type": "basic_event",
        "data": {
            "id": "BE1",
            "name": "Basic Event 1",
            "probability": 0.01,
            "description": "Sample basic event"
        }
    }
    
    # Convert the basic event
    converter.convert_basic_event(saphire_data, openpra_data)
    
    # Check if the basic event was added
    assert len(openpra_data["models"]["basic_events"]) == 1, "Basic event should be added"
    basic_event = openpra_data["models"]["basic_events"][0]
    assert basic_event["id"] == "BE1", "Basic event ID should match"
    assert basic_event["name"] == "Basic Event 1", "Basic event name should match"
    assert basic_event["probability"] == 0.01, "Basic event probability should match"
    assert basic_event["description"] == "Sample basic event", "Basic event description should match"

if __name__ == "__main__":
    test_to_openpra()
    test_convert_fault_tree()
    test_convert_event_tree()
    test_convert_basic_event()
    print("All converter tests passed!") 