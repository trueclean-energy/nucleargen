"""
Tests for schema validation
"""
import os
import json
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vyom.schema import saphire, openpra

def test_saphire_schema():
    """Test SAPHIRE schema validation"""
    # Create a valid fault tree
    valid_fault_tree = {
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
    
    # Test validation of valid fault tree
    is_valid, message = saphire.validate_fault_tree(valid_fault_tree)
    assert is_valid, f"Valid fault tree failed validation: {message}"
    
    # Create an invalid fault tree (missing gates)
    invalid_fault_tree = {
        "id": "FT1",
        "name": "Sample Fault Tree",
        "basic_events": ["BE1", "BE2"]
    }
    
    # Test validation of invalid fault tree
    is_valid, message = saphire.validate_fault_tree(invalid_fault_tree)
    assert not is_valid, "Invalid fault tree passed validation"
    assert "gates" in message, f"Validation message should mention missing field: {message}"

def test_openpra_schema():
    """Test OpenPRA schema validation"""
    # Create a valid OpenPRA schema
    valid_schema = openpra.create_empty_schema()
    valid_schema["metadata"]["title"] = "Test Schema"
    
    # Test validation of valid schema
    is_valid, message = openpra.validate_schema(valid_schema)
    assert is_valid, f"Valid schema failed validation: {message}"
    
    # Create an invalid schema (missing models)
    invalid_schema = {
        "version": openpra.SCHEMA_VERSION,
        "metadata": {
            "title": "Test Schema"
        }
    }
    
    # Test validation of invalid schema
    is_valid, message = openpra.validate_schema(invalid_schema)
    assert not is_valid, "Invalid schema passed validation"
    assert "models" in message, f"Validation message should mention missing key: {message}"

def test_create_model_from_data():
    """Test creating an OpenPRA model from source data"""
    # Test creating a basic model
    model = openpra.create_model_from_data("test_source", {})
    
    # Check the model structure
    assert model["id"] == "test_source", "Model ID should match source"
    assert "type" in model, "Model should have a type"
    assert "name" in model, "Model should have a name"
    assert "data" in model, "Model should have data"

if __name__ == "__main__":
    test_saphire_schema()
    test_openpra_schema()
    test_create_model_from_data()
    print("All schema tests passed!") 