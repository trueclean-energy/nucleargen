"""
Nuclear Data Validation Application with Gemini AI Integration

To run this application:
1. Activate the virtual environment:
   $ cd /Users/personal/DEV/nucleargen
   $ source venv/bin/activate

2. Then run this script:
   $ cd data-validation
   $ python app.py

Or use the provided shell script:
   $ ./data-validation/run.sh
"""

import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize the app
app = Flask(__name__)

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05");

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate():
    """Validate the provided data"""
    data_input = request.form.get('data_input', '')
    
    # Simple validation for demonstration
    is_valid_format = len(data_input) > 10  # Example validation rule
    is_valid_content = 'nuclear' in data_input.lower()  # Example content check
    
    # Prepare the response
    response = {
        'status': 'valid' if (is_valid_format and is_valid_content) else 'invalid',
        'details': {
            'length': len(data_input),
            'format_check': is_valid_format,
            'content_check': is_valid_content
        },
        'messages': []
    }
    
    # Add specific validation messages
    if not is_valid_format:
        response['messages'].append('Data is too short (minimum 10 characters).')
    if not is_valid_content:
        response['messages'].append('Data must contain nuclear-related content.')
        
    return jsonify(response)

@app.route('/gemini', methods=['POST'])
def gemini_api():
    """Process requests to the Gemini AI API"""
    # Get prompt from the request
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided', 'response': 'Please provide a question or prompt.'})
    
    try:
        # Generate content using Gemini
        print(f"Sending prompt to Gemini API: {prompt[:50]}...")
        response = model.generate_content(prompt)
        print("Received response from Gemini API")
        return jsonify({'response': response.text})
    except Exception as e:
        # Handle any errors
        print(f"Error in Gemini API: {str(e)}")
        return jsonify({'error': str(e), 'response': f'An error occurred while processing your request: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 