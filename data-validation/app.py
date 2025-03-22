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
import re
import time
import threading
from flask import Flask, request, jsonify, render_template, send_file, stream_with_context, Response
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import google.generativeai as genai
import tempfile
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize the app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORTS_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'json'}
app.config['REPORT_TIMEOUT'] = 60  # Maximum time for report generation in seconds
app.config['SECRET_KEY'] = os.urandom(24)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")

# Store background tasks
report_tasks = {}

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

def generate_schema_report_async(task_id, schema, filename=''):
    """
    Asynchronously generates a schema report and updates the task status.
    """
    task = report_tasks[task_id]
    
    try:
        # Update status to processing
        task['status'] = 'processing'
        task['progress'] = 5
        task['message'] = 'Validating schema structure...'
        
        # Validate schema structure
        if not isinstance(schema, dict):
            raise ValueError("Invalid schema format: must be a JSON object")
        
        # Determine if this is a large schema
        is_large = is_large_schema(schema)
        
        # Update progress
        task['progress'] = 10
        task['message'] = 'Analyzing schema structure...'
        
        # Collect statistics about the schema
        statistics = {
            'total_elements': count_schema_elements(schema),
            'naming_patterns': analyze_naming_patterns(schema),
            'element_types': analyze_element_types(schema)
        }
        
        # Update progress
        task['progress'] = 30
        task['message'] = 'Analyzing schema content...'
        
        # For large schemas, use a simplified analysis
        if is_large:
            task['message'] = 'Processing large schema (simplified analysis)...'
            # Get a representative sample of the schema
            schema_sample = extract_schema_sample(schema)
            prompt = create_simplified_prompt(schema_sample, filename)
        else:
            # Create a prompt for the AI
            prompt = f"""
            Please analyze this JSON schema for a nuclear industry application and provide:
            1. A summary of the schema structure and purpose
            2. Identified issues with naming conventions, structure, or other aspects
            3. Recommendations for improvement
            4. An improved version of the schema
            5. A quality score from 0-10
            
            Schema: {json.dumps(schema, indent=2)}
            """
            if filename:
                prompt += f"\nFilename: {filename}"
        
        # Start timer for AI call
        ai_start_time = time.time()
        
        # Update progress
        task['progress'] = 40
        task['message'] = 'Generating AI analysis...'
        
        # Simulate AI analysis (in a production environment, this would call a real AI API)
        # This is a placeholder for actual AI integration
        try:
            # Check if we've exceeded timeout
            current_time = time.time()
            if current_time - task['start_time'] > app.config['REPORT_TIMEOUT'] * 0.8:
                # If close to timeout, return simplified analysis
                analysis_text = generate_fallback_analysis(schema, statistics)
                task['message'] = 'Generated simplified analysis due to timeout constraints'
            else:
                # In a real implementation, this would be a call to an AI service
                # Wait with timeout to simulate API call
                # For now, we'll create a simulated response based on the schema
                time.sleep(min(3, app.config['REPORT_TIMEOUT'] * 0.3))  # Simulate AI processing time, capped at 3 seconds
                analysis_text = generate_ai_analysis(schema, statistics, is_large)
                
                # Check if timeout occurred during AI call
                if time.time() - ai_start_time > app.config['REPORT_TIMEOUT'] * 0.7:
                    task['message'] = 'AI analysis took longer than expected, results may be limited'
        except Exception as e:
            app.logger.error(f"Error during AI analysis: {str(e)}")
            # Fallback to simple analysis if AI fails
            analysis_text = generate_fallback_analysis(schema, statistics)
            task['message'] = 'Generated simplified analysis due to AI service error'
        
        # Update progress
        task['progress'] = 70
        task['message'] = 'Extracting insights from analysis...'
        
        # Extract issues, recommendations, and improved schema from the analysis
        report_data = extract_report_data(analysis_text, schema)
        
        # Generate a unique report ID
        report_id = str(uuid.uuid4())
        report_filename = f"{report_id}.json"
        report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
        
        # Save the report to a file
        with open(report_path, 'w') as f:
            json.dump({
                'report_data': report_data,
                'statistics': statistics,
                'schema': schema,
                'generated_at': datetime.now().isoformat(),
                'filename': filename
            }, f, indent=2)
        
        # Update progress
        task['progress'] = 90
        task['message'] = 'Finalizing report...'
        
        # Create the final report object
        report = {
            'report_id': report_id,
            'report_data': report_data,
            'statistics': statistics,
            'generated_at': datetime.now().isoformat()
        }
        
        # Update the task with the completed report
        task['status'] = 'completed'
        task['progress'] = 100
        task['message'] = 'Report generation complete'
        task['report'] = report
        
    except Exception as e:
        app.logger.error(f"Error generating report: {str(e)}")
        task['status'] = 'error'
        task['progress'] = 0
        task['error'] = str(e)

def is_large_schema(schema):
    """Determine if schema is too large for detailed analysis"""
    schema_str = json.dumps(schema)
    return len(schema_str) > 1000000  # Consider schemas > 1MB as large

def extract_schema_sample(schema, max_keys=100):
    """Extract a representative sample from a large schema"""
    sample = {}
    
    # For large objects, extract a limited number of keys
    if isinstance(schema, dict):
        # Get the first few keys
        keys = list(schema.keys())[:max_keys]
        for key in keys:
            # For nested structures, do a shallow copy
            if isinstance(schema[key], (dict, list)):
                if isinstance(schema[key], dict):
                    sample[key] = {k: schema[key][k] for k in list(schema[key].keys())[:5]} if schema[key] else {}
                else:
                    sample[key] = schema[key][:5] if schema[key] else []
            else:
                sample[key] = schema[key]
    
    return sample

def create_simplified_prompt(schema_sample, filename=''):
    """Create a simplified prompt for the AI using a schema sample"""
    return f"""
    Please provide a simplified analysis of this large JSON schema sample:
    1. Brief summary of the schema structure
    2. Common naming patterns observed in the sample
    3. Potential issues observed in the sample
    4. General recommendations for schema of this type
    5. A quality score from 0-10 based on the sample
    
    Schema Sample: {json.dumps(schema_sample, indent=2)}
    """

def generate_fallback_analysis(schema, statistics):
    """Generate a simple analysis text without AI when timeout occurs"""
    naming_patterns = statistics['naming_patterns']
    element_types = statistics['element_types']
    total_elements = statistics['total_elements']
    
    # Identify potential issues based on heuristics
    issues = []
    
    # Check for consistent naming patterns
    pattern_keys = list(naming_patterns.keys())
    if len(pattern_keys) > 3:
        issues.append("- Inconsistent naming conventions detected across schema elements")
    
    # Check for balance of types
    if 'object' not in element_types:
        issues.append("- Schema appears to lack proper structural hierarchy (missing object types)")
    
    # Check for empty arrays or objects
    if 'empty_arrays' in statistics and statistics['empty_arrays'] > 0:
        issues.append(f"- Contains {statistics['empty_arrays']} empty arrays that should be specified further")
    
    # Generate recommendations based on issues
    recommendations = [
        "- Use consistent naming conventions (camelCase or snake_case) throughout",
        "- Provide descriptions for all schema elements",
        "- Use appropriate type definitions and avoid using 'any' types",
        "- Implement proper validation constraints for numeric values"
    ]
    
    # Calculate approximate quality score
    quality_score = 5  # Default middle score
    if len(issues) > 5:
        quality_score = max(2, quality_score - len(issues) * 0.5)
    if 'description' in statistics and statistics['description'] > total_elements * 0.5:
        quality_score += 2
    
    quality_score = min(10, max(1, quality_score))
    
    # Generate the analysis text
    analysis = f"""
    ## Schema Analysis Summary
    
    This schema contains approximately {total_elements} elements. The main naming conventions appear to be {', '.join(pattern_keys[:3])}.
    
    ## Issues Identified
    {chr(10).join(issues) if issues else "No major issues identified with basic analysis."}
    
    ## Recommendations
    {chr(10).join(recommendations)}
    
    ## Quality Assessment
    Based on basic heuristics, the schema quality score is {quality_score:.1f}/10.
    """
    
    return analysis

def generate_ai_analysis(schema, statistics, is_large=False):
    """
    Generate an analysis of the schema using simulated AI response.
    In a production environment, this would call a real AI API.
    """
    # Simplistic AI simulation based on schema statistics
    naming_patterns = statistics['naming_patterns']
    element_types = statistics['element_types']
    total_elements = statistics['total_elements']
    
    # For this example, we'll generate a synthetic analysis
    pattern_names = list(naming_patterns.keys())
    primary_convention = max(naming_patterns.items(), key=lambda x: x[1])[0] if naming_patterns else "unclear"
    
    # Identify potential issues
    issues = []
    
    # Check naming consistency
    if len(pattern_names) > 2:
        issues.append({
            "description": f"Inconsistent naming conventions detected: {', '.join(pattern_names[:3])}",
            "severity": 3
        })
    
    # Check for type diversity
    type_ratio = element_types.get('string', 0) / total_elements if total_elements > 0 else 0
    if type_ratio > 0.8:
        issues.append({
            "description": "Over-reliance on string types (80%+ of elements). Consider using more specific types.",
            "severity": 2
        })
    
    # Check for structural depth
    if element_types.get('object', 0) < total_elements * 0.1:
        issues.append({
            "description": "Schema structure appears flat with limited nesting. Consider organizing related fields into objects.",
            "severity": 2
        })
    
    # Generate recommendations
    recommendations = [
        f"Standardize on {primary_convention} naming convention across all fields",
        "Add comprehensive descriptions to all fields relevant to nuclear industry context",
        "Implement proper validation constraints for critical numeric values",
        "Group related fields into logical objects to improve schema organization"
    ]
    
    # Calculate quality score
    base_score = 6
    issue_penalty = sum(issue['severity'] for issue in issues) * 0.3
    has_descriptions = True  # This would be calculated from actual schema
    has_constraints = element_types.get('number', 0) > 0  # Simplified check
    
    quality_score = base_score - issue_penalty
    if has_descriptions:
        quality_score += 1.5
    if has_constraints:
        quality_score += 1.5
    
    quality_score = min(10, max(1, round(quality_score * 10) / 10))
    
    # For a large schema with limited analysis
    if is_large:
        return f"""
        ## Schema Analysis Summary
        
        This is a large schema with approximately {total_elements} elements. Analysis is based on a representative sample.
        The predominant naming convention appears to be {primary_convention}.
        
        ## Issues Identified
        {chr(10).join([f"- {issue['description']} (Severity: {issue['severity']})" for issue in issues])if issues else "No major issues identified in the sample."}
        
        ## Recommendations
        {chr(10).join([f"- {rec}" for rec in recommendations])}
        
        ## Quality Assessment
        Based on the sample analysis, the estimated schema quality score is {quality_score:.1f}/10.
        
        ## Improved Schema
        Due to the large size of the schema, a complete improved version cannot be generated.
        Please apply the recommendations to improve the schema quality.
        """
    
    # For normal-sized schemas
    return f"""
    ## Schema Analysis Summary
    
    This schema contains {total_elements} elements and appears to be for a nuclear industry application.
    The predominant naming convention is {primary_convention}, with {len(naming_patterns)} different patterns detected.
    
    ## Issues Identified
    {chr(10).join([f"- {issue['description']} (Severity: {issue['severity']})" for issue in issues]) if issues else "No major issues identified."}
    
    ## Recommendations
    {chr(10).join([f"- {rec}" for rec in recommendations])}
    
    ## Quality Assessment
    The overall schema quality score is {quality_score:.1f}/10.
    
    ## Improved Schema
    {json.dumps(schema, indent=2)}  # In a real implementation, this would be an improved version
    """

def extract_report_data(analysis_text, original_schema):
    """Extract report data from the analysis text"""
    # Initialize the report data structure
    report_data = {
        'summary': '',
        'issues': [],
        'recommendations': [],
        'improved_schema': original_schema,  # Default to original schema
        'quality_score': 5.0  # Default score
    }
    
    # Extract summary - everything between "Summary" and "Issues"
    summary_match = re.search(r'##\s*(?:Schema\s*)?Analysis\s*Summary(.*?)(?=##|$)', analysis_text, re.DOTALL)
    if summary_match:
        report_data['summary'] = summary_match.group(1).strip()
    
    # Extract issues - extract items that start with "-" or numbered items
    issues_match = re.search(r'##\s*Issues\s*Identified(.*?)(?=##|$)', analysis_text, re.DOTALL)
    if issues_match:
        issues_text = issues_match.group(1).strip()
        issue_items = re.findall(r'[-\*•]\s*(.*?)(?=\n[-\*•]|\n\n|$)', issues_text, re.DOTALL)
        
        for issue in issue_items:
            issue = issue.strip()
            if not issue:
                continue
                
            # Check if severity is mentioned
            severity_match = re.search(r'\(Severity:\s*(\d+)\)', issue)
            severity = int(severity_match.group(1)) if severity_match else 3
            
            # Remove severity from description if present
            if severity_match:
                issue = issue.replace(severity_match.group(0), '').strip()
                
            report_data['issues'].append({
                'description': issue,
                'severity': severity
            })
    
    # Extract recommendations
    recommendations_match = re.search(r'##\s*Recommendations(.*?)(?=##|$)', analysis_text, re.DOTALL)
    if recommendations_match:
        recommendations_text = recommendations_match.group(1).strip()
        recommendation_items = re.findall(r'[-\*•]\s*(.*?)(?=\n[-\*•]|\n\n|$)', recommendations_text, re.DOTALL)
        
        for recommendation in recommendation_items:
            recommendation = recommendation.strip()
            if recommendation:
                report_data['recommendations'].append(recommendation)
    
    # Extract quality score
    quality_match = re.search(r'quality\s*(?:score|assessment).*?(\d+\.?\d*)(?:\s*\/\s*10)?', analysis_text, re.IGNORECASE)
    if quality_match:
        try:
            report_data['quality_score'] = float(quality_match.group(1))
        except ValueError:
            pass  # Keep default if conversion fails
    
    # Extract improved schema if available
    # This is complex since we need to find valid JSON. In a production system, 
    # you'd want a more robust method to extract this.
    improved_schema_match = re.search(r'##\s*Improved\s*Schema(.*?)(?=##|$)', analysis_text, re.DOTALL)
    if improved_schema_match:
        schema_text = improved_schema_match.group(1).strip()
        
        # Look for a JSON object in the text
        try:
            # Try to find JSON-like structure
            json_match = re.search(r'(\{.*\})', schema_text, re.DOTALL)
            if json_match:
                improved_schema = json.loads(json_match.group(1))
                report_data['improved_schema'] = improved_schema
        except Exception as e:
            app.logger.error(f"Failed to parse improved schema: {str(e)}")
            # If parsing fails, keep the original schema
    
    return report_data

def count_schema_elements(schema):
    """Count the total number of elements in a schema"""
    total = 0
    
    def traverse(obj):
        nonlocal total
        if isinstance(obj, dict):
            total += len(obj)
            for value in obj.values():
                traverse(value)
        elif isinstance(obj, list):
            total += len(obj)
            for item in obj:
                traverse(item)
    
    traverse(schema)
    return total

def analyze_naming_patterns(schema):
    """Analyze naming patterns in the schema keys"""
    patterns = {
        "camelCase": 0,
        "snake_case": 0,
        "PascalCase": 0,
        "kebab-case": 0,
        "UPPER_CASE": 0,
        "other": 0
    }
    
    def is_camel_case(s):
        return (s and s[0].islower() and 
                '_' not in s and 
                '-' not in s and 
                any(c.isupper() for c in s))
    
    def is_snake_case(s):
        return (s and 
                '_' in s and 
                all(c.islower() or c == '_' or c.isdigit() for c in s))
    
    def is_pascal_case(s):
        return (s and s[0].isupper() and 
                '_' not in s and 
                '-' not in s)
    
    def is_kebab_case(s):
        return (s and 
                '-' in s and 
                all(c.islower() or c == '-' or c.isdigit() for c in s))
    
    def is_upper_case(s):
        return (s and 
                all(c.isupper() or c == '_' or c.isdigit() for c in s) and 
                '_' in s)
    
    def traverse(obj, level=0):
        if isinstance(obj, dict):
            for key in obj:
                # Skip special keys like metadata
                if key.startswith('$') or key in ('id', 'type', 'properties'):
                    continue
                
                if is_camel_case(key):
                    patterns["camelCase"] += 1
                elif is_snake_case(key):
                    patterns["snake_case"] += 1
                elif is_pascal_case(key):
                    patterns["PascalCase"] += 1
                elif is_kebab_case(key):
                    patterns["kebab-case"] += 1
                elif is_upper_case(key):
                    patterns["UPPER_CASE"] += 1
                else:
                    patterns["other"] += 1
                
                traverse(obj[key], level + 1)
        elif isinstance(obj, list):
            for item in obj:
                traverse(item, level + 1)
    
    traverse(schema)
    
    # Remove patterns with zero count
    return {k: v for k, v in patterns.items() if v > 0}

def analyze_element_types(schema):
    """Analyze the types of elements in the schema"""
    types = {
        "object": 0,
        "array": 0,
        "string": 0,
        "number": 0,
        "integer": 0,
        "boolean": 0,
        "null": 0,
        "any": 0  # for unspecified types
    }
    
    empty_arrays = 0
    
    def traverse(obj):
        nonlocal empty_arrays
        
        if isinstance(obj, dict):
            types["object"] += 1
            
            # Check if this is a JSON Schema type definition
            if "type" in obj:
                if isinstance(obj["type"], str):
                    if obj["type"] in types:
                        types[obj["type"]] += 1
                elif isinstance(obj["type"], list):
                    # Multiple types possible
                    for t in obj["type"]:
                        if t in types:
                            types[t] += 1
                    types["any"] += 1  # Count as "any" type if multiple types
            
            # Check for empty arrays
            if "items" in obj and isinstance(obj.get("items"), list) and len(obj.get("items", [])) == 0:
                empty_arrays += 1
            
            # Traverse children
            for key, value in obj.items():
                if key not in ("type", "required", "description"):  # Skip schema keywords
                    traverse(value)
        
        elif isinstance(obj, list):
            types["array"] += 1
            if len(obj) == 0:
                empty_arrays += 1
            for item in obj:
                traverse(item)
                
    traverse(schema)
    
    # Add empty arrays count if any found
    if empty_arrays > 0:
        types["empty_arrays"] = empty_arrays
        
    # Remove types with zero count
    return {k: v for k, v in types.items() if v > 0}

@app.route('/generate-report', methods=['POST'])
def api_generate_report():
    try:
        data = request.get_json()
        if not data or 'schema' not in data:
            return jsonify({'success': False, 'message': 'No schema provided'}), 400
        
        schema = data.get('schema')
        filename = data.get('filename', '')
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        report_tasks[task_id] = {
            'status': 'pending',
            'progress': 0,
            'message': 'Initializing report generation...',
            'schema': schema,
            'filename': filename,
            'report': None,
            'error': None,
            'start_time': time.time()
        }
        
        # Start background thread for processing
        thread = threading.Thread(
            target=generate_schema_report_async,
            args=(task_id, schema, filename)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Report generation started',
            'task_id': task_id
        })
        
    except Exception as e:
        app.logger.error(f"Error starting report generation: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/report-status/<task_id>', methods=['GET'])
def report_status(task_id):
    if task_id not in report_tasks:
        return jsonify({
            'status': 'error',
            'message': 'Report task not found'
        }), 404
    
    task = report_tasks[task_id]
    
    # If task is completed, include the report data
    if task['status'] == 'completed':
        response = {
            'status': 'completed',
            'progress': 100,
            'message': 'Report generation complete',
        }
        
        # Include report data if available
        if task['report']:
            response['report'] = task['report']
        
        # Clean up old tasks after 1 hour
        current_time = time.time()
        if 'start_time' in task and (current_time - task['start_time']) > 3600:
            # Keep the report ID but remove the large schema data to free memory
            task['schema'] = None
            
        return jsonify(response)
    
    # If task errored out
    elif task['status'] == 'error':
        return jsonify({
            'status': 'error',
            'progress': task['progress'],
            'message': task['error'] or 'An error occurred during report generation'
        })
    
    # If task is still running
    else:
        return jsonify({
            'status': task['status'],
            'progress': task['progress'],
            'message': task['message']
        })

@app.route('/download-schema/<report_id>', methods=['GET'])
def download_schema(report_id):
    """Download the improved schema"""
    try:
        # Find the report file
        report_files = [f for f in os.listdir(app.config['REPORTS_FOLDER']) if report_id in f]
        
        if not report_files:
            return jsonify({
                'error': 'Report not found',
                'message': 'The requested report was not found.'
            }), 404
            
        report_path = os.path.join(app.config['REPORTS_FOLDER'], report_files[0])
        
        # Read the report
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        # Extract the improved schema
        improved_schema = report_data['report_data']['improved_schema']
        
        # Create a temporary file for download
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        temp_filename = temp_file.name
        
        with open(temp_filename, 'w') as f:
            json.dump(improved_schema, f, indent=2)
        
        # Get original filename if available, otherwise use report ID
        original_filename = report_data.get('original_filename', f'improved_schema_{report_id}.json')
        if not original_filename.endswith('.json'):
            original_filename += '.improved.json'
        
        return send_file(
            temp_filename,
            mimetype='application/json',
            as_attachment=True,
            download_name=original_filename
        )
            
    except Exception as e:
        print(f"Error downloading schema: {str(e)}")
        return jsonify({
            'error': str(e),
            'message': f'An error occurred while downloading the schema: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 