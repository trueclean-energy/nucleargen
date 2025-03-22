"""
Nuclear Data Validation Module

A simple web application for validating nuclear data formats.
"""

from flask import Flask, request, render_template, jsonify
import webbrowser
import os
import threading
import time

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))

def validate_nuclear_data(data_string):
    """
    Validate nuclear data format and content.
    
    Args:
        data_string (str): The data to validate
        
    Returns:
        dict: Validation results with status and details
    """
    # This is a placeholder for actual validation logic
    
    results = {
        "status": "valid" if len(data_string) > 0 else "invalid",
        "details": {
            "length": len(data_string),
            "format_check": True,
            "content_check": True
        },
        "messages": []
    }
    
    # Add some example validation logic
    if len(data_string) < 10:
        results["status"] = "invalid"
        results["details"]["content_check"] = False
        results["messages"].append("Data is too short for proper validation")
    
    # You would add actual validation checks here based on
    # the expected format of your nuclear data
    
    return results

def validate_file(file_path):
    """
    Validate nuclear data from a file.
    
    Args:
        file_path (str): Path to the file to validate
        
    Returns:
        dict: Validation results
    """
    try:
        with open(file_path, 'r') as file:
            data = file.read()
        return validate_nuclear_data(data)
    except Exception as e:
        return {
            "status": "error",
            "details": {
                "error_type": str(type(e).__name__),
                "error_message": str(e)
            },
            "messages": [f"Error reading file: {str(e)}"]
        }

@app.route('/')
def index():
    """Serve the index.html file."""
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate_data():
    """Handle data validation requests from the web interface."""
    data = request.form.get('data_input', '')
    
    # Process the data using our validation function
    results = validate_nuclear_data(data)
    
    # Return the results as JSON
    return jsonify(results)

def open_browser():
    """Open the web browser after a short delay."""
    time.sleep(1)
    webbrowser.open('http://127.0.0.1:5000/')

# Example usage
if __name__ == "__main__":
    # Start the browser-opening thread
    threading.Thread(target=open_browser).start()
    
    # Start the Flask application
    print("Starting Nuclear Data Validation Tool...")
    print("Opening web browser. If it doesn't open automatically, navigate to: http://127.0.0.1:5000/")
    app.run(debug=False)  # Set debug=False for production use
