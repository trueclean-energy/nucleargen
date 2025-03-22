"""
Extractor module for Vyom.
"""
import os
import json
import shutil
import tempfile
import zipfile
import logging
import re
from typing import Dict, List, Any, Optional, Tuple

from vyom.schema.saphire import parse_saphire_file, generate_saphire_model

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define SAPHIRE file extensions
SAPHIRE_EXTENSIONS = {
    '.BEI': 'Basic Event Information',
    '.FTL': 'Fault Tree Logic',
    '.ETL': 'Event Tree Logic',
    '.FAD': 'Project Description',
    '.MARD': 'Master Relational Database',
    '.GDL': 'Graphical Description',
    '.IDX': 'Index',
    '.BEC': 'Basic Event Category',
    '.BED': 'Basic Event Description',
    '.BEA': 'Basic Event Attribute',
    '.BET': 'Basic Event Type',
    '.BEF': 'Basic Event Failure',
    '.BEG': 'Basic Event Group',
    '.BEH': 'Basic Event Hazard',
    '.ESL': 'End State List',
    '.ESD': 'End State Description',
    '.ESA': 'End State Attribute',
    '.ESC': 'End State Cut Set',
    '.ESI': 'End State Information',
    '.STL': 'Sequence List',
    '.STD': 'Sequence Description',
    '.STA': 'Sequence Attribute',
    '.SQL': 'Sequence Logic',
    '.SQD': 'Sequence Description',
    '.SQC': 'Sequence Cut Set',
    '.SQP': 'Sequence Probability',
    '.SQY': 'Sequence Uncertainty',
    '.SQA': 'Sequence Attribute',
    '.FTD': 'Fault Tree Description',
    '.FTA': 'Fault Tree Attribute',
    '.FTC': 'Fault Tree Components',
    '.FTT': 'Fault Tree Types',
    '.FTY': 'Fault Tree System',
    '.ETD': 'Event Tree Description',
    '.ETA': 'Event Tree Attribute',
    '.EGI': 'Event Group Information',
    '.EGD': 'Event Group Description',
    '.PHD': 'Project Header Description',
    '.HID': 'Header ID',
    '.FAU': 'Family Attribute Uncertainty',
    '.MTD': 'Model Type Description',
    '.FAA': 'Family Attribute Additional',
    '.FAT': 'Family Attribute Type'
}

def extract_zip(zip_path: str, output_dir: Optional[str] = None) -> str:
    """
    Extract a ZIP file to a directory.
    
    Args:
        zip_path: Path to the ZIP file
        output_dir: Output directory. If None, a temporary directory is created
        
    Returns:
        str: Path to the directory containing the extracted files
    """
    # Create a temporary directory if output_dir is not specified
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix='vyom_extract_')
    
    logger.info(f"Extracting {zip_path} to {output_dir}")
    
    # Extract the files
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # First, extract all files
        zip_ref.extractall(output_dir)
    
    return output_dir

def analyze_files(directory: str, job_id: str) -> Dict[str, Any]:
    """
    Analyze files in a directory and build a schema representation.
    
    Args:
        directory: Directory containing the files
        job_id: Job ID
        
    Returns:
        Dict[str, Any]: Schema representation of the files
    """
    # Initialize the schema
    schema = {
        "job_id": job_id,
        "files": {},
        "metadata": {
            "total_files": 0,
            "errors": 0,
            "warnings": 0
        },
        "saphire_data": {
            "fault_trees": [],
            "event_trees": [],
            "basic_events": [],
            "end_states": [],
            "sequences": [],
            "project": {}
        }
    }
    
    # Process all files
    total_files = 0
    errors = 0
    warnings = 0
    
    logger.info(f"Starting analysis of directory: {directory}")
    
    for root, _, files in os.walk(directory):
        logger.info(f"Processing directory: {root} with {len(files)} files")
        for file in files:
            # Skip macOS metadata files
            if file.startswith('._') or file == '.DS_Store' or '/__MACOSX/' in root:
                continue
                
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, directory)
            
            try:
                # Get file type
                file_type = determine_file_type(file_path)
                logger.info(f"Processing file: {rel_path} (type: {file_type})")
                
                # Process file based on type
                if file_type in ['fault_tree', 'event_tree', 'basic_event', 'end_state', 'sequence', 'project', 'master_db']:
                    logger.info(f"Reading SAPHIRE file: {rel_path}")
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                            parsed_data = parse_saphire_file(file_path, content)
                            
                            # Add data to appropriate category
                            if file_type == 'fault_tree':
                                logger.info(f"Adding fault tree data from {rel_path}")
                                if parsed_data['type'] == 'fault_tree_logic' and 'fault_trees' in parsed_data.get('data', {}):
                                    # Convert each fault tree in the dictionary to a proper fault tree object
                                    for tree_name, tree_data in parsed_data['data']['fault_trees'].items():
                                        fault_tree = {
                                            'id': tree_name,
                                            'name': tree_name,
                                            'gates': tree_data.get('gates', []),
                                            'basic_events': tree_data.get('basic_events', [])
                                        }
                                        schema['saphire_data']['fault_trees'].append(fault_tree)
                                else:
                                    schema['saphire_data']['fault_trees'].append(parsed_data)
                            elif file_type == 'event_tree':
                                logger.info(f"Adding event tree data from {rel_path}")
                                if parsed_data['type'] == 'event_tree_logic' and 'event_trees' in parsed_data.get('data', {}):
                                    # Extract end states from event tree sequences
                                    end_states_set = set()
                                    
                                    # Convert each event tree in the dictionary to a proper event tree object
                                    for tree_name, tree_data in parsed_data['data']['event_trees'].items():
                                        # Skip entries without a valid name
                                        if not tree_name or tree_name.lower() == 'unknown':
                                            logger.warning(f"Skipping event tree with invalid name: {tree_name}")
                                            continue
                                            
                                        event_tree = {
                                            'id': tree_name,
                                            'name': tree_name,
                                            'top_events': tree_data.get('top_events', []),
                                            'sequences': tree_data.get('sequences', []),
                                            'node_descriptions': tree_data.get('node_descriptions', {}),
                                            'node_substitutions': tree_data.get('node_substitutions', {})
                                        }
                                        
                                        # Collect end states from sequences
                                        for sequence in tree_data.get('sequences', []):
                                            end_state = sequence.get('end_state')
                                            if end_state and end_state.strip():
                                                end_states_set.add(end_state.strip())
                                                
                                        schema['saphire_data']['event_trees'].append(event_tree)
                                    
                                    # Add end states to the schema
                                    logger.info(f"Found {len(end_states_set)} end states in {rel_path}")
                                    for end_state in end_states_set:
                                        if not any(es.get('id') == end_state for es in schema['saphire_data']['end_states']):
                                            schema['saphire_data']['end_states'].append({
                                                'id': end_state,
                                                'name': end_state,
                                                'description': f"End state {end_state}"
                                            })
                                            logger.info(f"Added end state: {end_state}")
                                elif parsed_data.get('name') and parsed_data.get('name').lower() != 'unknown':
                                    # Only add other event tree objects if they have valid names
                                    schema['saphire_data']['event_trees'].append(parsed_data)
                                else:
                                    logger.warning(f"Skipping event tree data without valid structure or name from {rel_path}")
                            elif file_type == 'basic_event':
                                # For BEI files that contain basic event info
                                if parsed_data['type'] == 'basic_event_info' and 'basic_events' in parsed_data.get('data', {}):
                                    basic_events = parsed_data['data']['basic_events']
                                    logger.info(f"Adding {len(basic_events)} basic events from {rel_path}")
                                    for event in basic_events:
                                        schema['saphire_data']['basic_events'].append({
                                            'id': event['id'],
                                            'name': event.get('name', event['id']),
                                            'probability': event.get('probability', 0.0),
                                            'description': event.get('name', '')
                                        })
                                else:
                                    schema['saphire_data']['basic_events'].append(parsed_data)
                            elif file_type == 'end_state':
                                logger.info(f"Adding end state data from {rel_path}")
                                if parsed_data['type'] == 'end_state_description' and 'end_states' in parsed_data.get('data', {}):
                                    end_states = parsed_data['data']['end_states']
                                    logger.info(f"Adding {len(end_states)} end states from {rel_path}")
                                    for end_state in end_states:
                                        # Skip if already exists
                                        if not any(es.get('id') == end_state['id'] for es in schema['saphire_data']['end_states']):
                                            schema['saphire_data']['end_states'].append({
                                                'id': end_state['id'],
                                                'name': end_state.get('name', end_state['id']),
                                                'description': end_state.get('description', '')
                                            })
                                            logger.info(f"Added end state: {end_state['id']}")
                                elif parsed_data.get('data') and isinstance(parsed_data['data'], dict):
                                    for es_id, es_data in parsed_data['data'].items():
                                        if not any(es.get('id') == es_id for es in schema['saphire_data']['end_states']):
                                            schema['saphire_data']['end_states'].append({
                                                'id': es_id,
                                                'name': es_data.get('name', es_id),
                                                'description': es_data.get('description', f"End state {es_id}")
                                            })
                                            logger.info(f"Added end state: {es_id}")
                                else:
                                    schema['saphire_data']['end_states'].append(parsed_data)
                            elif file_type == 'sequence':
                                logger.info(f"Adding sequence data from {rel_path}")
                                if parsed_data['type'] == 'sequence_list' and 'sequences' in parsed_data.get('data', {}):
                                    sequences = parsed_data['data']['sequences']
                                    logger.info(f"Adding {len(sequences)} sequences from {rel_path}")
                                    for sequence in sequences:
                                        # Skip if already exists
                                        if not any(s.get('id') == sequence['id'] for s in schema['saphire_data']['sequences']):
                                            schema['saphire_data']['sequences'].append({
                                                'id': sequence['id'],
                                                'name': sequence.get('name', sequence['id']),
                                                'description': sequence.get('description', ''),
                                                'end_state': sequence.get('end_state', '')
                                            })
                                            logger.info(f"Added sequence: {sequence['id']}")
                                elif parsed_data.get('data') and isinstance(parsed_data['data'], dict):
                                    for seq_id, seq_data in parsed_data['data'].items():
                                        if not any(s.get('id') == seq_id for s in schema['saphire_data']['sequences']):
                                            schema['saphire_data']['sequences'].append({
                                                'id': seq_id,
                                                'name': seq_data.get('name', seq_id),
                                                'description': seq_data.get('description', ''),
                                                'end_state': seq_data.get('end_state', '')
                                            })
                                            logger.info(f"Added sequence: {seq_id}")
                                else:
                                    schema['saphire_data']['sequences'].append(parsed_data)
                            elif file_type == 'project':
                                schema['saphire_data']['project'].update(parsed_data)
                    except UnicodeDecodeError:
                        logger.warning(f"Could not decode {file_path} as text, skipping")
                        warnings += 1
                
                # Store file info
                schema['files'][rel_path] = {
                    'type': file_type,
                    'size': os.path.getsize(file_path),
                    'path': rel_path
                }
                
                total_files += 1
                
            except Exception as e:
                errors += 1
                logger.error(f"Error processing {file_path}: {str(e)}")
                continue
    
    # Update metadata
    schema['metadata']['total_files'] = total_files
    schema['metadata']['errors'] = errors
    schema['metadata']['warnings'] = warnings
    
    # Log summary
    logger.info(f"Analysis complete. Processed {total_files} files.")
    logger.info(f"Found {len(schema['saphire_data']['fault_trees'])} fault trees")
    logger.info(f"Found {len(schema['saphire_data']['event_trees'])} event trees")
    logger.info(f"Found {len(schema['saphire_data']['basic_events'])} basic events")
    logger.info(f"Found {len(schema['saphire_data']['end_states'])} end states")
    logger.info(f"Found {len(schema['saphire_data']['sequences'])} sequences")
    
    return schema

def determine_file_type(file_path: str) -> str:
    """
    Determine the file type based on its extension and content.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: File type
    """
    # Get the file extension
    file_name = os.path.basename(file_path)
    _, ext = os.path.splitext(file_path)
    ext = ext.upper()
    
    # Handle special case for dot-prefixed files (like .FTL)
    if file_name.startswith('.') and ext == '':
        ext = f".{file_name[1:].upper()}"
        logger.info(f"Detected dot-prefixed file: {file_path}, using extension: {ext}")
    
    logger.info(f"Checking file type for {file_path} (extension: {ext})")
    
    # Check for SAPHIRE files first
    if ext in SAPHIRE_EXTENSIONS:
        logger.info(f"Found SAPHIRE file: {file_path} ({SAPHIRE_EXTENSIONS[ext]})")
        # Map SAPHIRE extensions to categories
        if ext in ['.FTL', '.FTD', '.FTA', '.FTC', '.FTT', '.FTY']:
            logger.info(f"Identified as fault tree: {file_path}")
            return 'fault_tree'
        elif ext in ['.ETL', '.ETD', '.ETA']:
            logger.info(f"Identified as event tree: {file_path}")
            return 'event_tree'
        elif ext in ['.BEI', '.BEC', '.BED', '.BEA', '.BET', '.BEF', '.BEG', '.BEH']:
            logger.info(f"Identified as basic event: {file_path}")
            return 'basic_event'
        elif ext in ['.ESL', '.ESD', '.ESA', '.ESC', '.ESI']:
            logger.info(f"Identified as end state: {file_path}")
            return 'end_state'
        elif ext in ['.STL', '.STD', '.STA', '.SQL', '.SQD', '.SQC', '.SQP', '.SQY', '.SQA']:
            logger.info(f"Identified as sequence: {file_path}")
            return 'sequence'
        elif ext in ['.FAD', '.PRF', '.PRF2', '.PHD', '.HID', '.MTD', '.FAA', '.FAT', '.FAU']:
            logger.info(f"Identified as project: {file_path}")
            return 'project'
        elif ext in ['.MARD', '.EGI', '.EGD']:
            logger.info(f"Identified as master_db: {file_path}")
            return 'master_db'
        else:
            logger.info(f"Identified as generic saphire: {file_path}")
            return 'saphire'
    
    # Common text file extensions
    text_extensions = ['.txt', '.md', '.csv', '.log']
    # Common JSON file extensions
    json_extensions = ['.json']
    # Common binary file extensions
    binary_extensions = ['.zip', '.gz', '.tar', '.bin', '.exe']
    
    logger.info(f"Not found in SAPHIRE_EXTENSIONS dict. Checking other file types: {file_path}")
    
    # Check for text files
    if ext.lower() in text_extensions:
        logger.info(f"Identified as text file: {file_path}")
        return "text"
    # Check for JSON files
    elif ext.lower() in json_extensions:
        logger.info(f"Identified as JSON file: {file_path}")
        return "json"
    # Check for binary files
    elif ext.lower() in binary_extensions:
        logger.info(f"Identified as binary file: {file_path}")
        return "binary"
    
    # Default to text for unrecognized extensions
    logger.info(f"Unrecognized extension, defaulting to text: {file_path} (ext: {ext})")
    return "text"
