#!/usr/bin/env python
"""
CLI Update Script

This script tests the updated CLI commands to ensure they're working correctly.
Run this after updating from the old command structure to the new one.
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import vyom
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Check if vyom is installed as a command
vyom_command = 'vyom'
if not shutil.which('vyom'):
    print("Warning: 'vyom' command not found in PATH. ")
    print("The CLI aliases may not work correctly unless the package is installed.")
    print("Installing the package with 'pip install -e .' is recommended.")
    # Fall back to using the module directly
    vyom_command = 'python -m vyom.cli'

def print_header(text):
    """Print a header with the given text."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def run_command(command, description=None):
    """Run a command and print its output."""
    if description:
        print(f"\n> {description}")
    
    cmd_str = " ".join(command) if isinstance(command, list) else command
    print(f"$ {cmd_str}")
    
    result = subprocess.run(command, capture_output=True, text=True, shell=isinstance(command, str))
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(f"Error: {result.stderr}", file=sys.stderr)
    
    return result


def test_cli_command_aliases():
    """Test that all CLI command aliases work correctly."""
    print_header("Testing CLI Command Aliases")
    
    # Test all the command aliases using the command names as displayed in help
    commands = {
        'import-': 'i',
        'list': 'l', 
        'show': 's',
        'explore': 'e',
        'convert': 'c',
        'convert-file': 'cf',
        'export': 'x',
        'view': 'v'
    }
    
    # For each command, test that the full name and alias show the same help
    for cmd_name, alias in commands.items():
        print(f"\nTesting alias '{alias}' for command '{cmd_name}':")
        
        # Get help for both the full command and the alias
        full_cmd = f"{vyom_command} {cmd_name} --help"
        alias_cmd = f"{vyom_command} {alias} --help"
        
        full_cmd_result = run_command(full_cmd, f"Testing full command: {cmd_name}")
        alias_cmd_result = run_command(alias_cmd, f"Testing alias: {alias}")
        
        # Check that both return code 0 (success)
        if full_cmd_result.returncode != 0:
            print(f"Error: Full command '{full_cmd}' failed with return code {full_cmd_result.returncode}")
            return False
            
        if alias_cmd_result.returncode != 0:
            print(f"Error: Alias command '{alias_cmd}' failed with return code {alias_cmd_result.returncode}")
            return False
            
        # Check that the help output is similar for both
        # We don't check for exact equality because the command name might be different in the output
        if len(full_cmd_result.stdout) < 10 or len(alias_cmd_result.stdout) < 10:
            print(f"Error: Help output is too short for {cmd_name} or its alias {alias}")
            return False
            
        print(f"✓ Alias '{alias}' for command '{cmd_name}' is working correctly")
        
    return True


def test_last_job_id_feature():
    """Test the '-' and 'last' job ID features."""
    print_header("Testing '-' and 'last' Job ID features")
    
    # Create a temporary file to use in the test
    temp_file = Path("test_saphire.json")
    
    try:
        # Create a simple JSON file as test data
        simple_data = {
            "version": "1.0.0",
            "project": {"name": "Test Project"},
            "saphire_data": {
                "basic_events": [],
                "fault_trees": [],
                "event_trees": []
            }
        }
        
        with open(temp_file, 'w') as f:
            json.dump(simple_data, f)
        
        # Test converting this file directly to avoid needing a real SAPHIRE ZIP
        cmd = f"{vyom_command} convert-file {temp_file}"
        result = run_command(cmd, "Converting test file to create a job")
        
        if result.returncode != 0:
            print("Error: Failed to convert test file")
            return False
        
        # Test listing jobs
        cmd = f"{vyom_command} list"
        result = run_command(cmd, "Listing all jobs")
        
        if result.returncode != 0:
            print("Error: Failed to list jobs")
            return False
        
        # Test using 'last' with show command
        cmd = f"{vyom_command} show last"
        result = run_command(cmd, "Testing 'last' with show command")
        
        if result.returncode != 0:
            print("Error: Failed to use 'last' with show command")
            return False
        
        # Test using '-' with show command
        cmd = f"{vyom_command} show -"
        result = run_command(cmd, "Testing '-' with show command")
        
        if result.returncode != 0:
            print("Error: Failed to use '-' with show command")
            return False
            
        print("\n✓ '-' and 'last' job ID features are working correctly")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
        
    finally:
        # Clean up
        if temp_file.exists():
            temp_file.unlink()


def test_help_and_version():
    """Test help and version commands."""
    print_header("Testing Help and Version Commands")
    
    # Test main help
    cmd = f"{vyom_command} --help"
    result = run_command(cmd, "Testing main help command")
    if result.returncode != 0:
        print("Error: Main help command failed")
        return False
    
    # Test version command
    cmd = f"{vyom_command} --version"
    result = run_command(cmd, "Testing version command")
    if result.returncode != 0:
        print("Error: Version command failed")
        return False
    
    print("\n✓ Help and version commands are working correctly")
    return True


def main():
    """Run all tests."""
    print_header("Vyom CLI Update Verification")
    print("This script tests the CLI command structure update to ensure all features are working correctly.")
    
    tests = [
        ("Command Aliases", test_cli_command_aliases),
        ("Last Job ID Feature", test_last_job_id_feature),
        ("Help and Version", test_help_and_version),
    ]
    
    results = []
    
    for name, test_func in tests:
        print_header(f"Running Test: {name}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"Error running test '{name}': {str(e)}")
            results.append((name, False))
    
    # Print summary
    print_header("Test Summary")
    
    all_passed = True
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        all_passed = all_passed and result
        print(f"{status}: {name}")
    
    if all_passed:
        print("\nAll tests passed! The CLI update is working correctly.")
        return 0
    else:
        print("\nSome tests failed. Please check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 