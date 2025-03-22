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
import json
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize the app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'json'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def validate_schema_naming(schema_json):
    """
    Analyze a JSON schema for naming convention issues
    using Gemini AI to provide insights and suggestions.
    """
    prompt = f"""
    You are a Nuclear PRA (Probabilistic Risk Assessment) expert reviewing schemas for naming convention consistency. 
    Please analyze the following JSON schema and provide:
    
    1. An overall assessment of naming convention consistency
    2. Any identified inconsistencies in naming patterns
    3. Suggestions for standardizing naming conventions
    4. Any other potential issues noticed with component references or naming
    
    Format your response in clear sections with bullet points where appropriate.
    
    JSON Schema to analyze:
    ```json
    {schema_json}
    ```
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error in schema validation: {str(e)}")
        return f"Error analyzing schema: {str(e)}"

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

@app.route('/validate-schema', methods=['POST'])
def validate_schema():
    """Validate a JSON schema for naming convention consistency"""
    try:
        # Get the JSON data
        data = request.json
        schema_text = data.get('schema', '')
        
        if not schema_text:
            return jsonify({
                'error': 'No schema provided',
                'analysis': 'Please provide a JSON schema to analyze.'
            })
        
        # Parse the JSON to validate it's properly formatted
        try:
            # If it's already a JSON object, we'll just use it as is
            if isinstance(schema_text, dict):
                schema_json = schema_text
            else:
                # Otherwise parse the string
                schema_json = json.loads(schema_text)
        except json.JSONDecodeError:
            return jsonify({
                'error': 'Invalid JSON',
                'analysis': 'The provided schema is not valid JSON. Please check the formatting.'
            })
        
        # Analyze the schema with Gemini
        analysis = validate_schema_naming(json.dumps(schema_json, indent=2))
        
        return jsonify({
            'analysis': analysis
        })
        
    except Exception as e:
        print(f"Error in schema validation: {str(e)}")
        return jsonify({
            'error': str(e),
            'analysis': f'An error occurred while analyzing the schema: {str(e)}'
        })

@app.route('/upload-json', methods=['POST'])
def upload_json():
    """Handle JSON file upload and validate it"""
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file part',
                'message': 'No file was uploaded.'
            })
            
        file = request.files['file']
        
        # If user does not select file, browser might submit an empty file
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'No file was selected.'
            })
            
        if file and allowed_file(file.filename):
            # Securely save the file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Read the JSON file content
            try:
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                
                # Return the JSON content for validation
                return jsonify({
                    'success': True,
                    'filename': filename,
                    'content': json_data
                })
            except json.JSONDecodeError:
                return jsonify({
                    'error': 'Invalid JSON',
                    'message': 'The uploaded file is not valid JSON.'
                })
        else:
            return jsonify({
                'error': 'Invalid file type',
                'message': 'Only JSON files are allowed.'
            })
            
    except Exception as e:
        print(f"Error in file upload: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': f'An error occurred while processing your file: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 