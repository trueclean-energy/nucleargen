#!/usr/bin/env python
"""
Test runner for Vyom application
"""
import os
import sys
import pytest
import subprocess
from pathlib import Path

def run_api_tests():
    """Run API-level tests using pytest"""
    print("Running API-level tests...")
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
    result = pytest.main([test_dir, '-v'])
    return result == 0

def run_specific_tests():
    """Run specific tests individually"""
    print("\nRunning SAPHIRE extraction tests...")
    saphire_extraction = run_test_module('test_saphire_extraction.py')
    
    print("\nRunning SAPHIRE parser tests...")
    saphire_parser = run_test_module('test_saphire_parser.py')
    
    print("\nRunning SAPHIRE file parsing tests...")
    saphire_file_parsing = run_test_module('test_saphire_parsing.py')
    
    print("\nRunning schema validation tests...")
    schema_tests = run_test_module('test_schema.py')
    
    print("\nRunning database tests...")
    db_tests = run_test_module('test_db.py')
    
    print("\nRunning converter tests...")
    converter_tests = run_test_module('test_converter.py')
    
    return all([
        saphire_extraction, 
        saphire_parser, 
        saphire_file_parsing,
        schema_tests, 
        db_tests, 
        converter_tests
    ])

def run_end_to_end_test(custom_zip_path=None):
    """Run the end-to-end test
    
    Args:
        custom_zip_path (str, optional): Path to a custom ZIP file to test with.
    """
    print("\nRunning end-to-end workflow test...")
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                            'tests', 'test_end_to_end.py')
    
    cmd = [sys.executable, test_path]
    if custom_zip_path and os.path.exists(custom_zip_path):
        cmd.append(custom_zip_path)
        
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print the output
    print(result.stdout)
    if result.stderr:
        print("ERRORS:", result.stderr)
    
    return result.returncode == 0

def run_saphire_converter_test():
    """Run the SAPHIRE to OpenPRA converter test"""
    print("\nRunning SAPHIRE to OpenPRA converter test...")
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                            'tests', 'test_saphire_to_openpra.py')
    
    if not os.path.exists(test_path):
        print(f"Test module not found: {test_path}")
        return False
        
    result = subprocess.run([sys.executable, test_path], 
                           capture_output=True, text=True)
    
    # Print the output
    print(result.stdout)
    if result.stderr:
        print("ERRORS:", result.stderr)
    
    return result.returncode == 0

def create_saphire_converter_test():
    """Create a SAPHIRE to OpenPRA converter test file if it doesn't exist"""
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                            'tests', 'test_saphire_to_openpra.py')
    
    # For simplicity, we have moved the content creation to a separate mechanism.
    # This test file should be committed to the repository.
    if not os.path.exists(test_path):
        print(f"Test file not found: {test_path}")
        print("Please create the test file manually or check the repository.")
    else:
        print(f"Test file exists: {test_path}")

def run_test_module(module_name):
    """Run a specific test module"""
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                            'tests', module_name)
    if not os.path.exists(test_path):
        print(f"Test module not found: {test_path}")
        return False
        
    result = subprocess.run([sys.executable, test_path], 
                           capture_output=True, text=True)
    
    # Print the output
    print(result.stdout)
    if result.stderr:
        print("ERRORS:", result.stderr)
    
    return result.returncode == 0

def run_integration_test():
    """Run integration tests that combine multiple components"""
    print("\nRunning integration tests...")
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                            'tests', 'test_integration.py')
    
    if not os.path.exists(test_path):
        print(f"Test module not found: {test_path}")
        return False
        
    result = subprocess.run([sys.executable, test_path], 
                           capture_output=True, text=True)
    
    # Print the output
    print(result.stdout)
    if result.stderr:
        print("ERRORS:", result.stderr)
    
    return result.returncode == 0

def main():
    """Main test runner function"""
    # Check if a custom ZIP path was provided
    custom_zip_path = None
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        custom_zip_path = sys.argv[1]
        print(f"Using custom ZIP file for end-to-end test: {custom_zip_path}")
    
    # Ensure tests directory exists
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
    os.makedirs(test_dir, exist_ok=True)
    
    # Create an __init__.py in the tests directory if it doesn't exist
    init_file = os.path.join(test_dir, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write("# Test package\n")
    
    # Run tests
    api_success = run_api_tests()
    specific_success = run_specific_tests()
    saphire_converter_success = run_saphire_converter_test()
    integration_success = run_integration_test()
    end_to_end_success = run_end_to_end_test(custom_zip_path)
    
    # Print overall result
    print("\n=== Test Results ===")
    print(f"API Tests: {'✅' if api_success else '❌'}")
    print(f"Specific Tests: {'✅' if specific_success else '❌'}")
    print(f"SAPHIRE Converter Tests: {'✅' if saphire_converter_success else '❌'}")
    print(f"Integration Tests: {'✅' if integration_success else '❌'}")
    print(f"End-to-End Tests: {'✅' if end_to_end_success else '❌'}")
    
    if api_success and specific_success and saphire_converter_success and integration_success and end_to_end_success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 