import json
import os
import logging
from typing import Dict, Any, List

from .schema import saphire, openpra

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def to_openpra(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert SAPHIRE data to OpenPRA format.
    
    Args:
        data: SAPHIRE data from job schema or direct SAPHIRE schema
        
    Returns:
        dict: Data in OpenPRA format
    """
    # Create an empty OpenPRA schema
    openpra_data = openpra.create_empty_schema()
    
    # Update metadata
    openpra_data["metadata"]["title"] = "Converted from SAPHIRE"
    openpra_data["metadata"]["source"] = "SAPHIRE Import"
    
    # Check if we're dealing with a complete SAPHIRE schema or job data
    if "saphire_data" in data:
        # This is job data with a SAPHIRE schema
        saphire_model = data["saphire_data"]
        
        # Add job metadata
        job_id = data.get("job_id", "unknown")
        openpra_data["metadata"]["job_id"] = job_id
        openpra_data["metadata"]["description"] = f"Data from job {job_id}"
        openpra_data["metadata"]["file_count"] = data.get("metadata", {}).get("total_files", 0)
        
        # Update title if project name is available
        if saphire_model and "project" in saphire_model and "name" in saphire_model["project"]:
            project_name = saphire_model["project"]["name"]
            openpra_data["metadata"]["title"] = f"PRA Model: {project_name}"
        
        # Process the SAPHIRE model
        convert_saphire_model(saphire_model, openpra_data)
    
    elif "project" in data and "fault_trees" in data and "event_trees" in data:
        # This is a direct SAPHIRE schema
        convert_saphire_model(data, openpra_data)
    
    else:
        # Legacy support for file-by-file conversion
        logger.warning("Using legacy file-by-file conversion - less accurate results may occur")
        
        # Process each file in the data
        for file_path, file_info in data.get("files", {}).items():
            # Skip files that aren't SAPHIRE related
            if "saphire" not in file_info:
                continue
                
            # Extract SAPHIRE data
            saphire_data = file_info.get("saphire", {})
            
            # Convert based on SAPHIRE data type
            if saphire_data.get("type") == "fault_tree":
                convert_fault_tree(saphire_data, openpra_data)
            elif saphire_data.get("type") == "event_tree":
                convert_event_tree(saphire_data, openpra_data)
            elif saphire_data.get("type") == "basic_event":
                convert_basic_event(saphire_data, openpra_data)
    
    # Validate the OpenPRA data
    is_valid, message = openpra.validate_schema(openpra_data)
    if not is_valid:
        logger.warning(f"Generated OpenPRA model is not valid: {message}")
    
    return openpra_data

def convert_saphire_model(saphire_model: Dict[str, Any], openpra_data: Dict[str, Any]) -> None:
    """
    Convert a complete SAPHIRE model to OpenPRA format.
    
    Args:
        saphire_model: Complete SAPHIRE model
        openpra_data: OpenPRA data to update
    """
    # Update project info in metadata
    if "project" in saphire_model:
        project = saphire_model["project"]
        openpra_data["metadata"]["title"] = f"PRA Model: {project.get('name', 'Unnamed')}"
        openpra_data["metadata"]["description"] = project.get("description", "")
        
        # Add project attributes if available
        if "attributes" in project:
            for key, value in project["attributes"].items():
                openpra_data["metadata"]["attributes"][key] = value
    
    # Convert fault trees
    for fault_tree in saphire_model.get("fault_trees", []):
        openpra_fault_tree = {
            "id": fault_tree.get("id", "unknown"),
            "name": fault_tree.get("name", "Unnamed Fault Tree"),
            "description": fault_tree.get("description", ""),
            "gates": convert_gates(fault_tree.get("gates", [])),
            "basic_events": convert_basic_events_references(fault_tree.get("basic_events", []))
        }
        
        # Add attributes if available
        if "attributes" in fault_tree:
            openpra_fault_tree["attributes"] = fault_tree["attributes"]
        
        # Add to OpenPRA data
        openpra_data["models"]["fault_trees"].append(openpra_fault_tree)
    
    # Convert event trees
    for event_tree in saphire_model.get("event_trees", []):
        openpra_event_tree = {
            "id": event_tree.get("id", "unknown"),
            "name": event_tree.get("name", "Unnamed Event Tree"),
            "description": event_tree.get("description", ""),
            "initiating_event": event_tree.get("initiating_event", ""),
            "sequences": convert_sequences(event_tree.get("sequences", []))
        }
        
        # Add attributes if available
        if "attributes" in event_tree:
            openpra_event_tree["attributes"] = event_tree["attributes"]
        
        # Add to OpenPRA data
        openpra_data["models"]["event_trees"].append(openpra_event_tree)
    
    # Convert basic events
    for basic_event in saphire_model.get("basic_events", []):
        openpra_basic_event = {
            "id": basic_event.get("id", "unknown"),
            "name": basic_event.get("name", "Unnamed Basic Event"),
            "probability": basic_event.get("probability", 0),
            "description": basic_event.get("description", "")
        }
        
        # Add attributes if available
        if "attributes" in basic_event:
            openpra_basic_event["attributes"] = basic_event["attributes"]
        
        # Add to OpenPRA data
        openpra_data["models"]["basic_events"].append(openpra_basic_event)
    
    # Convert end states
    for end_state in saphire_model.get("end_states", []):
        openpra_end_state = {
            "id": end_state.get("id", "unknown"),
            "name": end_state.get("name", "Unnamed End State"),
            "description": end_state.get("description", "")
        }
        
        # Add attributes if available
        if "attributes" in end_state:
            openpra_end_state["attributes"] = end_state["attributes"]
        
        # Add to OpenPRA data
        openpra_data["models"]["end_states"].append(openpra_end_state)

def convert_fault_tree(saphire_data: Dict[str, Any], openpra_data: Dict[str, Any]) -> None:
    """
    Convert a SAPHIRE fault tree to OpenPRA format.
    
    Args:
        saphire_data: SAPHIRE fault tree data
        openpra_data: OpenPRA data to update
    """
    # Extract data from SAPHIRE format
    fault_tree_data = saphire_data.get("data", {})
    
    # Create OpenPRA fault tree structure
    fault_tree = {
        "id": fault_tree_data.get("id", "unknown"),
        "name": fault_tree_data.get("name", "Unnamed Fault Tree"),
        "description": fault_tree_data.get("description", ""),
        "gates": convert_gates(fault_tree_data.get("gates", [])),
        "basic_events": convert_basic_events_references(fault_tree_data.get("basic_events", []))
    }
    
    # Add to OpenPRA data
    openpra_data["models"]["fault_trees"].append(fault_tree)

def convert_event_tree(saphire_data: Dict[str, Any], openpra_data: Dict[str, Any]) -> None:
    """
    Convert a SAPHIRE event tree to OpenPRA format.
    
    Args:
        saphire_data: SAPHIRE event tree data
        openpra_data: OpenPRA data to update
    """
    # Extract data from SAPHIRE format
    event_tree_data = saphire_data.get("data", {})
    
    # Create OpenPRA event tree structure
    event_tree = {
        "id": event_tree_data.get("id", "unknown"),
        "name": event_tree_data.get("name", "Unnamed Event Tree"),
        "description": event_tree_data.get("description", ""),
        "initiating_event": event_tree_data.get("initiating_event", ""),
        "sequences": convert_sequences(event_tree_data.get("sequences", []))
    }
    
    # Add to OpenPRA data
    openpra_data["models"]["event_trees"].append(event_tree)

def convert_basic_event(saphire_data: Dict[str, Any], openpra_data: Dict[str, Any]) -> None:
    """
    Convert a SAPHIRE basic event to OpenPRA format.
    
    Args:
        saphire_data: SAPHIRE basic event data
        openpra_data: OpenPRA data to update
    """
    # Extract data from SAPHIRE format
    basic_event_data = saphire_data.get("data", {})
    
    # Create OpenPRA basic event structure
    basic_event = {
        "id": basic_event_data.get("id", "unknown"),
        "name": basic_event_data.get("name", "Unnamed Basic Event"),
        "probability": basic_event_data.get("probability", 0),
        "description": basic_event_data.get("description", "")
    }
    
    # Add to OpenPRA data
    openpra_data["models"]["basic_events"].append(basic_event)

# Helper conversion functions
def convert_gates(saphire_gates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert SAPHIRE gates to OpenPRA format.
    
    Args:
        saphire_gates: List of SAPHIRE gates
        
    Returns:
        List of OpenPRA gates
    """
    openpra_gates = []
    
    for gate in saphire_gates:
        openpra_gate = {
            "id": gate.get("id", "unknown"),
            "type": normalize_gate_type(gate.get("type", "OR")),
            "inputs": []
        }
        
        # Add inputs
        for input_id in gate.get("inputs", []):
            # In SAPHIRE, gate IDs might have a prefix to indicate type
            # This is a simplification
            if input_id.startswith("G"):
                input_type = "gate"
            else:
                input_type = "basic_event"
                
            openpra_gate["inputs"].append({
                "id": input_id,
                "type": input_type
            })
        
        openpra_gates.append(openpra_gate)
    
    return openpra_gates

def normalize_gate_type(gate_type: str) -> str:
    """
    Normalize gate type to OpenPRA format.
    
    Args:
        gate_type: SAPHIRE gate type
        
    Returns:
        OpenPRA gate type
    """
    gate_type = gate_type.upper()
    
    if gate_type in ["AND", "OR", "NOT", "XOR"]:
        return gate_type
    
    # Map other gate types
    gate_map = {
        "A": "AND",
        "O": "OR",
        "N": "NOT",
        "X": "XOR",
        "NAND": "NAND",
        "NOR": "NOR"
    }
    
    return gate_map.get(gate_type, "OR")  # Default to OR

def convert_basic_events_references(basic_event_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Convert SAPHIRE basic event references to OpenPRA format.
    
    Args:
        basic_event_ids: List of SAPHIRE basic event IDs
        
    Returns:
        List of OpenPRA basic event references
    """
    return [{"id": id} for id in basic_event_ids]

def convert_sequences(saphire_sequences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert SAPHIRE sequences to OpenPRA format.
    
    Args:
        saphire_sequences: List of SAPHIRE sequences
        
    Returns:
        List of OpenPRA sequences
    """
    openpra_sequences = []
    
    for sequence in saphire_sequences:
        openpra_sequence = {
            "id": sequence.get("id", "unknown"),
            "end_state": sequence.get("end_state", ""),
            "path": []
        }
        
        # Convert path if available
        for branch in sequence.get("path", []):
            if isinstance(branch, dict) and "event" in branch and "state" in branch:
                # Modern format
                openpra_sequence["path"].append({
                    "event": branch["event"],
                    "success": branch["state"]
                })
            elif isinstance(branch, str):
                # Legacy format - 'S' for success, 'F' for failure
                success = branch.upper() in ["S", "SUCCESS"]
                openpra_sequence["path"].append({
                    "event": f"Event{len(openpra_sequence['path'])+1}",
                    "success": success
                })
        
        openpra_sequences.append(openpra_sequence)
    
    return openpra_sequences
