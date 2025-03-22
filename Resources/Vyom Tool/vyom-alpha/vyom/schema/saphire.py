"""
SAPHIRE schema definitions for parsing and validating SAPHIRE data.
"""
import os
import re
import json
import jsonschema
import logging

logger = logging.getLogger(__name__)

# SAPHIRE schema version
SCHEMA_VERSION = "1.0.0"

# Get the path to the schema file
SCHEMA_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(SCHEMA_DIR, 'saphire_schema.json')

def load_schema():
    """Load the SAPHIRE schema from file"""
    with open(SCHEMA_PATH, 'r') as f:
        return json.load(f)

# Basic SAPHIRE schema structure for in-memory use
SAPHIRE_SCHEMA = {
    "version": SCHEMA_VERSION,
    "project": {
        "name": "",
        "description": ""
    },
    "fault_trees": [],
    "event_trees": [],
    "basic_events": [],
    "end_states": [],
    "source_files": {}
}

def create_empty_schema():
    """Create an empty SAPHIRE schema."""
    return SAPHIRE_SCHEMA.copy()

def validate_schema(saphire_data):
    """
    Validate SAPHIRE data against the schema.
    
    Args:
        saphire_data: SAPHIRE data to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    try:
        schema = load_schema()
        jsonschema.validate(instance=saphire_data, schema=schema)
        return True, "Valid"
    except jsonschema.exceptions.ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error validating schema: {str(e)}"

def validate_fault_tree(fault_tree):
    """Validate a fault tree structure."""
    required_fields = ["id", "name", "gates", "basic_events"]
    
    # Check required fields
    for field in required_fields:
        if field not in fault_tree:
            return False, f"Missing required field: {field}"
    
    # Validate gates
    if "gates" in fault_tree:
        for i, gate in enumerate(fault_tree["gates"]):
            if "id" not in gate:
                return False, f"Gate {i} missing id"
            if "type" not in gate:
                return False, f"Gate {gate['id']} missing type"
            if "inputs" not in gate:
                return False, f"Gate {gate['id']} missing inputs"
            
            # Check gate type
            if gate["type"] not in ["AND", "OR", "NOT", "XOR", "NAND", "NOR", "TRAN"]:
                return False, f"Gate {gate['id']} has invalid type: {gate['type']}"
    
    return True, "Valid"

def validate_event_tree(event_tree):
    """Validate an event tree structure."""
    required_fields = ["id", "name", "initiating_event", "sequences"]
    
    # Check required fields
    for field in required_fields:
        if field not in event_tree:
            return False, f"Missing required field: {field}"
    
    # Validate sequences
    if "sequences" in event_tree:
        for i, seq in enumerate(event_tree["sequences"]):
            if "id" not in seq:
                return False, f"Sequence {i} missing id"
            if "path" not in seq:
                return False, f"Sequence {seq['id']} missing path"
            if "end_state" not in seq:
                return False, f"Sequence {seq['id']} missing end_state"
    
    return True, "Valid"

def validate_basic_event(basic_event):
    """Validate a basic event structure."""
    required_fields = ["id", "name", "probability"]
    
    # Check required fields
    for field in required_fields:
        if field not in basic_event:
            return False, f"Missing required field: {field}"
    
    # Check probability range
    if "probability" in basic_event:
        prob = basic_event["probability"]
        if not isinstance(prob, (int, float)) or prob < 0 or prob > 1:
            return False, f"Probability must be a number between 0 and 1, got: {prob}"
    
    return True, "Valid"

def parse_saphire_file(file_path, file_content):
    """
    Parse a SAPHIRE file and extract relevant data.
    
    Args:
        file_path: Path to the file
        file_content: Content of the file
        
    Returns:
        dict: Extracted data in SAPHIRE schema format
    """
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_path)[1].upper()
    
    # Handle dot-prefixed SAPHIRE files (e.g., .FTL)
    if file_name.startswith('.') and file_ext == '':
        # For files like ".FTL" where splitext doesn't work as expected
        ext = file_name.upper()  # e.g., ".FTL"
        
        # Special handling for known SAPHIRE extensions
        if ext == '.FTL':
            return parse_ftl_file(file_content)
        elif ext == '.ETL':
            return parse_etl_file(file_content)
        elif ext == '.BEI':
            return parse_bei_file(file_content)
        elif ext == '.FAD':
            return parse_fad_file(file_content)
        elif ext == '.MARD':
            return parse_mard_file(file_content)
        elif ext == '.ESD':
            return parse_esd_file(file_content)
        elif ext == '.STL':
            return parse_stl_file(file_content)
        elif ext == '.SQL':
            return parse_sql_file(file_content)
        elif ext == '.SQD':
            return parse_sqd_file(file_content)
    
    # Normal file extension handling
    if file_ext == '.BEI':
        return parse_bei_file(file_content)
    elif file_ext == '.FTL':
        return parse_ftl_file(file_content)
    elif file_ext == '.ETL':
        return parse_etl_file(file_content)
    elif file_ext == '.FAD':
        return parse_fad_file(file_content)
    elif file_ext == '.MARD':
        return parse_mard_file(file_content)
    elif file_ext == '.ESD':
        return parse_esd_file(file_content)
    elif file_ext == '.STL':
        return parse_stl_file(file_content)
    elif file_ext == '.SQL':
        return parse_sql_file(file_content)
    elif file_ext == '.SQD':
        return parse_sqd_file(file_content)
    elif file_ext == '.JSON':
        try:
            data = json.loads(file_content)
            return {
                "type": "json",
                "data": data,
                "errors": []
            }
        except json.JSONDecodeError as e:
            return {
                "type": "json",
                "data": {},
                "errors": [f"Invalid JSON: {str(e)}"]
            }
    
    # For other files, return a skeleton structure
    return {
        "type": "unknown",
        "data": {},
        "errors": [f"Unknown file type: {file_ext or file_name}"]
    }

def parse_bei_file(content):
    """Parse a BEI (Basic Event Information) file"""
    events = []
    errors = []
    
    for i, line in enumerate(content.strip().split('\n')):
        try:
            # Skip empty lines
            if not line.strip():
                continue
                
            parts = line.split(',')
            if len(parts) >= 2:
                event = {
                    "id": parts[0].strip(),
                    "probability": float(parts[1].strip()) if parts[1].strip() else 0.0
                }
                if len(parts) > 2:
                    event["name"] = parts[2].strip()
                if len(parts) > 3:
                    event["type"] = parts[3].strip()
                events.append(event)
        except Exception as e:
            errors.append(f"Error in line {i+1}: {str(e)}")
    
    return {
        "type": "basic_event_info",
        "data": {
            "basic_events": events
        },
        "errors": errors
    }

def parse_ftl_file(content):
    """Parse a FTL (Fault Tree Logic) file"""
    fault_trees = {}
    errors = []
    current_tree = None
    
    try:
        lines = content.strip().split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
                
            # Check if this is a new fault tree definition
            if line.startswith('HTGR_PRA,'):
                try:
                    # Extract the fault tree name
                    parts = line.split(',', 1)
                    if len(parts) > 1:
                        tree_name = parts[1].split('=')[0].strip()
                        current_tree = tree_name
                        # Initialize the tree if not already present
                        if current_tree not in fault_trees:
                            fault_trees[current_tree] = {
                                "gates": [],
                                "basic_events": set()
                            }
                except Exception as e:
                    errors.append(f"Error parsing fault tree header in line {i+1}: {str(e)}")
            
            # Check if this is the end of a fault tree
            elif line == '^EOS':
                current_tree = None
            
            # Parse gate definitions
            elif current_tree is not None:
                try:
                    # Split the line into parts
                    parts = line.split()
                    if len(parts) >= 2:  # Changed from 3 to 2 to handle TRAN gates
                        gate_id = parts[0]
                        gate_type = parts[1]
                        inputs = parts[2:] if len(parts) > 2 else []
                        
                        # Create the gate
                        gate = {
                            "id": gate_id,
                            "type": gate_type,
                            "inputs": inputs
                        }
                        
                        # Add the gate to the current tree
                        fault_trees[current_tree]["gates"].append(gate)
                        
                        # Add basic events to the set
                        for input_item in inputs:
                            if not input_item.startswith('G'):  # Basic events don't start with 'G'
                                fault_trees[current_tree]["basic_events"].add(input_item)
                except Exception as e:
                    errors.append(f"Error parsing gate in line {i+1}: {str(e)}")
            
            i += 1
        
        # Convert sets to lists for JSON serialization
        for tree in fault_trees.values():
            tree["basic_events"] = list(tree["basic_events"])
        
        return {
            "type": "fault_tree_logic",
            "data": {
                "fault_trees": fault_trees
            },
            "errors": errors
        }
        
    except Exception as e:
        return {
            "type": "fault_tree_logic",
            "data": {
                "fault_trees": {}
            },
            "errors": [f"Error parsing FTL file: {str(e)}"]
        }

def parse_etl_file(content):
    """Parse an ETL (Event Tree Logic) file"""
    trees = {}  # Dictionary to store multiple event trees
    errors = []
    current_tree = None
    
    try:
        logger.info("Starting ETL file parsing")
        
        # Remove BOM if present at the start of the file
        if content.startswith('\ufeff'):
            logger.debug("Removing BOM character from start of file")
            content = content[1:]
        
        # Split content by ^EOS and process each tree block
        tree_blocks = content.split('^EOS')
        logger.info(f"Found {len(tree_blocks)} blocks after splitting by ^EOS")
        
        for block_idx, block in enumerate(tree_blocks):
            if not block.strip():
                logger.debug(f"Skipping empty block {block_idx}")
                continue
                
            # Remove BOM if present at the start of the block
            if block.strip().startswith('\ufeff'):
                logger.debug(f"Removing BOM character from start of block {block_idx}")
                block = block.strip()[1:]
            
            lines = block.strip().split('\n')
            i = 0
            
            # Process the tree header - should be in the first line
            first_line = lines[0].strip() if lines else ""
            logger.debug(f"Block {block_idx} first line: {first_line[:50]}...")
            
            if first_line.startswith('HTGR_PRA,'):
                try:
                    # Extract the tree name
                    # The format is: HTGR_PRA, TREE_NAME, IE-TREE_NAME =
                    parts = first_line.split('=')[0].strip()
                    if ',' in parts:
                        tree_name = parts.split(',')[1].strip()
                        current_tree = tree_name
                        logger.info(f"Found event tree: {current_tree}")
                        # Initialize the tree
                        if current_tree not in trees:
                            trees[current_tree] = {
                                "top_events": [],
                                "sequences": [],
                                "node_descriptions": {},
                                "node_substitutions": {}
                            }
                except Exception as e:
                    logger.error(f"Error parsing event tree header in block {block_idx}: {str(e)}")
                    errors.append(f"Error parsing event tree header: {str(e)}")
                    continue
            else:
                # If not a valid tree block, skip it
                logger.debug(f"Block {block_idx} does not start with HTGR_PRA, - skipping")
                continue
            
            # Process the remaining lines in the block
            i = 1  # Start from the second line
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip empty lines
                if not line:
                    i += 1
                    continue
                
                try:
                    # Check for top events section
                    if line == '^TOPS':
                        i += 1  # Move to the next line
                        if i < len(lines):
                            tops = lines[i].strip().split(',')
                            for top in tops:
                                top = top.strip()
                                if top:  # Only add non-empty top events
                                    trees[current_tree]["top_events"].append({
                                        "id": top,
                                        "description": top
                                    })
                            logger.debug(f"Added {len(tops)} top events to {current_tree}")
                    
                    # Check for sequences section
                    elif line.startswith('^SEQUENCES'):
                        logger.debug(f"Processing SEQUENCES section for {current_tree}")
                        i += 2  # Skip the header line
                        seq_count = 0
                        while i < len(lines):
                            if i >= len(lines) or lines[i].strip().startswith('^'):
                                break
                                
                            line_content = lines[i].strip()
                            parts = line_content.split(',')
                            if len(parts) >= 4 and parts[0].strip() == 'Y':
                                seq_name = parts[1].strip()
                                end_state = parts[3].strip()
                                if seq_name:  # Only add sequences with names
                                    seq = {
                                        "id": seq_name,
                                        "end_state": end_state,
                                        "path": []  # Path will be populated from LOGIC section
                                    }
                                    trees[current_tree]["sequences"].append(seq)
                                    logger.debug(f"Added sequence {seq_name} with end state {end_state}")
                                    seq_count += 1
                            i += 1
                        logger.debug(f"Added {seq_count} sequences to {current_tree}")
                        continue  # Skip the increment at the end since we're already at the next section
                    
                    # Check for LOGIC section
                    elif line == '^LOGIC':
                        logger.debug(f"Processing LOGIC section for {current_tree}")
                        i += 1  # Move to the next line
                        logic_count = 0
                        while i < len(lines):
                            if i >= len(lines) or lines[i].strip().startswith('^'):
                                break
                                
                            line_content = lines[i].strip()
                            parts = line_content.split(',')
                            if len(parts) >= 2:
                                seq_name = parts[0].strip()
                                node_id = parts[1].strip()
                                # Find the sequence and add the node to its path
                                for seq in trees[current_tree]["sequences"]:
                                    if seq["id"] == seq_name:
                                        seq["path"].append(node_id)
                                        logic_count += 1
                                        break
                            i += 1
                        logger.debug(f"Added {logic_count} logic nodes for {current_tree}")
                        continue  # Skip the increment at the end
                    
                    # Check for NODESUBS section
                    elif line == '^NODESUBS':
                        logger.debug(f"Processing NODESUBS section for {current_tree}")
                        i += 1  # Move to the next line
                        subs_count = 0
                        while i < len(lines):
                            if i >= len(lines) or lines[i].strip().startswith('^'):
                                break
                                
                            line_content = lines[i].strip()
                            if line_content.startswith('NODEPOS'):
                                node_pos = line_content.split()[1].strip()
                                i += 1
                                if i < len(lines):
                                    subs = lines[i].strip().split('=')
                                    if len(subs) == 2:
                                        trees[current_tree]["node_substitutions"][node_pos] = {
                                            "original": subs[0].strip(),
                                            "substitute": subs[1].strip()
                                        }
                                        subs_count += 1
                            i += 1
                        logger.debug(f"Added {subs_count} node substitutions for {current_tree}")
                        continue  # Skip the increment at the end
                    
                    # Check for TEXT section
                    elif line == '^TEXT':
                        logger.debug(f"Processing TEXT section for {current_tree}")
                        i += 1  # Move to the next line
                        text_count = 0
                        while i < len(lines):
                            if i >= len(lines) or lines[i].strip().startswith('^'):
                                break
                                
                            line_content = lines[i].strip()
                            if line_content.startswith('NODEPOS'):
                                node_pos = line_content.split()[1].strip()
                                i += 1
                                if i < len(lines):
                                    desc = lines[i].strip().strip('"')
                                    trees[current_tree]["node_descriptions"][node_pos] = desc
                                    text_count += 1
                            i += 1
                        logger.debug(f"Added {text_count} node descriptions for {current_tree}")
                        continue  # Skip the increment at the end
                except Exception as e:
                    logger.error(f"Error parsing event tree content in block for {current_tree}: {str(e)}")
                    errors.append(f"Error parsing event tree content in block for {current_tree}: {str(e)}")
                
                i += 1
        
        # Log the trees found
        tree_names = list(trees.keys())
        logger.info(f"ETL parsing complete - found {len(tree_names)} event trees: {', '.join(tree_names)}")
        
        # Count end states
        end_states = set()
        for tree_name, tree_data in trees.items():
            for seq in tree_data.get("sequences", []):
                if seq.get("end_state") and seq["end_state"].strip():
                    end_states.add(seq["end_state"])
        logger.info(f"Found {len(end_states)} unique end states in ETL file: {', '.join(end_states)}")
        
        if len(tree_names) < len(tree_blocks) - 1:  # -1 because splitting by ^EOS may leave an empty element
            warning_msg = f"Warning: Expected to find {len(tree_blocks)-1} trees, but found {len(tree_names)}: {', '.join(tree_names)}"
            logger.warning(warning_msg)
            errors.append(warning_msg)
        
        return {
            "type": "event_tree_logic",
            "data": {
                "event_trees": trees
            },
            "errors": errors
        }
        
    except Exception as e:
        error_msg = f"Error parsing ETL file: {str(e)}"
        logger.error(error_msg)
        return {
            "type": "event_tree_logic",
            "data": {
                "event_trees": {}
            },
            "errors": [error_msg]
        }

def parse_fad_file(content):
    """Parse a FAD (Project Description) file"""
    project = {"name": "", "description": ""}
    errors = []
    
    try:
        lines = content.strip().split('\n')
        if lines:
            # Split by comma and filter out empty parts
            parts = [p.strip() for p in lines[0].split(',')]
            if len(parts) >= 2:
                # First part is HTGR_PRA, second part is the description
                project["name"] = parts[0].strip()  # Use first part as name
                project["description"] = parts[1].strip()  # Use second part as description
            
            logger.info(f"Found project info in FAD: {project}")
    except Exception as e:
        logger.error(f"Error parsing FAD file: {str(e)}")
        errors.append(f"Error parsing FAD file: {str(e)}")
    
    return {
        "type": "project_description",
        "data": project,
        "errors": errors
    }

def parse_mard_file(content):
    """Parse a MARD file"""
    # MARD files are typically small and act as references to other files
    return {
        "type": "mard_file",
        "data": {
            "raw_content": content,
            "description": "MARD file is a reference to PRA data"
        },
        "errors": []
    }

def parse_sql_file(content):
    """Parse an SQL (Sequence Logic) file"""
    sequences = []
    errors = []
    
    try:
        logger.info("Parsing SQL file")
        
        # Remove BOM if present at the start of the file
        if content.startswith('\ufeff'):
            logger.debug("Removing BOM character from start of file")
            content = content[1:]
        
        # Split the content by sequence end marker
        sequence_blocks = content.split('^EOS')
        logger.info(f"Found {len(sequence_blocks)} sequence blocks after splitting by ^EOS")
        
        # Process each sequence block
        for i, block in enumerate(sequence_blocks):
            if not block.strip():
                continue
                
            try:
                # First line contains the header with project, event tree, and sequence ID
                lines = block.strip().split('\n')
                if not lines:
                    continue
                    
                header = lines[0].strip()
                if not header.startswith('HTGR_PRA'):
                    continue
                    
                # Parse header - format is typically: HTGR_PRA, EVENT_TREE, SEQUENCE_ID=
                header_parts = header.split(',')
                if len(header_parts) < 3:
                    continue
                    
                event_tree = header_parts[1].strip()
                seq_id = header_parts[2].split('=')[0].strip()
                
                # The rest of the lines contain the logic
                logic_lines = [line.strip() for line in lines[1:] if line.strip()]
                logic = ' '.join(logic_lines)
                
                # Create the sequence object
                sequence = {
                    "id": seq_id,
                    "event_tree": event_tree,
                    "logic": logic
                }
                
                # Determine end state from SQD file or from the logic
                # End states are usually determined from event trees but we'll look for hints
                if '.' in logic:
                    # The last term before the period might indicate the end state
                    terms = logic.split()
                    potential_end_state = None
                    for term in reversed(terms):
                        if term != '.':
                            potential_end_state = term.strip('/')
                            break
                    
                    if potential_end_state:
                        sequence["end_state"] = potential_end_state
                
                sequences.append(sequence)
                logger.debug(f"Added sequence {seq_id} from event tree {event_tree}")
                
            except Exception as e:
                error_msg = f"Error parsing sequence block {i}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        logger.info(f"Found {len(sequences)} sequences in SQL file")
        
    except Exception as e:
        error_msg = f"Error parsing SQL file: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
    
    return {
        "type": "sequence_list",
        "data": {
            "sequences": sequences
        },
        "errors": errors
    }

def parse_sqd_file(content):
    """Parse an SQD (Sequence Description) file"""
    sequences = []
    errors = []
    
    try:
        logger.info("Parsing SQD file")
        
        # Remove BOM if present at the start of the file
        if content.startswith('\ufeff'):
            logger.debug("Removing BOM character from start of file")
            content = content[1:]
        
        lines = content.strip().split('\n')
        
        # Process the file by event tree sections
        current_event_tree = None
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Check for event tree header
            if line.startswith('HTGR_PRA,'):
                parts = line.split(',', 1)
                if len(parts) > 1:
                    current_event_tree = parts[1].split('=')[0].strip()
                    logger.debug(f"Processing sequences for event tree: {current_event_tree}")
                i += 1
                continue
            
            # Process sequence description line
            try:
                parts = line.split(',')
                if len(parts) >= 1:
                    seq_id = parts[0].strip()
                    if seq_id:
                        sequence = {
                            "id": seq_id,
                            "event_tree": current_event_tree,
                            "name": seq_id,
                            "description": parts[1].strip() if len(parts) > 1 and parts[1].strip() else f"Sequence {seq_id}"
                        }
                        
                        # Add flag set if present
                        if len(parts) > 2 and parts[2].strip():
                            sequence["flag_set"] = parts[2].strip()
                        
                        # Add project name if present
                        if len(parts) > 3 and parts[3].strip():
                            sequence["project"] = parts[3].strip()
                        
                        sequences.append(sequence)
                        logger.debug(f"Added sequence description for {seq_id} from event tree {current_event_tree}")
            except Exception as e:
                error_msg = f"Error parsing sequence description in line {i+1}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
            
            i += 1
        
        logger.info(f"Found {len(sequences)} sequences in SQD file")
        
    except Exception as e:
        error_msg = f"Error parsing SQD file: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
    
    return {
        "type": "sequence_list",
        "data": {
            "sequences": sequences
        },
        "errors": errors
    }

def parse_stl_file(content):
    """Parse an STL (Sequence List) file"""
    sequences = []
    errors = []
    
    try:
        logger.info("Parsing STL file")
        
        # Remove BOM if present at the start of the file
        if content.startswith('\ufeff'):
            logger.debug("Removing BOM character from start of file")
            content = content[1:]
        
        lines = content.strip().split('\n')
        
        # Skip header line if present
        start_idx = 0
        if lines and "HTGR_PRA=" in lines[0]:
            start_idx = 1
            logger.debug("Skipping header line")
        
        # Process sequences
        sequence_count = 0
        for i, line in enumerate(lines[start_idx:], start=start_idx):
            try:
                parts = line.strip().split(',')
                
                # Skip empty lines or malformed entries
                if not parts or not parts[0].strip():
                    continue
                    
                sequence = {
                    "id": parts[0].strip(),
                    "name": parts[0].strip(),
                    "description": parts[1].strip() if len(parts) > 1 else "",
                    "end_state": parts[2].strip() if len(parts) > 2 else ""
                }
                
                sequences.append(sequence)
                sequence_count += 1
                logger.debug(f"Added sequence: {sequence['id']}")
            except Exception as e:
                error_msg = f"Error parsing sequence in line {i+1}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        logger.info(f"Found {sequence_count} sequences in STL file")
        
    except Exception as e:
        error_msg = f"Error parsing STL file: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
    
    return {
        "type": "sequence_list",
        "data": {
            "sequences": sequences
        },
        "errors": errors
    }

def parse_esd_file(content):
    """Parse an ESD (End State Description) file"""
    end_states = []
    errors = []
    
    try:
        logger.info("Parsing ESD file")
        
        # Remove BOM if present at the start of the file
        if content.startswith('\ufeff'):
            logger.debug("Removing BOM character from start of file")
            content = content[1:]
        
        lines = content.strip().split('\n')
        
        # Skip header line if present
        start_idx = 0
        if lines and "HTGR_PRA=" in lines[0]:
            start_idx = 1
            logger.debug("Skipping header line")
        
        # Process end states
        end_state_count = 0
        for i, line in enumerate(lines[start_idx:], start=start_idx):
            try:
                parts = line.strip().split(',')
                
                # Skip empty lines or malformed entries
                if not parts or not parts[0].strip():
                    continue
                    
                end_state = {
                    "id": parts[0].strip(),
                    "name": parts[0].strip(),
                    "description": parts[1].strip() if len(parts) > 1 else "",
                }
                
                end_states.append(end_state)
                end_state_count += 1
                logger.debug(f"Added end state: {end_state['id']}")
            except Exception as e:
                error_msg = f"Error parsing end state in line {i+1}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        logger.info(f"Found {end_state_count} end states in ESD file")
        
    except Exception as e:
        error_msg = f"Error parsing ESD file: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
    
    return {
        "type": "end_state_description",
        "data": {
            "end_states": end_states
        },
        "errors": errors
    }

def generate_saphire_model(files_data):
    """
    Generate a complete SAPHIRE model from parsed files.
    
    Args:
        files_data: Dictionary of parsed file data
        
    Returns:
        dict: Complete SAPHIRE model
    """
    model = create_empty_schema()
    
    # Process project information from all sources
    project_info = {
        "name": "",
        "description": "",
        "attributes": {},
        "text": ""
    }
    
    # Process FAD file (project name and description)
    fad_files = [f for f in files_data.values() if f.get("type") == "project_description"]
    if fad_files:
        fad_data = fad_files[0].get("data", {})
        project_info["name"] = fad_data.get("name", "")
        project_info["description"] = fad_data.get("description", "")
        logger.info(f"Found project info in FAD: {fad_data}")
    
    # Process FAA file (project attributes)
    faa_files = [f for f in files_data.values() if f.get("type") == "project_attribute"]
    if faa_files:
        for file_data in faa_files:
            attributes = file_data.get("data", {}).get("attributes", [])
            for attr in attributes:
                project_info["attributes"][attr.get("name", "")] = attr.get("value", "")
        logger.info(f"Found project attributes in FAA: {project_info['attributes']}")
    
    # Process FAT file (project text)
    fat_files = [f for f in files_data.values() if f.get("type") == "project_text"]
    if fat_files:
        texts = []
        for file_data in fat_files:
            text_entries = file_data.get("data", {}).get("texts", [])
            for entry in text_entries:
                section = entry.get("section", "")
                text = entry.get("text", "")
                texts.append(f"{section}: {text}" if section else text)
        project_info["text"] = "\n\n".join(texts)
        logger.info(f"Found project text in FAT: {project_info['text']}")
    
    # Update model with combined project information
    model["project"] = project_info
    logger.info(f"Final project information: {project_info}")
    
    # Process basic events
    basic_event_files = [f for f in files_data.values() if f.get("type", "").startswith("basic_event")]
    for file_data in basic_event_files:
        process_basic_event_data(file_data, model)
    
    # Process fault trees
    fault_tree_files = [f for f in files_data.values() if f.get("type", "").startswith("fault_tree")]
    for file_data in fault_tree_files:
        process_fault_tree_data(file_data, model)
    
    # Process event trees
    event_tree_files = [f for f in files_data.values() if f.get("type", "").startswith("event_tree")]
    for file_data in event_tree_files:
        process_event_tree_data(file_data, model)
    
    # Process end states
    end_state_files = [f for f in files_data.values() if f.get("type", "").startswith("end_state")]
    for file_data in end_state_files:
        process_end_state_data(file_data, model)
    
    # Validate the model
    is_valid, message = validate_schema(model)
    if not is_valid:
        logger.warning(f"Generated model is not valid: {message}")
    
    return model
