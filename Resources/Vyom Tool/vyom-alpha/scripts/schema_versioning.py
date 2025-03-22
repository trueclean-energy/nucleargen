#!/usr/bin/env python
"""
OpenPRA Schema Versioning Tool

This script helps manage OpenPRA schema versions and migrations.

Usage:
  python schema_versioning.py --info                     # Show schema version information
  python schema_versioning.py --validate <file>          # Validate a file against the schema
  python schema_versioning.py --upgrade <file> <version> # Upgrade a file to a newer schema version
  python schema_versioning.py --export <version>         # Export a specific schema version
"""
import os
import sys
import json
import argparse
import datetime
from pathlib import Path

# Add the parent directory to the path so that we can import vyom
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from vyom.schema import openpra

def show_schema_info():
    """Display information about available schema versions"""
    print("OpenPRA Schema Versions:")
    print("=======================")
    
    versions = openpra.get_schema_versions()
    latest = openpra.get_latest_schema_version()
    
    for version in versions:
        info = openpra.get_schema_version_info(version)
        is_latest = " (latest)" if version == latest else ""
        print(f"Version {version}{is_latest}:")
        print(f"  Released: {info['release_date']}")
        print(f"  Description: {info['description']}")
        print()

def validate_file(file_path):
    """Validate a file against the OpenPRA schema"""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    try:
        data, success, message = openpra.load_from_file(file_path)
        
        if not success:
            print(f"Validation failed: {message}")
            
            # Print more details about the schema validation
            if "version" in data:
                version = data["version"]
                print(f"File schema version: {version}")
                
                if version in openpra.get_schema_versions():
                    print("This is a supported schema version.")
                    print("Use --upgrade to upgrade to a newer version if needed.")
                else:
                    print(f"Warning: Unsupported schema version. Supported versions: {', '.join(openpra.get_schema_versions())}")
            else:
                print("No schema version information found in the file.")
            
            return False
        
        print(f"File is valid: {message}")
        print(f"Schema version: {data['version']}")
        
        # Print some summary information
        if "metadata" in data:
            print("\nMetadata:")
            print(f"  Title: {data['metadata'].get('title', 'N/A')}")
            print(f"  Created: {data['metadata'].get('created_date', 'N/A')}")
            print(f"  Schema version: {data['metadata'].get('schema_version', 'N/A')}")
        
        if "models" in data:
            print("\nModel Counts:")
            print(f"  Fault Trees: {len(data['models'].get('fault_trees', []))}")
            print(f"  Event Trees: {len(data['models'].get('event_trees', []))}")
            print(f"  Basic Events: {len(data['models'].get('basic_events', []))}")
            print(f"  End States: {len(data['models'].get('end_states', []))}")
        
        return True
    
    except Exception as e:
        print(f"Error validating file: {str(e)}")
        return False

def upgrade_file(file_path, target_version):
    """Upgrade a file to a newer schema version"""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    if target_version not in openpra.get_schema_versions():
        print(f"Error: Unsupported target version: {target_version}")
        print(f"Supported versions: {', '.join(openpra.get_schema_versions())}")
        return False
    
    try:
        # Load the file
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check if version information is present
        if "version" not in data:
            print("Error: No version information found in the file.")
            return False
        
        current_version = data["version"]
        
        # Check if upgrade is needed
        if current_version == target_version:
            print(f"File is already at version {target_version}.")
            return True
        
        # Upgrade the schema
        upgraded_data, success, message = openpra.upgrade_schema(data, target_version)
        
        if not success:
            print(f"Upgrade failed: {message}")
            return False
        
        # Save to a new file
        base_name = os.path.splitext(file_path)[0]
        new_file_path = f"{base_name}_v{target_version}.json"
        
        with open(new_file_path, 'w') as f:
            json.dump(upgraded_data, f, indent=2)
        
        print(f"Upgraded from version {current_version} to {target_version}")
        print(f"Saved to: {new_file_path}")
        
        # Validate the upgraded file
        print("\nValidating upgraded file:")
        validate_file(new_file_path)
        
        return True
    
    except Exception as e:
        print(f"Error upgrading file: {str(e)}")
        return False

def export_schema(version=None):
    """Export a specific schema version to a file"""
    if version is None:
        version = openpra.get_latest_schema_version()
    
    if version not in openpra.get_schema_versions():
        print(f"Error: Unsupported version: {version}")
        print(f"Supported versions: {', '.join(openpra.get_schema_versions())}")
        return False
    
    try:
        # Create an empty schema
        schema = openpra.create_empty_schema(version)
        
        # Save to file
        exports_dir = os.path.join(parent_dir, "data", "examples")
        os.makedirs(exports_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        file_path = os.path.join(exports_dir, f"openpra_schema_v{version}_{timestamp}.json")
        
        with open(file_path, 'w') as f:
            json.dump(schema, f, indent=2)
        
        print(f"Exported schema version {version} to {file_path}")
        return True
    
    except Exception as e:
        print(f"Error exporting schema: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="OpenPRA Schema Versioning Tool")
    
    # Define mutually exclusive arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--info", action="store_true", help="Show schema version information")
    group.add_argument("--validate", metavar="FILE", help="Validate a file against the schema")
    group.add_argument("--upgrade", nargs=2, metavar=("FILE", "VERSION"), help="Upgrade a file to a newer schema version")
    group.add_argument("--export", nargs='?', const=None, metavar="VERSION", help="Export a specific schema version")
    
    args = parser.parse_args()
    
    if args.info:
        show_schema_info()
    elif args.validate:
        validate_file(args.validate)
    elif args.upgrade:
        upgrade_file(args.upgrade[0], args.upgrade[1])
    elif args.export is not None:
        export_schema(args.export)
    else:
        export_schema()

if __name__ == "__main__":
    main() 