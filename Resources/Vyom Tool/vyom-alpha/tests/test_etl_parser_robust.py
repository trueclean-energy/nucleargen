"""
Test SAPHIRE ETL parser with robust techniques.

This test module uses property-based testing approaches to verify the robustness
of the ETL parser in handling various file formats and edge cases.
"""
import os
import sys
import tempfile
import zipfile
import random
import string
import io
import json
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vyom.schema.saphire import parse_etl_file
from vyom.extractor import analyze_files, extract_zip

class TestETLParserRobust(unittest.TestCase):
    """Test class for robust ETL parser testing"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp(prefix="vyom_test_etl_")
        self.test_data_dir = os.path.join(self.temp_dir, "test_data")
        os.makedirs(self.test_data_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def generate_minimal_etl(self, num_trees=2, with_bom=False, corrupted=False):
        """Generate a minimal ETL file with the specified number of trees"""
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
        
        # Introduce corruption if requested
        if corrupted:
            # Randomly corrupt some section
            corrupt_index = random.randint(1, len(content) - 1)
            if '^' in content[corrupt_index]:
                # Corrupt a section marker
                content[corrupt_index] = content[corrupt_index].replace('^', '&')
            else:
                # Corrupt a content line
                content[corrupt_index] = '<<<CORRUPTED>>>'
        
        return '\n'.join(content)
    
    def create_test_etl_file(self, content, filename=".ETL"):
        """Create a test ETL file with the given content"""
        file_path = os.path.join(self.test_data_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def create_test_zip(self, files_dict):
        """Create a test ZIP file with the given files"""
        zip_path = os.path.join(self.temp_dir, "test_etl.zip")
        
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
    
    def test_basic_etl_parsing(self):
        """Test basic ETL parsing with minimal content"""
        etl_content = self.generate_minimal_etl(num_trees=3)
        result = parse_etl_file(etl_content)
        
        self.assertEqual(result['type'], 'event_tree_logic')
        self.assertIn('event_trees', result['data'])
        self.assertEqual(len(result['data']['event_trees']), 3)
        
        # Check that each tree has the expected structure
        for i in range(3):
            tree_name = f'TREE_{i}'
            self.assertIn(tree_name, result['data']['event_trees'])
            tree = result['data']['event_trees'][tree_name]
            
            self.assertIn('top_events', tree)
            self.assertIn('sequences', tree)
            self.assertEqual(len(tree['sequences']), 2)
    
    def test_bom_handling(self):
        """Test ETL parsing with BOM characters"""
        etl_content = self.generate_minimal_etl(num_trees=3, with_bom=True)
        result = parse_etl_file(etl_content)
        
        self.assertEqual(result['type'], 'event_tree_logic')
        self.assertIn('event_trees', result['data'])
        self.assertEqual(len(result['data']['event_trees']), 3)
    
    def test_error_handling(self):
        """Test ETL parser error handling with corrupted files"""
        etl_content = self.generate_minimal_etl(num_trees=3, corrupted=True)
        result = parse_etl_file(etl_content)
        
        # Parser should still return a result with the type
        self.assertEqual(result['type'], 'event_tree_logic')
        self.assertIn('event_trees', result['data'])
        
        # The parser should have logged errors
        self.assertTrue(len(result['errors']) > 0)
    
    def test_empty_file(self):
        """Test ETL parser with empty file"""
        result = parse_etl_file("")
        
        # Parser should handle empty files without crashing
        self.assertEqual(result['type'], 'event_tree_logic')
        self.assertIn('event_trees', result['data'])
        self.assertEqual(len(result['data']['event_trees']), 0)
        self.assertTrue(len(result['errors']) > 0)
    
    def test_fuzz_etl_parser(self):
        """Fuzz test the ETL parser with randomly generated content"""
        # Generate multiple random ETL files with various issues
        for _ in range(5):
            # Generate random content with some SAPHIRE-like structure
            lines = []
            
            # Randomly decide if it has a BOM
            if random.choice([True, False]):
                lines.append('\ufeff')
            
            # Add some random tree structure
            num_trees = random.randint(1, 5)
            
            for i in range(num_trees):
                # Random tree name
                tree_name = ''.join(random.choice(string.ascii_uppercase) for _ in range(8))
                lines.append(f'HTGR_PRA, {tree_name}, IE-{tree_name} =')
                
                # Add random sections
                for section in ['^TOPS', '^SEQUENCES', '^LOGIC', '^TEXT', '^NODESUBS']:
                    if random.choice([True, False]):
                        lines.append(section)
                        # Add some random content for this section
                        num_lines = random.randint(1, 5)
                        for _ in range(num_lines):
                            lines.append(''.join(random.choice(string.printable) for _ in range(20)))
                
                # Add EOS marker except for last tree
                if i < num_trees - 1:
                    lines.append('^EOS')
                    # Maybe add BOM after EOS
                    if random.choice([True, False]):
                        lines.append('\ufeff')
            
            # Test parsing this random content
            content = '\n'.join(lines)
            result = parse_etl_file(content)
            
            # Basic validation - we're mainly testing that it doesn't crash
            self.assertEqual(result['type'], 'event_tree_logic')
            self.assertIn('event_trees', result['data'])
            
            # Note: we don't assert on the number of trees parsed, as the random
            # content may not be parseable, but the parser should still handle it
            # without crashing
    
    def test_end_to_end_extraction(self):
        """Test end-to-end extraction from a ZIP containing ETL files"""
        # Create minimal ETL content
        etl_content = self.generate_minimal_etl(num_trees=3, with_bom=True)
        
        # Create additional file types
        fad_content = "Test Project,Project Description"
        etd_content = "TREE_0,First tree description\nTREE_1,Second tree description"
        
        # Create a test zip
        files = {
            ".ETL": etl_content,
            ".FAD": fad_content,
            ".ETD": etd_content,
        }
        
        zip_path = self.create_test_zip(files)
        
        # Extract and analyze
        extract_dir = extract_zip(zip_path)
        result = analyze_files(extract_dir, "test_job")
        
        # Verify the extraction
        self.assertIn('saphire_data', result)
        self.assertIn('event_trees', result['saphire_data'])
        self.assertEqual(len(result['saphire_data']['event_trees']), 3)
        
        # Check for specific fields in the event trees
        for tree in result['saphire_data']['event_trees']:
            self.assertIn('id', tree)
            self.assertIn('name', tree)
            self.assertIn('sequences', tree)
    
    def test_idempotency(self):
        """Test that parsing an ETL file is idempotent"""
        # Generate ETL content
        etl_content = self.generate_minimal_etl(num_trees=3, with_bom=True)
        
        # Parse it once
        first_result = parse_etl_file(etl_content)
        
        # Convert to JSON and back to ensure we're comparing like with like
        first_json = json.dumps(first_result)
        first_result = json.loads(first_json)
        
        # Parse it again
        second_result = parse_etl_file(etl_content)
        second_json = json.dumps(second_result)
        second_result = json.loads(second_json)
        
        # Results should be identical (excluding any timing or non-deterministic values)
        self.assertEqual(first_result['type'], second_result['type'])
        self.assertEqual(
            len(first_result['data']['event_trees']), 
            len(second_result['data']['event_trees'])
        )
        
        # Check each tree name is present in both results
        for tree_name in first_result['data']['event_trees']:
            self.assertIn(tree_name, second_result['data']['event_trees'])

if __name__ == "__main__":
    unittest.main() 