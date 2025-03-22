"""
End-to-end test of the Vyom application
"""
import os
import json
import tempfile
import shutil
import subprocess
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.test_saphire_extraction import create_test_zip

def test_full_workflow(custom_zip_path=None):
    """Test the full workflow of the application
    
    Args:
        custom_zip_path (str, optional): Path to a custom ZIP file to test with.
            If not provided, a test ZIP is created automatically.
    """
    if custom_zip_path and os.path.exists(custom_zip_path):
        # Use the provided ZIP file
        zip_path = custom_zip_path
        temp_dir = tempfile.mkdtemp(prefix="vyom_test_")
        print(f"Using custom ZIP file: {zip_path}")
    else:
        # Create a test ZIP file
        zip_path, temp_dir = create_test_zip()
        print(f"Test ZIP file created at: {zip_path}")
    
    try:
        # Build the command to import the ZIP file
        import_cmd = [sys.executable, "-m", "vyom.cli", "import", zip_path]
        print(f"Running command: {' '.join(import_cmd)}")
        
        # Run the import command
        result = subprocess.run(import_cmd, capture_output=True, text=True)
        
        # Check if the command was successful
        assert result.returncode == 0, f"Import command failed: {result.stderr}"
        print("Import command output:")
        print(result.stdout)
        
        # Extract the job ID from the output
        output_lines = result.stdout.strip().split("\n")
        job_id_line = next((line for line in output_lines if "Job ID:" in line), None)
        assert job_id_line is not None, "Could not find job ID in output"
        
        job_id = job_id_line.split("Job ID:")[1].split("-")[0].strip()
        print(f"Job ID: {job_id}")
        
        # Check the job status using explore command
        explore_status_cmd = [sys.executable, "-m", "vyom.cli", "explore", job_id]
        result = subprocess.run(explore_status_cmd, capture_output=True, text=True)
        
        # Check if the command was successful
        assert result.returncode == 0, f"Explore command failed: {result.stderr}"
        print("Explore command output:")
        print(result.stdout)
        
        # Export the raw data
        export_path = os.path.join(temp_dir, "export.json")
        export_cmd = [sys.executable, "-m", "vyom.cli", "explore", job_id, "--export", "-o", export_path]
        result = subprocess.run(export_cmd, capture_output=True, text=True)
        
        # Check if the command was successful
        assert result.returncode == 0, f"Export command failed: {result.stderr}"
        assert os.path.exists(export_path), "Export file should exist"
        print(f"Data exported to: {export_path}")
        
        # Check the exported data
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        assert "files" in export_data, "Exported data should have files"
        assert "metadata" in export_data, "Exported data should have metadata"
        
        # Convert to OpenPRA format
        convert_path = os.path.join(temp_dir, "openpra.json")
        convert_cmd = [sys.executable, "-m", "vyom.cli", "convert", job_id, "--output", convert_path]
        result = subprocess.run(convert_cmd, capture_output=True, text=True)
        
        # Check if the command was successful
        assert result.returncode == 0, f"Convert command failed: {result.stderr}"
        assert os.path.exists(convert_path), "Convert file should exist"
        print(f"Data converted to: {convert_path}")
        
        # Check the converted data
        with open(convert_path, 'r') as f:
            openpra_data = json.load(f)
        
        assert "version" in openpra_data, "OpenPRA data should have version"
        assert "metadata" in openpra_data, "OpenPRA data should have metadata"
        assert "models" in openpra_data, "OpenPRA data should have models"
        
        # List all jobs
        list_cmd = [sys.executable, "-m", "vyom.cli", "list"]
        result = subprocess.run(list_cmd, capture_output=True, text=True)
        
        # Check if the command was successful
        assert result.returncode == 0, f"List command failed: {result.stderr}"
        assert job_id in result.stdout, "Job ID should be in the list output"
        print("List command output:")
        print(result.stdout)
        
        # Try the visualization (if available)
        try:
            # Only run this test if the visualization functionality exists
            # Use --no-browser so it doesn't open a browser window during tests
            view_cmd = [sys.executable, "-m", "vyom.cli", "view", job_id, "--no-browser"]
            result = subprocess.run(view_cmd, capture_output=True, text=True)
            
            # Check if the command was successful
            if result.returncode == 0:
                print("View command successful")
                # Check for visualization output path
                output_path_line = next((line for line in result.stdout.split("\n") 
                                     if "File saved at" in line), None)
                if output_path_line:
                    viz_path = output_path_line.split("File saved at")[1].strip()
                    assert os.path.exists(viz_path), "Visualization file should exist"
                    print(f"Visualization file created at: {viz_path}")
                    
                    # Verify the visualization file contains the expected content
                    with open(viz_path, 'r') as f:
                        content = f.read()
                        assert 'monaco-editor' in content, "Visualization should include Monaco editor"
                        assert 'comment-section' in content, "Visualization should include comment section"
                        assert 'json-panel' in content, "Visualization should include JSON panel"
                        
                        # Verify JavaScript code
                        assert 'currentSelectedPath' in content, "Visualization should include currentSelectedPath variable"
                        assert 'updateJsonEditor' in content, "Visualization should include updateJsonEditor function"
                        assert 'path || \'\'' in content, "Visualization should handle undefined path"
                        
                        # Verify error handling
                        assert 'try {' in content, "Visualization should include error handling"
                        assert 'catch (error)' in content, "Visualization should catch errors"
                        assert 'if (!Array.isArray(items))' in content, "Visualization should validate array inputs"
                        assert 'console.error' in content, "Visualization should log errors"
                        assert '<div class="empty-state">Error loading data</div>' in content, "Visualization should show error state"
                        
                        # Verify data loading
                        assert 'const saphireData = ' in content, "Visualization should load SAPHIRE data"
                        assert 'const jobId = ' in content, "Visualization should load job ID"
                        assert 'comments: ' in content, "Visualization should load comments"
                        
                        print("Visualization file content verified")
                else:
                    print("View command output did not contain visualization file path")
            else:
                print(f"View command failed: {result.stderr}")
        except Exception as e:
            print(f"View test error: {str(e)}")
        
        print("Full workflow test completed successfully!")
        return True
    except Exception as e:
        print(f"End-to-end test failed: {str(e)}")
        return False
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    # Check if a custom ZIP path was provided as a command line argument
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        custom_zip_path = sys.argv[1]
        print(f"Using custom ZIP file: {custom_zip_path}")
        test_full_workflow(custom_zip_path)
    else:
        test_full_workflow() 