import os
import zipfile
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import tempfile

# Comprehensive mapping of SAPHIRE file types to their categories and descriptions
SAPHIRE_FILE_TYPES = {
    # Basic Event Files
    '*.BEF': {
        'category': 'basic_event',
        'description': 'Basic event definition file',
        'required': True
    },
    '*.BEF2': {
        'category': 'basic_event',
        'description': 'Basic event definition file (alternate format)',
        'required': False
    },
    
    # Fault Tree Files
    '*.FTF': {
        'category': 'fault_tree',
        'description': 'Fault tree definition file',
        'required': True
    },
    '*.FTF2': {
        'category': 'fault_tree',
        'description': 'Fault tree definition file (alternate format)',
        'required': False
    },
    
    # Event Tree Files
    '*.ETF': {
        'category': 'event_tree',
        'description': 'Event tree definition file',
        'required': True
    },
    '*.ETF2': {
        'category': 'event_tree',
        'description': 'Event tree definition file (alternate format)',
        'required': False
    },
    
    # Sequence Files
    '*.SEF': {
        'category': 'sequence',
        'description': 'Sequence definition file',
        'required': True
    },
    '*.SEF2': {
        'category': 'sequence',
        'description': 'Sequence definition file (alternate format)',
        'required': False
    },
    
    # End State Files
    '*.ESF': {
        'category': 'end_state',
        'description': 'End state definition file',
        'required': True
    },
    '*.ESF2': {
        'category': 'end_state',
        'description': 'End state definition file (alternate format)',
        'required': False
    },
    
    # Gate Files
    '*.GAT': {
        'category': 'gate',
        'description': 'Gate definition file',
        'required': True
    },
    '*.GAT2': {
        'category': 'gate',
        'description': 'Gate definition file (alternate format)',
        'required': False
    },
    
    # Project Level Files
    '*.PRF': {
        'category': 'project',
        'description': 'Project definition file',
        'required': True
    },
    '*.PRF2': {
        'category': 'project',
        'description': 'Project definition file (alternate format)',
        'required': False
    },
    
    # Special Purpose Files
    '*.SPF': {
        'category': 'special',
        'description': 'Special purpose definition file',
        'required': False
    },
    '*.SPF2': {
        'category': 'special',
        'description': 'Special purpose definition file (alternate format)',
        'required': False
    }
} 

class SAPHIREExtractor:
    def extract_saphire_data(self, zip_path: str) -> Dict[str, Any]:
        """Extract and parse SAPHIRE data from ZIP file.
        
        Args:
            zip_path: Path to SAPHIRE ZIP file
            
        Returns:
            Dict containing parsed SAPHIRE data in schema format
        """
        try:
            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract ZIP contents
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Initialize result dictionary
                result = {
                    "version": "1.0",
                    "project": {
                        "name": "",
                        "description": "",
                        "created_date": "",
                        "modified_date": ""
                    },
                    "fault_trees": [],
                    "event_trees": [],
                    "sequences": []
                }
                
                # Process each file type
                for file_pattern, file_info in SAPHIRE_FILE_TYPES.items():
                    category = file_info['category']
                    required = file_info['required']
                    
                    # Find matching files
                    matching_files = list(Path(temp_dir).glob(file_pattern))
                    
                    if required and not matching_files:
                        raise ValueError(f"Required file type {file_pattern} not found in ZIP")
                    
                    for file_path in matching_files:
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                                
                            # Parse file based on category
                            if category == 'basic_event':
                                self._parse_basic_event(content, result)
                            elif category == 'fault_tree':
                                self._parse_fault_tree(content, result)
                            elif category == 'event_tree':
                                self._parse_event_tree(content, result)
                            elif category == 'sequence':
                                self._parse_sequence(content, result)
                            elif category == 'end_state':
                                self._parse_end_state(content, result)
                            elif category == 'gate':
                                self._parse_gate(content, result)
                            elif category == 'project':
                                self._parse_project(content, result)
                            elif category == 'special':
                                self._parse_special(content, result)
                                
                        except Exception as e:
                            logger.warning(f"Error processing {file_path}: {str(e)}")
                            continue
                
                # Validate result against schema
                self._validate_schema(result)
                
                return result
                
        except Exception as e:
            logger.error(f"Error extracting SAPHIRE data: {str(e)}")
            raise

    def _validate_schema(self, data: Dict[str, Any]) -> None:
        """Validate extracted data against SAPHIRE schema.
        
        Args:
            data: Extracted data dictionary
            
        Raises:
            ValueError: If data does not match schema
        """
        # Load schema
        schema_path = Path(__file__).parent.parent / 'schema' / 'saphire_schema.json'
        with open(schema_path) as f:
            schema = json.load(f)
            
        # Validate required fields
        required_fields = {
            'version': str,
            'project': dict,
            'fault_trees': list,
            'event_trees': list,
            'sequences': list
        }
        
        for field, field_type in required_fields.items():
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(data[field], field_type):
                raise ValueError(f"Invalid type for {field}: expected {field_type}")
                
        # Validate project fields
        project_fields = {'name', 'description', 'created_date', 'modified_date'}
        for field in project_fields:
            if field not in data['project']:
                raise ValueError(f"Missing required project field: {field}")
                
        # Validate fault trees
        for ft in data['fault_trees']:
            required_ft_fields = {'id', 'name', 'description', 'gates', 'basic_events'}
            for field in required_ft_fields:
                if field not in ft:
                    raise ValueError(f"Missing required fault tree field: {field}")
                    
        # Validate event trees
        for et in data['event_trees']:
            required_et_fields = {'id', 'name', 'description', 'sequences', 'end_states'}
            for field in required_et_fields:
                if field not in et:
                    raise ValueError(f"Missing required event tree field: {field}")
                    
        # Validate sequences
        for seq in data['sequences']:
            required_seq_fields = {'id', 'name', 'description', 'fault_trees', 'gates'}
            for field in required_seq_fields:
                if field not in seq:
                    raise ValueError(f"Missing required sequence field: {field}") 

    def _parse_basic_event(self, content: str, result: Dict[str, Any]) -> None:
        """Parse basic event file content.
        
        Args:
            content: File content
            result: Result dictionary to update
        """
        # Basic event format:
        # ID, Name, Description, Probability, Uncertainty
        lines = content.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue
            parts = line.split(',')
            if len(parts) >= 5:
                event = {
                    'id': parts[0].strip(),
                    'name': parts[1].strip(),
                    'description': parts[2].strip(),
                    'probability': float(parts[3]),
                    'uncertainty': float(parts[4])
                }
                # Add to appropriate fault trees
                for ft in result['fault_trees']:
                    if event['id'] in ft['basic_events']:
                        ft['basic_events'][event['id']] = event

    def _parse_fault_tree(self, content: str, result: Dict[str, Any]) -> None:
        """Parse fault tree file content.
        
        Args:
            content: File content
            result: Result dictionary to update
        """
        # Fault tree format:
        # ID, Name, Description, Gate IDs
        lines = content.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue
            parts = line.split(',')
            if len(parts) >= 4:
                ft = {
                    'id': parts[0].strip(),
                    'name': parts[1].strip(),
                    'description': parts[2].strip(),
                    'gates': [g.strip() for g in parts[3:]],
                    'basic_events': {}
                }
                result['fault_trees'].append(ft)

    def _parse_event_tree(self, content: str, result: Dict[str, Any]) -> None:
        """Parse event tree file content.
        
        Args:
            content: File content
            result: Result dictionary to update
        """
        # Event tree format:
        # ID, Name, Description, Sequence IDs, End State IDs
        lines = content.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue
            parts = line.split(',')
            if len(parts) >= 5:
                et = {
                    'id': parts[0].strip(),
                    'name': parts[1].strip(),
                    'description': parts[2].strip(),
                    'sequences': [s.strip() for s in parts[3].split()],
                    'end_states': [e.strip() for e in parts[4].split()]
                }
                result['event_trees'].append(et)

    def _parse_sequence(self, content: str, result: Dict[str, Any]) -> None:
        """Parse sequence file content.
        
        Args:
            content: File content
            result: Result dictionary to update
        """
        # Sequence format:
        # ID, Name, Description, Fault Tree IDs, Gate IDs
        lines = content.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue
            parts = line.split(',')
            if len(parts) >= 5:
                seq = {
                    'id': parts[0].strip(),
                    'name': parts[1].strip(),
                    'description': parts[2].strip(),
                    'fault_trees': [ft.strip() for ft in parts[3].split()],
                    'gates': [g.strip() for g in parts[4].split()]
                }
                result['sequences'].append(seq)

    def _parse_end_state(self, content: str, result: Dict[str, Any]) -> None:
        """Parse end state file content.
        
        Args:
            content: File content
            result: Result dictionary to update
        """
        # End state format:
        # ID, Name, Description, Category
        lines = content.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue
            parts = line.split(',')
            if len(parts) >= 4:
                end_state = {
                    'id': parts[0].strip(),
                    'name': parts[1].strip(),
                    'description': parts[2].strip(),
                    'category': parts[3].strip()
                }
                # Add to appropriate event trees
                for et in result['event_trees']:
                    if end_state['id'] in et['end_states']:
                        if 'end_state_details' not in et:
                            et['end_state_details'] = {}
                        et['end_state_details'][end_state['id']] = end_state

    def _parse_gate(self, content: str, result: Dict[str, Any]) -> None:
        """Parse gate file content.
        
        Args:
            content: File content
            result: Result dictionary to update
        """
        # Gate format:
        # ID, Name, Description, Type, Input IDs
        lines = content.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue
            parts = line.split(',')
            if len(parts) >= 5:
                gate = {
                    'id': parts[0].strip(),
                    'name': parts[1].strip(),
                    'description': parts[2].strip(),
                    'type': parts[3].strip(),
                    'inputs': [i.strip() for i in parts[4:]]
                }
                # Add to appropriate fault trees
                for ft in result['fault_trees']:
                    if gate['id'] in ft['gates']:
                        if 'gate_details' not in ft:
                            ft['gate_details'] = {}
                        ft['gate_details'][gate['id']] = gate

    def _parse_project(self, content: str, result: Dict[str, Any]) -> None:
        """Parse project file content.
        
        Args:
            content: File content
            result: Result dictionary to update
        """
        # Project format:
        # Name, Description, Created Date, Modified Date
        lines = content.strip().split('\n')
        if lines:
            parts = lines[0].split(',')
            if len(parts) >= 4:
                result['project'].update({
                    'name': parts[0].strip(),
                    'description': parts[1].strip(),
                    'created_date': parts[2].strip(),
                    'modified_date': parts[3].strip()
                })

    def _parse_special(self, content: str, result: Dict[str, Any]) -> None:
        """Parse special purpose file content.
        
        Args:
            content: File content
            result: Result dictionary to update
        """
        # Special purpose format is implementation specific
        # Store raw content for future processing
        if 'special_purpose' not in result:
            result['special_purpose'] = []
        result['special_purpose'].append(content) 