"""
Edge Case Tests for ETL Parsing.

This test module focuses on edge cases in ETL parsing that have been identified
as potential problems, including BOM markers, tree boundaries, and malformed data.
"""
import os
import sys
import tempfile
import zipfile
import unittest
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vyom.schema.saphire import parse_etl_file
from vyom.extractor import analyze_files, extract_zip

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestETLEdgeCases(unittest.TestCase):
    """Test class for ETL parser edge cases"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp(prefix="vyom_test_etl_edge_")
        self.test_data_dir = os.path.join(self.temp_dir, "test_data")
        os.makedirs(self.test_data_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
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
    
    def test_bom_at_file_start(self):
        """Test ETL parser with BOM at file start"""
        etl_content = '\ufeffHTGR_PRA, TREE_1, IE-TREE_1 =\n^TOPS\nTOP1, TOP2\n^SEQUENCES\n*\nY, SEQ1, , OK'
        result = parse_etl_file(etl_content)
        
        self.assertEqual(result['type'], 'event_tree_logic')
        self.assertIn('event_trees', result['data'])
        self.assertEqual(len(result['data']['event_trees']), 1)
        self.assertIn('TREE_1', result['data']['event_trees'])
    
    def test_multiple_bom_between_trees(self):
        """Test ETL parser with multiple BOM characters between trees"""
        etl_content = 'HTGR_PRA, TREE_1, IE-TREE_1 =\n^TOPS\nTOP1, TOP2\n^SEQUENCES\n*\nY, SEQ1, , OK\n^EOS\n'
        etl_content += '\ufeff\ufeff\ufeffHTGR_PRA, TREE_2, IE-TREE_2 =\n^TOPS\nTOP1, TOP2\n^SEQUENCES\n*\nY, SEQ2, , OK'
        
        result = parse_etl_file(etl_content)
        
        self.assertEqual(result['type'], 'event_tree_logic')
        self.assertIn('event_trees', result['data'])
        self.assertEqual(len(result['data']['event_trees']), 2)
        self.assertIn('TREE_1', result['data']['event_trees'])
        self.assertIn('TREE_2', result['data']['event_trees'])
    
    def test_no_eos_between_trees(self):
        """Test ETL parser with missing EOS markers between trees"""
        # Create content with two trees but no EOS marker
        etl_content = 'HTGR_PRA, TREE_1, IE-TREE_1 =\n^TOPS\nTOP1, TOP2\n^SEQUENCES\n*\nY, SEQ1, , OK\n'
        etl_content += 'HTGR_PRA, TREE_2, IE-TREE_2 =\n^TOPS\nTOP1, TOP2\n^SEQUENCES\n*\nY, SEQ2, , OK'
        
        result = parse_etl_file(etl_content)
        
        # Either both trees should be detected, or at least an error should be logged
        if len(result['data']['event_trees']) == 2:
            self.assertIn('TREE_1', result['data']['event_trees'])
            self.assertIn('TREE_2', result['data']['event_trees'])
        else:
            self.assertTrue(len(result['errors']) > 0)
    
    def test_htgr_event_trees_real_case(self):
        """Test ETL parser with a simulated HTGR_Event_Trees case like the real one"""
        # Simulate the actual file structure found in the HTGR_Event_Trees case
        trees = [
            "ATWS", 
            "CR-GROUP-WITHDRAWAL", 
            "EARTHQUAKE", 
            "HTS-COOLING-LOSS", 
            "LOSP", 
            "PRIMARY-LOCA", 
            "SG-LK-MODERATE", 
            "SG-LK-SMALL"
        ]
        
        etl_content = '\ufeff'  # Start with BOM
        
        for i, tree_name in enumerate(trees):
            # Add tree definition
            etl_content += f'HTGR_PRA, {tree_name}, IE-{tree_name} =\n'
            etl_content += f'^TOPS\nTOP1_{tree_name}, TOP2_{tree_name}\n'
            etl_content += f'^SEQUENCES\n*\nY, SEQ1_{tree_name}, , OK\nY, SEQ2_{tree_name}, , FAIL\n'
            etl_content += f'^LOGIC\nSEQ1_{tree_name}, TOP1_{tree_name}\nSEQ2_{tree_name}, TOP2_{tree_name}\n'
            
            # Add EOS and BOM except for the last tree
            if i < len(trees) - 1:
                etl_content += '^EOS\n\ufeff'
        
        # Parse the ETL content
        result = parse_etl_file(etl_content)
        
        # Check the result
        self.assertEqual(result['type'], 'event_tree_logic')
        self.assertIn('event_trees', result['data'])
        self.assertEqual(len(result['data']['event_trees']), len(trees))
        
        # Verify all trees were found
        for tree_name in trees:
            self.assertIn(tree_name, result['data']['event_trees'])
            
            # Verify basic structure of each tree
            tree = result['data']['event_trees'][tree_name]
            self.assertIn('top_events', tree)
            self.assertEqual(len(tree['top_events']), 2)
            self.assertIn('sequences', tree)
            self.assertEqual(len(tree['sequences']), 2)
    
    def test_zip_extraction_bom(self):
        """Test extraction from a ZIP file with BOM characters"""
        # Create ETL content with BOM characters
        etl_content = '\ufeff'  # Start with BOM
        
        # Add multiple trees with BOM characters between them
        for i in range(5):
            tree_name = f"TREE_{i}"
            etl_content += f'HTGR_PRA, {tree_name}, IE-{tree_name} =\n'
            etl_content += f'^TOPS\nTOP1, TOP2\n^SEQUENCES\n*\nY, SEQ1, , OK\n'
            
            # Add EOS and BOM except for the last tree
            if i < 4:
                etl_content += '^EOS\n\ufeff'
        
        # Create a ZIP with this content
        files = {".ETL": etl_content}
        zip_path = self.create_test_zip(files)
        
        # Extract and analyze
        extract_dir = extract_zip(zip_path)
        result = analyze_files(extract_dir, "test_job")
        
        # Verify that all trees were extracted
        self.assertIn('saphire_data', result)
        self.assertIn('event_trees', result['saphire_data'])
        self.assertEqual(len(result['saphire_data']['event_trees']), 5)
        
        # Check that each tree is present
        tree_names = [f"TREE_{i}" for i in range(5)]
        for tree in result['saphire_data']['event_trees']:
            self.assertIn(tree.get('name'), tree_names)
    
    def test_malformed_tree_headers(self):
        """Test ETL parser with malformed tree headers"""
        # Create content with various malformed headers
        etl_content = 'HTGR_PRA, TREE_1 =\n^TOPS\nTOP1, TOP2\n^SEQUENCES\n*\nY, SEQ1, , OK\n^EOS\n'  # Missing IE part
        etl_content += 'HTGR_PRA,TREE_2,IE-TREE_2 =\n^TOPS\nTOP1, TOP2\n^SEQUENCES\n*\nY, SEQ2, , OK\n^EOS\n'  # No spaces after commas
        etl_content += 'HTGR_PRA, TREE_3, IE-TREE_3\n^TOPS\nTOP1, TOP2\n^SEQUENCES\n*\nY, SEQ3, , OK'  # Missing "=" at the end
        
        result = parse_etl_file(etl_content)
        
        # The parser should still identify at least some trees
        self.assertGreater(len(result['data']['event_trees']), 0)
        
        # Check if specific trees were found despite malformed headers
        found_trees = list(result['data']['event_trees'].keys())
        logger.info(f"Found trees: {found_trees}")
        
        # There might be errors logged
        if len(found_trees) < 3:
            self.assertTrue(len(result['errors']) > 0)
    
    def test_missing_sections(self):
        """Test ETL parser with trees missing certain sections"""
        # Tree with missing TOPS section
        tree1 = 'HTGR_PRA, TREE_1, IE-TREE_1 =\n^SEQUENCES\n*\nY, SEQ1, , OK\n^LOGIC\nSEQ1, TOP1\n^EOS\n'
        
        # Tree with missing SEQUENCES section
        tree2 = 'HTGR_PRA, TREE_2, IE-TREE_2 =\n^TOPS\nTOP1, TOP2\n^LOGIC\nSEQ1, TOP1\n^EOS\n'
        
        # Tree with missing LOGIC section
        tree3 = 'HTGR_PRA, TREE_3, IE-TREE_3 =\n^TOPS\nTOP1, TOP2\n^SEQUENCES\n*\nY, SEQ1, , OK\n'
        
        etl_content = tree1 + tree2 + tree3
        
        result = parse_etl_file(etl_content)
        
        # The parser should identify all trees despite missing sections
        self.assertEqual(len(result['data']['event_trees']), 3)
        
        # Check each tree has what sections were provided
        tree = result['data']['event_trees']['TREE_1']
        self.assertIn('sequences', tree)
        
        tree = result['data']['event_trees']['TREE_2']
        self.assertIn('top_events', tree)
        
        tree = result['data']['event_trees']['TREE_3']
        self.assertIn('top_events', tree)
        self.assertIn('sequences', tree)

if __name__ == "__main__":
    unittest.main() 