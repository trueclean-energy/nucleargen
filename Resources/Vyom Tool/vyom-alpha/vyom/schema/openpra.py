"""
OpenPRA schema definitions - the base IR for Vyom.
"""
import os
import json
import logging
import datetime
from typing import Dict, Any, Tuple, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Schema version history
SCHEMA_VERSIONS = {
    "1.0.0": {
        "release_date": "2023-10-01",
        "description": "Initial schema version",
        "file": None  # Built-in schema
    },
    "1.1.0": {
        "release_date": "2023-12-15",
        "description": "Added attributes to models",
        "file": None  # Built-in schema
    },
    "2.0.0": {
        "release_date": "2024-03-01",
        "description": "Major schema update with LMP support",
        "file": None  # Built-in schema
    }
}

# Current OpenPRA schema version
SCHEMA_VERSION = "2.0.0"

# Core OpenPRA schema structure for version 2.0.0
OPENPRA_SCHEMA = {
    "version": SCHEMA_VERSION,
    "metadata": {
        "title": "",
        "description": "",
        "created_date": "",
        "source": "",
        "schema_version": SCHEMA_VERSION,  # Track the schema version explicitly
        "attributes": {}
    },
    "models": {
        "fault_trees": [],
        "event_trees": [],
        "basic_events": [],
        "initiating_events": [],
        "end_states": [],
        "sequences": []
    },
    "analysis": {
        "quantifications": [],
        "importance_measures": [],
        "uncertainty": {}
    },
    "lmp": {
        "lbes": [],  # Licensing Basis Events
        "sscs": [],  # Structures, Systems, and Components
        "drm": {}    # Defense-in-Depth and Risk Measures
    }
}

def get_schema_versions() -> List[str]:
    """Get a list of all available schema versions"""
    return list(SCHEMA_VERSIONS.keys())

def get_latest_schema_version() -> str:
    """Get the latest schema version"""
    return SCHEMA_VERSION

def get_schema_version_info(version: str) -> Dict[str, Any]:
    """Get information about a specific schema version"""
    if version in SCHEMA_VERSIONS:
        return SCHEMA_VERSIONS[version]
    return {"error": f"Version {version} not found"}

def create_empty_schema(version: Optional[str] = None) -> Dict[str, Any]:
    """
    Create an empty OpenPRA schema with current date.
    
    Args:
        version: Optional schema version to use (defaults to latest)
    
    Returns:
        Dict[str, Any]: A new OpenPRA schema instance
    """
    if version is None:
        version = SCHEMA_VERSION
    
    if version not in SCHEMA_VERSIONS:
        logger.warning(f"Requested schema version {version} not found, using latest ({SCHEMA_VERSION})")
        version = SCHEMA_VERSION
    
    # For now, we only have one schema structure (could add version-specific schemas in the future)
    schema = OPENPRA_SCHEMA.copy()
    
    # Update version
    schema["version"] = version
    schema["metadata"]["schema_version"] = version
    
    # Add creation date
    schema["metadata"]["created_date"] = datetime.datetime.now().isoformat()
    
    return schema

def validate_schema(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that data conforms to OpenPRA schema.
    
    Args:
        data: Data to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if top-level keys exist
    required_keys = ["version", "metadata", "models"]
    for key in required_keys:
        if key not in data:
            return False, f"Missing required key: {key}"
    
    # Get the schema version from the data
    schema_version = data.get("version", "unknown")
    
    # Check if the version is supported
    if schema_version not in SCHEMA_VERSIONS:
        return False, f"Unsupported schema version: {schema_version}. Supported versions: {', '.join(SCHEMA_VERSIONS.keys())}"
    
    # Validation logic based on schema version
    if schema_version == "1.0.0" or schema_version == "1.1.0":
        return validate_schema_v1(data)
    elif schema_version == "2.0.0":
        return validate_schema_v2(data)
    else:
        return False, f"No validation logic for schema version {schema_version}"

def validate_schema_v1(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate against version 1.x schema"""
    # Validate metadata
    if not isinstance(data["metadata"], dict):
        return False, "Metadata must be a dictionary"
    
    # Validate models
    if not isinstance(data["models"], dict):
        return False, "Models must be a dictionary"
    
    model_keys = ["fault_trees", "event_trees", "basic_events", "end_states"]
    for key in model_keys:
        if key not in data["models"]:
            return False, f"Missing required model key: {key}"
        if not isinstance(data["models"][key], list):
            return False, f"{key} must be a list"
    
    # Basic validation of models
    return validate_models(data["models"])

def validate_schema_v2(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate against version 2.x schema"""
    # Validate metadata
    if not isinstance(data["metadata"], dict):
        return False, "Metadata must be a dictionary"
    
    # Validate models
    if not isinstance(data["models"], dict):
        return False, "Models must be a dictionary"
    
    model_keys = ["fault_trees", "event_trees", "basic_events", "initiating_events", "end_states", "sequences"]
    for key in model_keys:
        if key not in data["models"]:
            return False, f"Missing required model key: {key}"
        if not isinstance(data["models"][key], list):
            return False, f"{key} must be a list"
    
    # Validate LMP section
    if "lmp" not in data:
        return False, "Missing required LMP section"
    
    if not isinstance(data["lmp"], dict):
        return False, "LMP section must be a dictionary"
    
    lmp_keys = ["lbes", "sscs", "drm"]
    for key in lmp_keys:
        if key not in data["lmp"]:
            return False, f"Missing required LMP key: {key}"
    
    # Basic validation of models
    return validate_models(data["models"])

def validate_models(models: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate model structures"""
    # Validate fault trees
    for i, ft in enumerate(models["fault_trees"]):
        if not isinstance(ft, dict):
            return False, f"Fault tree {i} must be a dictionary"
        if "id" not in ft:
            return False, f"Fault tree {i} missing id"
        if "gates" not in ft:
            return False, f"Fault tree {ft['id']} missing gates"
    
    # Validate event trees
    for i, et in enumerate(models["event_trees"]):
        if not isinstance(et, dict):
            return False, f"Event tree {i} must be a dictionary"
        if "id" not in et:
            return False, f"Event tree {i} missing id"
        if "sequences" not in et:
            return False, f"Event tree {et['id']} missing sequences"
    
    # Validate basic events
    for i, be in enumerate(models["basic_events"]):
        if not isinstance(be, dict):
            return False, f"Basic event {i} must be a dictionary"
        if "id" not in be:
            return False, f"Basic event {i} missing id"
    
    return True, "Valid"

def upgrade_schema(data: Dict[str, Any], target_version: str = SCHEMA_VERSION) -> Tuple[Dict[str, Any], bool, str]:
    """
    Upgrade a schema from an older version to a newer version.
    
    Args:
        data: The data to upgrade
        target_version: The target schema version
        
    Returns:
        tuple: (upgraded_data, success, message)
    """
    if "version" not in data:
        return data, False, "No version information in data"
    
    current_version = data["version"]
    
    if current_version == target_version:
        return data, True, "Already at target version"
    
    if current_version not in SCHEMA_VERSIONS:
        return data, False, f"Unknown source version: {current_version}"
    
    if target_version not in SCHEMA_VERSIONS:
        return data, False, f"Unknown target version: {target_version}"
    
    # Version upgrade paths
    if current_version == "1.0.0" and target_version == "1.1.0":
        return upgrade_1_0_to_1_1(data)
    elif current_version == "1.1.0" and target_version == "2.0.0":
        return upgrade_1_1_to_2_0(data)
    elif current_version == "1.0.0" and target_version == "2.0.0":
        # Two-step upgrade
        data, success, message = upgrade_1_0_to_1_1(data)
        if not success:
            return data, success, message
        return upgrade_1_1_to_2_0(data)
    else:
        return data, False, f"No upgrade path from {current_version} to {target_version}"

def upgrade_1_0_to_1_1(data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, str]:
    """Upgrade from schema version 1.0.0 to 1.1.0"""
    # Create a copy of the data
    upgraded = data.copy()
    
    # Update version
    upgraded["version"] = "1.1.0"
    upgraded["metadata"]["schema_version"] = "1.1.0"
    
    # Add attributes to each model if not present
    for model_type in ["fault_trees", "event_trees", "basic_events", "end_states"]:
        for model in upgraded["models"][model_type]:
            if "attributes" not in model:
                model["attributes"] = {}
    
    return upgraded, True, "Upgraded from 1.0.0 to 1.1.0"

def upgrade_1_1_to_2_0(data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, str]:
    """Upgrade from schema version 1.1.0 to 2.0.0"""
    # Create a copy of the latest schema
    upgraded = create_empty_schema("2.0.0")
    
    # Copy over metadata
    for key, value in data["metadata"].items():
        if key != "schema_version":  # Skip schema_version as it's already set
            upgraded["metadata"][key] = value
    
    # Copy over models
    for model_type in ["fault_trees", "event_trees", "basic_events", "end_states"]:
        upgraded["models"][model_type] = data["models"][model_type]
    
    # Initialize new models
    if "initiating_events" not in data["models"]:
        upgraded["models"]["initiating_events"] = []
    else:
        upgraded["models"]["initiating_events"] = data["models"]["initiating_events"]
    
    if "sequences" not in data["models"]:
        upgraded["models"]["sequences"] = []
    else:
        upgraded["models"]["sequences"] = data["models"]["sequences"]
    
    # Copy over analysis section if present
    if "analysis" in data:
        upgraded["analysis"] = data["analysis"]
    
    # LMP section is new in 2.0.0
    # It's already initialized in the new schema
    
    return upgraded, True, "Upgraded from 1.1.0 to 2.0.0"

def save_to_file(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save OpenPRA data to a JSON file.
    
    Args:
        data: OpenPRA data
        file_path: Path to save the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Error saving OpenPRA data to {file_path}: {str(e)}")
        return False

def load_from_file(file_path: str, auto_upgrade: bool = False) -> Tuple[Dict[str, Any], bool, str]:
    """
    Load OpenPRA data from a JSON file.
    
    Args:
        file_path: Path to the file
        auto_upgrade: Whether to automatically upgrade to the latest version
        
    Returns:
        tuple: (data, success, message)
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check if version information is present
        if "version" not in data:
            return data, False, "No version information found in file"
        
        # Validate the data
        is_valid, message = validate_schema(data)
        if not is_valid:
            if auto_upgrade and "version" in data:
                # Try to upgrade the schema
                upgraded_data, success, upgrade_message = upgrade_schema(data)
                if success:
                    logger.info(f"Auto-upgraded schema from {data['version']} to {upgraded_data['version']}")
                    return upgraded_data, True, f"Loaded and upgraded: {upgrade_message}"
                else:
                    logger.warning(f"Failed to auto-upgrade schema: {upgrade_message}")
            
            logger.warning(f"Loaded data is not valid: {message}")
            return data, False, f"Invalid schema: {message}"
        
        return data, True, "Successfully loaded"
    except Exception as e:
        logger.error(f"Error loading OpenPRA data from {file_path}: {str(e)}")
        return create_empty_schema(), False, f"Error: {str(e)}"

def create_model_from_data(source: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create an OpenPRA model from source data.
    
    Args:
        source: Source identifier
        data: Source data
        
    Returns:
        dict: Model in OpenPRA format
    """
    # This function would transform source data into OpenPRA structure
    # The implementation depends on the structure of the source data
    
    # For prototype, return a skeleton model
    model = {
        "id": source,
        "type": "fault_tree",  # or event_tree, etc.
        "name": source,
        "data": {},  # Transformed data would go here
        "attributes": {}  # New in 1.1.0
    }
    
    return model
