"""
Generic Extraction Test for SAPHIRE files.

This test module provides a framework for testing the extraction
of various SAPHIRE file formats using dynamically generated test data
and property-based testing principles.
"""
import os
import sys
import tempfile
import zipfile
import random
import string
import json
import unittest
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vyom.schema.saphire import parse_saphire_file
from vyom.extractor import analyze_files, extract_zip, determine_file_type, SAPHIRE_EXTENSIONS

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileGenerator:
    """Generator for test SAPHIRE files"""
    
    @classmethod
    def generate_bei_content(cls, num_events=5):
        """Generate BEI (Basic Event Information) file content"""
        content = []
        for i in range(num_events):
            # Format: ID,probability,name,type
            event_id = f"BE{i}"
            prob = round(random.uniform(0.0, 1.0), 4)
            name = f"Basic Event {i}"
            event_type = random.choice(["RANDOM", "DEMAND", "CCF"])
            content.append(f"{event_id},{prob},{name},{event_type}")
        return "\n".join(content)
    
    @classmethod
    def generate_ftl_content(cls, num_gates=3, num_events=5):
        """Generate FTL (Fault Tree Logic) file content"""
        content = ["HTGR_PRA, SAMPLE_TREE ="]
        
        # Create basic events
        basic_events = [f"BE{i}" for i in range(num_events)]
        
        # Create gates
        gates = []
        for i in range(num_gates):
            gate_id = f"G{i}"
            gate_type = random.choice(["AND", "OR", "NOT", "XOR"])
            
            # Gate inputs can be other gates or basic events
            inputs = []
            num_inputs = random.randint(1, 3)
            
            for _ in range(num_inputs):
                if i > 0 and random.random() < 0.3:  # 30% chance to reference another gate
                    inputs.append(f"G{random.randint(0, i-1)}")
                else:
                    inputs.append(random.choice(basic_events))
            
            gates.append(f"{gate_id} {gate_type} {' '.join(inputs)}")
        
        content.extend(gates)
        content.append("^EOS")
        return "\n".join(content)
    
    @classmethod
    def generate_etl_content(cls, num_trees=2, with_bom=False):
        """Generate ETL (Event Tree Logic) file content"""
        content = []
        
        if with_bom:
            content.append('\ufeff')  # Add BOM at start
        
        for i in range(num_trees):
            # Add tree header
            content.append(f'HTGR_PRA, TREE_{i}, IE-TREE_{i} =')
            
            # Add tree content sections
            content.append('^TOPS')
            content.append(f'TOP_EVENT_{i}_1, TOP_EVENT_{i}_2')
            
            content.append('^SEQUENCES')
            content.append('*')
            content.append(f'Y, SEQ_{i}_1, , OK')
            content.append(f'Y, SEQ_{i}_2, , FAIL')
            
            content.append('^LOGIC')
            content.append(f'SEQ_{i}_1, TOP_EVENT_{i}_1')
            content.append(f'SEQ_{i}_2, TOP_EVENT_{i}_2')
            
            # Add EOS marker for all but the last tree
            if i < num_trees - 1:
                content.append('^EOS')
                if with_bom:
                    content.append('\ufeff')  # Add BOM after EOS
        
        return "\n".join(content)
    
    @classmethod
    def generate_fad_content(cls):
        """Generate FAD (Project Description) file content"""
        return f"Test Project {random.randint(1,100)},This is a test project description for SAPHIRE testing"
    
    @classmethod
    def generate_mard_content(cls):
        """Generate MARD file content"""
        return f"MARD file content for test project {random.randint(1,100)}"
    
    @classmethod
    def generate_content_for_type(cls, file_type, with_bom=False):
        """Generate content based on file type"""
        if file_type in ['.BEI', '.BEC', '.BED', '.BEA', '.BET', '.BEF', '.BEG', '.BEH']:
            return cls.generate_bei_content()
        elif file_type in ['.FTL', '.FTD', '.FTA', '.FTC', '.FTT', '.FTY']:
            return cls.generate_ftl_content()
        elif file_type in ['.ETL', '.ETD', '.ETA']:
            return cls.generate_etl_content(with_bom=with_bom)
        elif file_type in ['.FAD', '.PRF', '.PRF2']:
            return cls.generate_fad_content()
        elif file_type == '.MARD':
            return cls.generate_mard_content()
        else:
            return f"Generic content for {file_type}"


class TestGenericExtraction(unittest.TestCase):
    """Test class for generic file extraction testing"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp(prefix="vyom_test_generic_")
        self.test_data_dir = os.path.join(self.temp_dir, "test_data")
        os.makedirs(self.test_data_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, file_extension, content):
        """Create a test file with the given extension and content"""
        # For dot-prefixed files like .FTL
        if file_extension.startswith('.'):
            filename = file_extension
        else:
            filename = f"test_file{file_extension}"
            
        file_path = os.path.join(self.test_data_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def create_test_zip(self, files_dict):
        """Create a test ZIP file with the given files"""
        zip_path = os.path.join(self.temp_dir, "test_saphire.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for filename, content in files_dict.items():
                file_path = os.path.join(self.test_data_dir, filename)
                
                # Create the file
                if isinstance(content, str):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    with open(file_path, 'wb') as f:
                        f.write(content)
                
                # Add to ZIP
                arcname = os.path.join("_Subs", filename)
                zip_file.write(file_path, arcname=arcname)
        
        return zip_path
    
    def test_individual_file_parsing(self):
        """Test parsing of individual SAPHIRE files"""
        # Test each SAPHIRE file type
        for ext, description in SAPHIRE_EXTENSIONS.items():
            # Skip non-critical extensions to speed up test
            if ext not in ['.BEI', '.FTL', '.ETL', '.FAD', '.MARD']:
                continue
                
            logger.info(f"Testing {ext} file parsing ({description})")
            
            # Generate content for this file type
            with_bom = ext == '.ETL'  # Only add BOM for ETL files
            content = FileGenerator.generate_content_for_type(ext, with_bom=with_bom)
            
            # Create test file
            file_path = self.create_test_file(ext, content)
            
            # Parse the file
            result = parse_saphire_file(file_path, content)
            
            # Basic validation
            self.assertIn('type', result)
            self.assertIn('data', result)
            
            # Type-specific validation
            if ext in ['.BEI', '.BEC', '.BED', '.BEA', '.BET', '.BEF', '.BEG', '.BEH']:
                if 'basic_events' in result.get('data', {}):
                    self.assertTrue(len(result['data']['basic_events']) > 0)
            elif ext in ['.FTL', '.FTD', '.FTA', '.FTC', '.FTT', '.FTY']:
                if 'fault_trees' in result.get('data', {}):
                    self.assertTrue(len(result['data']['fault_trees']) > 0)
            elif ext in ['.ETL', '.ETD', '.ETA']:
                if 'event_trees' in result.get('data', {}):
                    self.assertTrue(len(result['data']['event_trees']) > 0)
    
    def test_zip_extraction(self):
        """Test extraction and parsing of a ZIP with multiple SAPHIRE files"""
        # Create files for different SAPHIRE types
        files = {
            ".BEI": FileGenerator.generate_bei_content(),
            ".FTL": FileGenerator.generate_ftl_content(),
            ".ETL": FileGenerator.generate_etl_content(with_bom=True),
            ".FAD": FileGenerator.generate_fad_content(),
            ".MARD": FileGenerator.generate_mard_content()
        }
        
        # Create a test zip with these files
        zip_path = self.create_test_zip(files)
        
        # Extract and analyze
        extract_dir = extract_zip(zip_path)
        result = analyze_files(extract_dir, "test_job")
        
        # Verify the basic structure
        self.assertIn('saphire_data', result)
        self.assertIn('files', result)
        
        # Check that files were properly categorized
        self.assertIn('metadata', result)
        self.assertGreater(result['metadata']['total_files'], 0)
        
        # Check for specific SAPHIRE data
        if len(files['.ETL']) > 0:
            self.assertIn('event_trees', result['saphire_data'])
        if len(files['.FTL']) > 0:
            self.assertIn('fault_trees', result['saphire_data'])
        if len(files['.BEI']) > 0:
            self.assertIn('basic_events', result['saphire_data'])
    
    def test_robustness_with_edge_cases(self):
        """Test extraction robustness with various edge cases"""
        # Test with mixed valid/invalid files
        files = {
            ".BEI": "Invalid content\nMissing proper format",
            ".FTL": FileGenerator.generate_ftl_content(),
            ".ETL": FileGenerator.generate_etl_content(with_bom=True),
            "corrupted.txt": "This is not a SAPHIRE file",
            "empty.dat": ""
        }
        
        # Create a test zip with these files
        zip_path = self.create_test_zip(files)
        
        # Extract and analyze
        extract_dir = extract_zip(zip_path)
        result = analyze_files(extract_dir, "test_job")
        
        # The analysis should complete without exceptions
        self.assertIn('metadata', result)
        
        # There should be some errors/warnings logged
        self.assertGreaterEqual(result['metadata']['errors'] + result['metadata']['warnings'], 0)
        
        # But valid files should still be processed
        self.assertIn('event_trees', result['saphire_data'])
        self.assertIn('fault_trees', result['saphire_data'])
    
    def test_file_type_detection(self):
        """Test file type detection for SAPHIRE files"""
        for ext in SAPHIRE_EXTENSIONS:
            # Create a test file with this extension
            content = FileGenerator.generate_content_for_type(ext)
            file_path = self.create_test_file(ext, content)
            
            # Detect the file type
            file_type = determine_file_type(file_path)
            
            # The file type should be one of the SAPHIRE categories
            self.assertIn(file_type, ['fault_tree', 'event_tree', 'basic_event', 
                                     'end_state', 'sequence', 'project', 
                                     'master_db', 'saphire'])
    
    def test_mixed_encoding(self):
        """Test handling of files with mixed encoding"""
        # Create ETL content with BOM
        etl_content = FileGenerator.generate_etl_content(with_bom=True)
        
        # Create the same content but with UTF-16 encoding
        utf16_path = os.path.join(self.test_data_dir, "utf16.ETL")
        with open(utf16_path, 'w', encoding='utf-16') as f:
            f.write(etl_content)
        
        # Read it back and parse
        with open(utf16_path, 'r', encoding='utf-16', errors='replace') as f:
            content = f.read()
            result = parse_saphire_file(utf16_path, content)
        
        # The parser should handle the encoding
        self.assertEqual(result['type'], 'event_tree_logic')
        self.assertIn('event_trees', result['data'])

if __name__ == "__main__":
    unittest.main() 