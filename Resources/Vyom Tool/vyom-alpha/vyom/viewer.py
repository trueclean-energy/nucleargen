# Modify your viewer.py to use the LLM service

# Add this import at the top of viewer.py
import os
import sys
import json
import uuid
import re
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union
import webbrowser
import tempfile
import logging
from . import llm_service
import shutil
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add this function to handle prompt processing using LLM
def handle_prompt_with_llm(prompt: str, data: Optional[Dict[str, Any]] = None, output_dir: Optional[str] = None, browser: bool = False) -> str:
    """
    Handle prompt processing using LLM.
    
    Args:
        prompt: User's prompt for visualization
        data: Optional data dictionary
        output_dir: Optional output directory
        browser: Whether to open in browser
        
    Returns:
        Path to generated HTML file
    """
    try:
        # Create data summary
        data_summary = create_data_summary(data)
        
        # Check for critical errors in data summary
        if data_summary.get("errors"):
            error_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Data Processing Error</title>
    <style>
        body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; line-height: 1.6; }}
        .error-container {{ background-color: #fff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 20px; margin-top: 20px; }}
        h1 {{ color: #e74c3c; margin-top: 0; }}
        .error {{ color: #e74c3c; padding: 15px; border-left: 4px solid #e74c3c; background-color: #fef5f5; margin: 20px 0; }}
        .warning {{ color: #f39c12; padding: 15px; border-left: 4px solid #f39c12; background-color: #fff9f0; margin: 20px 0; }}
        .help {{ background-color: #f7f9fb; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }}
        .data-summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin: 20px 0; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="error-container">
        <h1>Data Processing Errors Detected</h1>
        
        <div class="error">
            <h3>Errors:</h3>
            <ul>
                {chr(10).join(f"<li>{error}</li>" for error in data_summary.get("errors", []))}
            </ul>
        </div>
        
        {f'''
        <div class="warning">
            <h3>Warnings:</h3>
            <ul>
                {chr(10).join(f"<li>{warning}</li>" for warning in data_summary.get("warnings", []))}
            </ul>
        </div>
        ''' if data_summary.get("warnings") else ""}
        
        <div class="help">
            <h3>Troubleshooting Suggestions:</h3>
            <ul>
                <li>Check that your SAPHIRE data is properly formatted</li>
                <li>Verify that all required components are present in the model</li>
                <li>Ensure that the data structure matches the expected schema</li>
                <li>Try running without the --use-llm flag to see the raw data structure</li>
            </ul>
        </div>
        
        <div class="data-summary">
            <h3>Available Data Summary:</h3>
            <pre>{json.dumps(data_summary.get("counts", {}), indent=2)}</pre>
        </div>
    </div>
</body>
</html>"""
            
            if output_dir:
                return _save_and_open_html(error_html, output_dir, browser)
            return error_html
        
        # Create LLM service
        llm_service_name = os.environ.get("LLM_SERVICE", "together")
        llm_service_instance = llm_service.create_llm_service(llm_service_name)
        
        try:
            # First stage: Analyze data and create visualization plan
            plan = llm_service_instance.summarize_data(prompt, data_summary)
            
            # Extract needed data based on plan
            focused_data = extract_needed_data(data, plan)
            
            # Second stage: Generate complete visualization
            html = llm_service_instance.generate_complete_visualization(prompt, focused_data, plan)
            
            # Save and return the visualization
            if output_dir:
                return _save_and_open_html(html, output_dir, browser)
            return html
            
        except Exception as e:
            # Generate fallback visualization with error information
            error_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>LLM Visualization Error</title>
    <style>
        body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; line-height: 1.6; }}
        .error-container {{ background-color: #fff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 20px; margin-top: 20px; }}
        h1 {{ color: #e74c3c; margin-top: 0; }}
        .error {{ color: #e74c3c; padding: 15px; border-left: 4px solid #e74c3c; background-color: #fef5f5; margin: 20px 0; }}
        .help {{ background-color: #f7f9fb; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }}
        .fallback {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="error-container">
        <h1>LLM Visualization Error</h1>
        
        <div class="error">
            <p><strong>Error message:</strong> {str(e)}</p>
        </div>
        
        <div class="help">
            <h3>Troubleshooting Suggestions:</h3>
            <ul>
                <li>Check that your API keys are properly configured</li>
                <li>Verify that the LLM service ({llm_service_name}) is available</li>
                <li>Try a more specific prompt that describes the visualization you want</li>
                <li>Check the log files for more detailed error information</li>
            </ul>
        </div>
        
        <div class="fallback">
            <h3>Fallback Visualization</h3>
            <p>While the LLM visualization failed, here's a basic overview of your data:</p>
            <pre>{json.dumps(data_summary, indent=2)}</pre>
        </div>
    </div>
</body>
</html>"""
            
            if output_dir:
                return _save_and_open_html(error_html, output_dir, browser)
            return error_html
            
    except Exception as e:
        # Handle any unexpected errors
        error_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Unexpected Error</title>
    <style>
        body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; line-height: 1.6; }}
        .error-container {{ background-color: #fff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 20px; margin-top: 20px; }}
        h1 {{ color: #e74c3c; margin-top: 0; }}
        .error {{ color: #e74c3c; padding: 15px; border-left: 4px solid #e74c3c; background-color: #fef5f5; margin: 20px 0; }}
        .help {{ background-color: #f7f9fb; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="error-container">
        <h1>Unexpected Error</h1>
        
        <div class="error">
            <p><strong>Error message:</strong> {str(e)}</p>
        </div>
        
        <div class="help">
            <h3>Troubleshooting Suggestions:</h3>
            <ul>
                <li>Check that your input data is valid</li>
                <li>Verify that all required dependencies are installed</li>
                <li>Check the log files for more detailed error information</li>
                <li>Try running the command without the --use-llm flag</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
        
        if output_dir:
            return _save_and_open_html(error_html, output_dir, browser)
        return error_html

def generate_mermaid_html(mermaid_code: str, explanation: str = "") -> str:
    """
    Generate HTML with embedded mermaid diagram
    
    Args:
        mermaid_code: Mermaid diagram code
        explanation: Optional explanation of the diagram
        
    Returns:
        HTML string
    """
    explanation_html = f"""
    <div class="explanation">
        <h3>Explanation</h3>
        <p>{explanation}</p>
    </div>
    """ if explanation else ""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Generated Diagram</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/9.4.3/mermaid.min.js"></script>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            h2 {{ color: #2c3e50; margin-top: 0; }}
            .diagram-container {{ 
                width: 100%; 
                overflow: auto;
                margin: 20px 0;
                padding: 20px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                background-color: #f8f9fa;
            }}
            .explanation {{
                margin: 20px 0;
                padding: 15px;
                background-color: #f0f4f8;
                border-left: 4px solid #3498db;
                border-radius: 3px;
            }}
            .explanation h3 {{
                margin-top: 0;
                color: #3498db;
            }}
        </style>
    </head>
    <body>
        <h2>Generated Diagram</h2>
        {explanation_html}
        <div class="diagram-container">
            <pre class="mermaid">
{mermaid_code}
            </pre>
        </div>
        <script>
            mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
        </script>
    </body>
    </html>
    """
    
    return html_content

# Modify your existing handle_prompt function to use the LLM service
def handle_prompt(prompt: str, data: Optional[Dict[str, Any]] = None, output_dir: Optional[str] = "data/visual", browser: bool = False) -> str:
    """
    Generate visualizations based on user prompt
    
    Args:
        prompt: User text prompt describing the visualization
        data: Optional data to visualize
        output_dir: Directory to save visualization file
        browser: Whether to open in browser
        
    Returns:
        HTML string containing the visualization or file path if output_dir is specified
    """
    # Check if LLM should be used
    use_llm = os.environ.get("USE_LLM", "false").lower() == "true"
    
    if use_llm:
        try:
            logger.info("Using LLM for visualization generation")
            return handle_prompt_with_llm(prompt, data, output_dir, browser)
        except Exception as e:
            logger.error(f"Error using LLM: {e}")
            logger.info("Falling back to rule-based processing")
    
    # If LLM is disabled or fails, fall back to the rule-based approach
    import re
    from datetime import datetime
    
    # Rule-based prompt analysis
    visualization_type = "generic"
    
    if re.search(r'fault\s*tree', prompt, re.IGNORECASE):
        visualization_type = "fault_tree"
    elif re.search(r'event\s*tree', prompt, re.IGNORECASE):
        visualization_type = "event_tree"
    elif re.search(r'sequence', prompt, re.IGNORECASE):
        visualization_type = "sequence"
    elif re.search(r'(flow\s*chart|diagram|relationship)', prompt, re.IGNORECASE):
        visualization_type = "diagram"
    
    # Generate timestamp for output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate visualization based on type
    if visualization_type == "fault_tree" and data:
        html_content = visualize_saphire_data(data, output_dir=None, browser=False, 
                                            visualization_type="fault_tree")
    elif visualization_type == "event_tree" and data:
        html_content = visualize_saphire_data(data, output_dir=None, browser=False, 
                                            visualization_type="event_tree")
    elif visualization_type == "sequence" and data:
        html_content = visualize_saphire_data(data, output_dir=None, browser=False, 
                                            visualization_type="sequence")
    elif visualization_type == "diagram" and data:
        html_content = visualize_saphire_data(data, output_dir=None, browser=False, 
                                            visualization_type="diagram")
    else:
        # Fallback to generic visualization
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Vyom Visualization</title>
    <style>
        body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Overview</h1>
        <pre>{json.dumps(data, indent=2)}</pre>
    </div>
</body>
</html>"""
    
    # Save to file if output_dir is specified
    if output_dir:
        return _save_and_open_html(html_content, output_dir, browser)
    return html_content

# Helper function to save HTML and optionally open in browser
def _save_and_open_html(html_content: str, output_dir: str, browser: bool = False) -> str:
    """
    Save HTML content to a file and optionally open in browser
    
    Args:
        html_content: HTML content to save
        output_dir: Directory to save file in
        browser: Whether to open file in browser
        
    Returns:
        Path to the saved file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"visualization_{timestamp}.html")
    
    # Write HTML content to file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    # Open in browser if requested
    if browser:
        webbrowser.open(f"file://{os.path.abspath(output_file)}")
    
    return output_file

# Add the missing functions required for rule-based fallback

def extract_entities_from_prompt(prompt: str) -> List[Dict[str, Any]]:
    """
    Extract entities and their relationships from a natural language prompt
    
    Args:
        prompt: The user's prompt text
        
    Returns:
        List of entity dictionaries with name, type, and relationships
    """
    # Simple rule-based entity extraction
    entities = []
    
    # Find nouns (potential entities)
    words = re.findall(r'\b[A-Za-z]+\b', prompt)
    
    # Convert to title case for entity names
    potential_entities = [word.title() for word in words if len(word) > 3]
    
    # Remove duplicates
    potential_entities = list(dict.fromkeys(potential_entities))
    
    # Keep only the first 6 entities to avoid overly complex diagrams
    potential_entities = potential_entities[:6]
    
    # Create entity objects
    for i, entity in enumerate(potential_entities):
        entities.append({
            "name": entity,
            "type": "process" if i % 2 == 0 else "decision",
            "relationships": []
        })
    
    # Add some basic relationships between entities
    for i in range(len(entities) - 1):
        entities[i]["relationships"].append({
            "target": entities[i + 1]["name"],
            "label": "next" if entities[i+1]["type"] == "process" else "if true"
        })
    
    return entities

def generate_mermaid_code(diagram_type: str, entities: List[Dict[str, Any]]) -> str:
    """
    Generate Mermaid diagram code based on entities and their relationships
    
    Args:
        diagram_type: Type of diagram to generate
        entities: List of entity dictionaries
        
    Returns:
        Mermaid diagram code as string
    """
    mermaid_code = f"{diagram_type}\n"
    
    # Handle different diagram types
    if diagram_type.startswith("flowchart"):
        # Generate flowchart
        for entity in entities:
            entity_id = entity["name"].replace(" ", "_")
            entity_shape = "(" if entity["type"] == "process" else "{"
            entity_shape_end = ")" if entity["type"] == "process" else "}"
            
            mermaid_code += f"    {entity_id}{entity_shape}{entity['name']}{entity_shape_end}\n"
        
        # Add relationships
        for entity in entities:
            entity_id = entity["name"].replace(" ", "_")
            for rel in entity.get("relationships", []):
                target_id = rel["target"].replace(" ", "_")
                mermaid_code += f"    {entity_id} --> |{rel.get('label', '')}| {target_id}\n"
                
    elif diagram_type == "sequenceDiagram":
        # Generate sequence diagram
        participants = [entity["name"].replace(" ", "") for entity in entities]
        
        # Add participants
        for participant in participants:
            mermaid_code += f"    participant {participant}\n"
        
        # Add sequence of messages
        for i in range(len(entities) - 1):
            sender = entities[i]["name"].replace(" ", "")
            receiver = entities[i+1]["name"].replace(" ", "")
            message = entities[i].get("relationships", [{}])[0].get("label", "request")
            
            mermaid_code += f"    {sender}->>+{receiver}: {message}\n"
            if i < len(entities) - 2:
                mermaid_code += f"    {receiver}-->>-{sender}: response\n"
    
    elif diagram_type == "classDiagram":
        # Generate class diagram
        for entity in entities:
            entity_name = entity["name"].replace(" ", "")
            mermaid_code += f"    class {entity_name} {{\n"
            mermaid_code += f"        +id: string\n"
            mermaid_code += f"        +name: string\n"
            mermaid_code += f"        +process(): void\n"
            mermaid_code += f"    }}\n"
        
        # Add relationships
        for i in range(len(entities) - 1):
            entity1 = entities[i]["name"].replace(" ", "")
            entity2 = entities[i+1]["name"].replace(" ", "")
            mermaid_code += f"    {entity1} --> {entity2}\n"
    
    elif diagram_type == "erDiagram":
        # Generate ER diagram
        for entity in entities:
            entity_name = entity["name"].replace(" ", "")
            mermaid_code += f"    {entity_name} {{\n"
            mermaid_code += f"        string id PK\n"
            mermaid_code += f"        string name\n"
            mermaid_code += f"        datetime created_at\n"
            mermaid_code += f"    }}\n"
        
        # Add relationships
        for i in range(len(entities) - 1):
            entity1 = entities[i]["name"].replace(" ", "")
            entity2 = entities[i+1]["name"].replace(" ", "")
            mermaid_code += f"    {entity1} ||--o{{ {entity2} : has\n"
    
    return mermaid_code

def visualize_saphire_data(data, output_dir="data/visual", browser=True, use_legacy=False):
    """
    Generate an HTML visualization of SAPHIRE data and optionally open it in a browser.
    
    Args:
        data: Job data containing SAPHIRE schema
        output_dir: Directory to save visualization files
        browser: If True, open the visualization in a browser
        use_legacy: If True, use legacy visualization format
        
    Returns:
        str: Path to the generated HTML file
    """
    # Use the Viewer class for consistent visualization
    with Viewer(output_dir=output_dir, use_legacy=use_legacy) as viewer:
        output_file = viewer.visualize(data)
        
        # Open in browser if requested
        if browser:
            webbrowser.open('file://' + os.path.abspath(output_file))
        
        return output_file

def generate_fault_tree_diagram(fault_tree: Dict[str, Any]) -> str:
    """Generate Mermaid diagram code for a fault tree"""
    name = fault_tree.get("name", "Unnamed Fault Tree")
    description = fault_tree.get("description", "")
    gates = fault_tree.get("gates", [])
    
    # Create basic fault tree diagram
    diagram = "graph TD\n"
    diagram += f"    title[\"Fault Tree: {name}\"] --- top\n"
    
    # Add top gate
    if gates:
        top_gate = gates[0]
        diagram += f"    top[\"Top Event: {top_gate.get('name', 'Top')}\"] --- gate1\n"
        
        # Add intermediate gates (simplified)
        for i, gate in enumerate(gates[1:4], 1):  # Limit to 3 intermediate gates for simplicity
            gate_type = gate.get("type", "OR").upper()
            diagram += f"    gate{i}[\"{gate_type}: {gate.get('name', f'Gate {i}')}\"] --- event{i*2-1}\n"
            diagram += f"    gate{i} --- event{i*2}\n"
            
            # Add basic events for each gate
            diagram += f"    event{i*2-1}[\"Basic Event {i*2-1}\"] \n"
            diagram += f"    event{i*2}[\"Basic Event {i*2}\"] \n"
    else:
        diagram += f"    top[\"Top Event\"] --- empty[\"No Gates Defined\"]\n"
    
    return diagram

def generate_event_tree_diagram(event_tree: Dict[str, Any]) -> str:
    """Generate Mermaid diagram code for an event tree"""
    name = event_tree.get("name", "Unnamed Event Tree")
    initiating_event = event_tree.get("initiating_event", "Unknown")
    
    # Create basic event tree diagram
    diagram = "graph LR\n"
    diagram += f"    title[\"Event Tree: {name}\"] --- init\n"
    diagram += f"    init[\"Initiating Event: {initiating_event}\"] --- branch1\n"
    
    # Add simplified branches
    diagram += "    branch1{\"Branch 1\"} -->|Success| seq1\n"
    diagram += "    branch1 -->|Failure| branch2\n"
    diagram += "    branch2{\"Branch 2\"} -->|Success| seq2\n"
    diagram += "    branch2 -->|Failure| seq3\n"
    
    # Add end states
    diagram += "    seq1[\"Sequence 1: OK\"]\n"
    diagram += "    seq2[\"Sequence 2: CD\"]\n"
    diagram += "    seq3[\"Sequence 3: CD\"]\n"
    
    return diagram

def generate_project_overview(saphire_data: Dict[str, Any]) -> str:
    """Generate Mermaid diagram code for a project overview"""
    # Extract counts
    fault_tree_count = len(saphire_data.get("fault_trees", []))
    event_tree_count = len(saphire_data.get("event_trees", []))
    basic_event_count = len(saphire_data.get("basic_events", []))
    sequence_count = len(saphire_data.get("sequences", []))
    
    # Generate overview diagram
    diagram = "graph TD\n"
    diagram += "    Project[\"SAPHIRE Project\"] --> FT\n"
    diagram += "    Project --> ET\n"
    diagram += "    Project --> BE\n"
    diagram += "    Project --> Seq\n"
    
    diagram += f"    FT[\"Fault Trees: {fault_tree_count}\"]\n"
    diagram += f"    ET[\"Event Trees: {event_tree_count}\"]\n"
    diagram += f"    BE[\"Basic Events: {basic_event_count}\"]\n"
    diagram += f"    Seq[\"Sequences: {sequence_count}\"]\n"
    
    return diagram

def generate_html_for_saphire(data):
    """
    Generate HTML content for SAPHIRE data visualization.
    
    Args:
        data: SAPHIRE schema data
        
    Returns:
        str: HTML content
    """
    # Get SAPHIRE data - try different possible locations
    saphire_data = data.get("saphire_data", {})
    if not saphire_data and "data" in data:
        saphire_data = data["data"]
    
    # Extract project information 
    project = {}
    if "project" in saphire_data:
        project = saphire_data["project"]
    elif "project" in data:
        project = data["project"]
    
    project_name = project.get("name", "Not specified")
    project_desc = project.get("description", "")
    
    # Generate HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SAPHIRE Model Visualization</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.30.1/min/vs/loader.js"></script>
        <style>
            :root {{
                --primary-color: #3b71ca;
                --background-color: #f5f5f5;
                --card-background: #ffffff;
                --header-color: #2c3e50;
                --text-primary: #333333;
                --text-secondary: #6c757d;
                --border-color: #dee2e6;
                --hover-color: #f8f9fa;
            }}
            
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: var(--text-primary);
                background-color: var(--background-color);
                margin: 0;
                padding: 0;
            }}
            
            .header {{
                background-color: var(--header-color);
                color: white;
                padding: 1rem;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .container {{
                display: flex;
                height: calc(100vh - 60px);
            }}
            
            .main-content {{
                flex: 1;
                overflow-y: auto;
                padding: 1.5rem;
            }}
            
            .json-panel {{
                width: 40%;
                border-left: 1px solid var(--border-color);
                display: flex;
                flex-direction: column;
                resize: horizontal;
                overflow: auto;
                min-width: 200px;
                max-width: 80%;
            }}
            
            .panel-header {{
                padding: 0.75rem;
                background-color: var(--header-color);
                color: white;
            }}
            
            .monaco-container {{
                flex: 1;
                overflow: hidden;
            }}
            
            .card {{
                background-color: var(--card-background);
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                margin-bottom: 1.5rem;
                overflow: hidden;
            }}
            
            .card-header {{
                padding: 1rem;
                background-color: var(--primary-color);
                color: white;
                font-weight: 500;
            }}
            
            .card-body {{
                padding: 1rem;
            }}
            
            .summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-bottom: 1.5rem;
            }}
            
            .summary-item {{
                background-color: var(--card-background);
                padding: 1.25rem;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                text-align: center;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .summary-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            
            .summary-item h3 {{
                color: var(--text-secondary);
                font-size: 0.875rem;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
            }}
            
            .summary-item p {{
                font-size: 1.75rem;
                font-weight: 600;
                color: var(--primary-color);
            }}
            
            .section {{
                margin-top: 2rem;
            }}
            
            .section-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-bottom: 0.5rem;
                margin-bottom: 1rem;
                border-bottom: 1px solid var(--border-color);
            }}
            
            .section-title {{
                font-size: 1.25rem;
                font-weight: 600;
                color: var(--text-primary);
            }}
            
            .list-container {{
                max-height: 300px;
                overflow-y: auto;
                border: 1px solid var(--border-color);
                border-radius: 4px;
            }}
            
            .list-item {{
                padding: 0.75rem 1rem;
                border-bottom: 1px solid var(--border-color);
                cursor: pointer;
            }}
            
            .list-item:last-child {{
                border-bottom: none;
            }}
            
            .list-item:hover {{
                background-color: var(--hover-color);
            }}
            
            .list-item.active {{
                background-color: var(--hover-color);
                border-left: 3px solid var(--primary-color);
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>SAPHIRE Model Visualization</h2>
        </div>
        
        <div class="container">
            <div class="main-content">
                <div class="card">
                    <div class="card-header">Project Information</div>
                    <div class="card-body">
                        <p><strong>Project Name:</strong> {project_name}</p>
                        <p><strong>Description:</strong> {project_desc}</p>
                    </div>
                </div>
                
                <div class="summary">
                    <div class="summary-item" data-section="fault-trees">
                        <h3>Fault Trees</h3>
                        <p>{len(saphire_data.get("fault_trees", []))}</p>
                    </div>
                    <div class="summary-item" data-section="event-trees">
                        <h3>Event Trees</h3>
                        <p>{len(saphire_data.get("event_trees", []))}</p>
                    </div>
                    <div class="summary-item" data-section="basic-events">
                        <h3>Basic Events</h3>
                        <p>{len(saphire_data.get("basic_events", []))}</p>
                    </div>
                    <div class="summary-item" data-section="end-states">
                        <h3>End States</h3>
                        <p>{len(saphire_data.get("end_states", []))}</p>
                    </div>
                </div>
                
                <div class="sections">
                    <div id="fault-trees" class="section">
                        <div class="section-header">
                            <h3 class="section-title">Fault Trees</h3>
                        </div>
                        <div class="list-container" id="fault-trees-list"></div>
                    </div>
                    
                    <div id="event-trees" class="section">
                        <div class="section-header">
                            <h3 class="section-title">Event Trees</h3>
                        </div>
                        <div class="list-container" id="event-trees-list"></div>
                    </div>
                    
                    <div id="basic-events" class="section">
                        <div class="section-header">
                            <h3 class="section-title">Basic Events</h3>
                        </div>
                        <div class="list-container" id="basic-events-list"></div>
                    </div>
                    
                    <div id="end-states" class="section">
                        <div class="section-header">
                            <h3 class="section-title">End States</h3>
                        </div>
                        <div class="list-container" id="end-states-list"></div>
                    </div>
                </div>
            </div>
            
            <div class="json-panel">
                <div class="panel-header">Raw JSON</div>
                <div class="monaco-container" id="jsonEditor"></div>
            </div>
        </div>
        
        <script>
            // Store the SAPHIRE data
            const saphireData = {json.dumps(saphire_data)};
            
            // Function to populate a list with data
            function populateList(listId, items, idKey = 'id', descKey = 'description') {{
                const list = document.getElementById(listId);
                if (!list) return;
                
                items.forEach(item => {{
                    const div = document.createElement('div');
                    div.className = 'list-item';
                    div.innerHTML = `<strong>${{item[idKey] || 'Unnamed'}}</strong>`;
                    if (item[descKey]) {{
                        div.innerHTML += ` - ${{item[descKey]}}`;
                    }}
                    div.onclick = () => {{
                        // Highlight this item
                        document.querySelectorAll('.list-item').forEach(i => i.classList.remove('active'));
                        div.classList.add('active');
                        
                        // Update JSON view with this item's data
                        if (window.jsonEditor) {{
                            window.jsonEditor.setValue(JSON.stringify(item, null, 2));
                        }}
                    }};
                    list.appendChild(div);
                }});
            }}
            
            // Initialize Monaco editor
            require.config({{ paths: {{ 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.30.1/min/vs' }}}});
            require(['vs/editor/editor.main'], function() {{
                window.jsonEditor = monaco.editor.create(document.getElementById('jsonEditor'), {{
                    value: JSON.stringify(saphireData, null, 2),
                    language: 'json',
                    theme: 'vs',
                    automaticLayout: true,
                    readOnly: true
                }});
            }});
            
            // Populate lists when document is ready
            document.addEventListener('DOMContentLoaded', function() {{
                // Populate all lists
                populateList('fault-trees-list', saphireData.fault_trees || []);
                populateList('event-trees-list', saphireData.event_trees || []);
                populateList('basic-events-list', saphireData.basic_events || []);
                populateList('end-states-list', saphireData.end_states || []);
                
                // Add click handlers to summary items
                document.querySelectorAll('.summary-item').forEach(item => {{
                    item.addEventListener('click', function() {{
                        const section = this.getAttribute('data-section');
                        document.getElementById(section).scrollIntoView({{ behavior: 'smooth' }});
                    }});
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    return html_content

class Viewer:
    """A class to handle visualization of SAPHIRE model data."""
    
    def __init__(self, output_dir: str, use_legacy: bool = False):
        """
        Initialize the Viewer.
        
        Args:
            output_dir: Directory where visualization files will be saved
            use_legacy: Whether to use legacy visualization (True) or new HTML visualization (False)
        """
        self.output_dir = Path(output_dir)
        self.use_legacy = use_legacy
        self.temp_dir = None
        self.visual_dir = None
        self.comments_file = None
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up visualization directory
        self._setup_visual_dir()
        
    def _setup_visual_dir(self):
        """Set up the visualization directory structure."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.use_legacy:
            # Legacy visualization directory structure
            self.visual_dir = self.output_dir
            self.visual_dir.mkdir(exist_ok=True)
            
            # Create a temporary directory for processing
            self.temp_dir = Path(tempfile.mkdtemp())
            logger.info(f"Created temporary directory: {self.temp_dir}")
            
            # Copy required files to temp directory
            self._copy_required_files()
        else:
            # New HTML visualization directory structure
            self.visual_dir = self.output_dir
            self.visual_dir.mkdir(parents=True, exist_ok=True)
            
            # Create comments file
            self.comments_file = self.visual_dir / f"comments_{timestamp}.json"
            if not self.comments_file.exists():
                with open(self.comments_file, 'w') as f:
                    json.dump([], f)
    
    def _copy_required_files(self):
        """Copy required files for legacy visualization to temp directory."""
        try:
            # Get the directory containing this script
            current_dir = Path(__file__).parent
            
            # Copy required files
            required_files = [
                "saphire_visualization.html",
                "saphire_visualization.css",
                "saphire_visualization.js"
            ]
            
            for file in required_files:
                src = current_dir / file
                if src.exists():
                    shutil.copy2(src, self.temp_dir)
                else:
                    logger.warning(f"Required file not found: {file}")
                    
        except Exception as e:
            logger.error(f"Error copying required files: {e}")
            raise
    
    def _create_legacy_visualization(self, data: Dict[str, Any], output_file: str):
        """Create legacy visualization using the old method."""
        try:
            # Read the template HTML file
            template_path = self.temp_dir / "saphire_visualization.html"
            with open(template_path, 'r') as f:
                template = f.read()
            
            # Create a temporary HTML file with the data
            temp_html = self.temp_dir / "temp.html"
            with open(temp_html, 'w') as f:
                # Replace the saphireData placeholder with actual data
                html_content = template.replace(
                    '<script src="saphire_visualization.js"></script>',
                    f'<script>const saphireData = {json.dumps(data)};</script>\n<script src="saphire_visualization.js"></script>'
                )
                f.write(html_content)
            
            # Copy all required files to the output directory
            output_dir = Path(output_file).parent
            shutil.copy2(self.temp_dir / "saphire_visualization.css", output_dir / "saphire_visualization.css")
            shutil.copy2(self.temp_dir / "saphire_visualization.js", output_dir / "saphire_visualization.js")
            shutil.copy2(temp_html, output_file)
            
        except Exception as e:
            logger.error(f"Error creating legacy visualization: {e}")
            raise
    
    def _create_new_visualization(self, data: Dict[str, Any], output_file: str):
        """Create new HTML visualization using the modern template."""
        try:
            # Generate HTML content directly instead of using a template file
            # Extract SAPHIRE data from the data structure
            saphire_data = data.get("saphire_data", {})
            if not saphire_data and "data" in data:
                saphire_data = data["data"]
            
            # Extract project information
            project = {}
            if "project" in saphire_data:
                project = saphire_data["project"]
            elif "project" in data:
                project = data["project"]
            
            project_name = project.get("name", "Not specified")
            project_desc = project.get("description", "")
            job_id = data.get("job_id", "Unknown")
            
            # Count model elements
            fault_trees = saphire_data.get("fault_trees", [])
            event_trees = saphire_data.get("event_trees", [])
            basic_events = saphire_data.get("basic_events", [])
            end_states = saphire_data.get("end_states", [])
            sequences = saphire_data.get("sequences", [])
            
            fault_tree_count = len(fault_trees)
            event_tree_count = len(event_trees)
            basic_event_count = len(basic_events)
            end_state_count = len(end_states)
            sequence_count = len(sequences)
            
            # Generate HTML content
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAPHIRE Model Visualization</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 1rem;
            text-align: center;
        }}
        .container {{
            display: flex;
            height: calc(100vh - 60px);
            overflow: hidden;
        }}
        .main-panel {{
            flex: 3;
            overflow-y: auto;
            padding: 1rem;
        }}
        .json-panel {{
            flex: 2;
            background-color: #f8f9fa;
            border-left: 1px solid #ddd;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        .json-header {{
            background-color: #2c3e50;
            color: white;
            padding: 0.5rem 1rem;
        }}
        .json-content {{
            overflow-y: auto;
            padding: 1rem;
            flex-grow: 1;
            font-family: monospace;
            white-space: pre-wrap;
        }}
        .project-info {{
            background-color: white;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 1rem;
            margin-bottom: 1rem;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        .summary-item {{
            background-color: white;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 1rem;
            text-align: center;
        }}
        .summary-item h3 {{
            margin-top: 0;
            text-transform: uppercase;
            font-size: 0.9rem;
            color: #777;
        }}
        .summary-item p {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #3498db;
            margin: 0.5rem 0;
        }}
        .section {{
            background-color: white;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }}
        .section-header {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #eee;
            font-weight: bold;
        }}
        .section-content {{
            padding: 0 1rem;
        }}
        .item-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .item {{
            padding: 0.75rem 0;
            border-bottom: 1px solid #eee;
            cursor: pointer;
        }}
        .item:last-child {{
            border-bottom: none;
        }}
        .item:hover {{
            background-color: #f5f7fa;
        }}
        .comments {{
            background-color: white;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 1rem;
            margin-top: 1rem;
        }}
        .comment-input {{
            width: 100%;
            min-height: 60px;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 0.5rem;
            margin-bottom: 0.5rem;
        }}
        .comment-btn {{
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SAPHIRE Model Visualization</h1>
    </div>
    
    <div class="container">
        <div class="main-panel">
            <div class="project-info">
                <h2>Project Information</h2>
                <p><strong>Project Name:</strong> {project_name}</p>
                <p><strong>Description:</strong> {project_desc}</p>
            </div>
            
            <div class="summary">
                <div class="summary-item">
                    <h3>FAULT TREES</h3>
                    <p>{fault_tree_count}</p>
                </div>
                <div class="summary-item">
                    <h3>EVENT TREES</h3>
                    <p>{event_tree_count}</p>
                </div>
                <div class="summary-item">
                    <h3>BASIC EVENTS</h3>
                    <p>{basic_event_count}</p>
                </div>
                <div class="summary-item">
                    <h3>END STATES</h3>
                    <p>{end_state_count}</p>
                </div>
            </div>
            
            <div class="section">
                <div class="section-header">Fault Trees ({fault_tree_count})</div>
                <div class="section-content">
                    {self._generate_item_list_html(fault_trees, "fault-tree")}
                </div>
            </div>
            
            <div class="section">
                <div class="section-header">Event Trees ({event_tree_count})</div>
                <div class="section-content">
                    {self._generate_item_list_html(event_trees, "event-tree")}
                </div>
            </div>
            
            <div class="section">
                <div class="section-header">Basic Events ({basic_event_count})</div>
                <div class="section-content">
                    {self._generate_item_list_html(basic_events, "basic-event")}
                </div>
            </div>
            
            <div class="section">
                <div class="section-header">End States ({end_state_count})</div>
                <div class="section-content">
                    {self._generate_item_list_html(end_states, "end-state")}
                </div>
            </div>
            
            <div class="section">
                <div class="section-header">Sequences ({sequence_count})</div>
                <div class="section-content">
                    {self._generate_item_list_html(sequences, "sequence")}
                </div>
            </div>
            
            <div class="comments">
                <h3>Comments</h3>
                <textarea class="comment-input" placeholder="Add a comment..."></textarea>
                <button class="comment-btn">Add Comment</button>
            </div>
        </div>
        
        <div class="json-panel">
            <div class="json-header">Raw JSON</div>
            <div class="json-content" id="jsonDisplay"></div>
        </div>
    </div>
    
    <script>
        // Store the SAPHIRE data
        const saphireData = {json.dumps(saphire_data)};
        
        // Function to display JSON in the right panel
        function displayJson(obj) {{
            const jsonContent = document.getElementById('jsonDisplay');
            jsonContent.textContent = JSON.stringify(obj, null, 2);
        }}
        
        // Initialize with the full SAPHIRE data
        displayJson(saphireData);
        
        // Add click handlers to items
        document.querySelectorAll('.item').forEach(item => {{
            item.addEventListener('click', function() {{
                // Get the item data based on type and index
                const type = this.getAttribute('data-type');
                const index = parseInt(this.getAttribute('data-index'));
                
                let itemData;
                switch(type) {{
                    case 'fault-tree':
                        itemData = saphireData.fault_trees[index];
                        break;
                    case 'event-tree':
                        itemData = saphireData.event_trees[index];
                        break;
                    case 'basic-event':
                        itemData = saphireData.basic_events[index];
                        break;
                    case 'end-state':
                        itemData = saphireData.end_states[index];
                        break;
                    case 'sequence':
                        itemData = saphireData.sequences[index];
                        break;
                    default:
                        itemData = {{error: 'Unknown item type'}};
                }}
                
                // Display the item data
                displayJson(itemData);
                
                // Highlight the selected item
                document.querySelectorAll('.item').forEach(i => i.style.backgroundColor = '');
                this.style.backgroundColor = '#e9f7fe';
            }});
        }});
    </script>
</body>
</html>"""
            
            # Write the final HTML file
            with open(output_file, 'w') as f:
                f.write(html_content)
            
        except Exception as e:
            logger.error(f"Error creating new visualization: {e}")
            raise
    
    def _generate_item_list_html(self, items: List[Dict[str, Any]], item_type: str) -> str:
        """Generate HTML for a list of items."""
        if not items:
            return "<p>No items found in the model.</p>"
        
        html = "<ul class='item-list'>"
        
        for i, item in enumerate(items):
            item_id = item.get("id", f"Unnamed {item_type}")
            desc = item.get("description", "")
            
            html += f"<li class='item' data-type='{item_type}' data-index='{i}'>"
            html += f"<strong>{item_id}</strong>"
            if desc:
                html += f" - {desc}"
            html += "</li>"
        
        html += "</ul>"
        return html
    
    def visualize(self, data: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """
        Create a visualization of the SAPHIRE model data.
        
        Args:
            data: Dictionary containing the SAPHIRE model data
            output_file: Optional name for the output file. If not provided, a timestamped name will be used.
            
        Returns:
            Path to the created visualization file
        """
        try:
            # Generate output filename if not provided
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"saphire_visualization_{timestamp}.html"
            
            output_path = self.visual_dir / output_file
            
            # Create visualization based on selected method
            if self.use_legacy:
                self._create_legacy_visualization(data, output_path)
            else:
                self._create_new_visualization(data, output_path)
            
            logger.info(f"Created visualization at: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            raise
    
    def cleanup(self):
        """Clean up temporary files and directories."""
        try:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                logger.info("Cleaned up temporary directory")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()

def create_data_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a compact summary of SAPHIRE data for sending to LLM.
    
    Args:
        data: Full SAPHIRE data dictionary
        
    Returns:
        Dictionary with summarized data
    """
    try:
        # Extract SAPHIRE data from different possible locations
        saphire_data = data.get("saphire_data", {})
        if not saphire_data and "data" in data:
            saphire_data = data["data"]
        
        # Extract project info
        project = {}
        if "project" in saphire_data:
            project = saphire_data["project"]
        elif "project" in data:
            project = data["project"]
        
        # Create enhanced summary dictionary with error tracking
        summary = {
            "project": {
                "name": project.get("name", "Not specified"),
                "description": project.get("description", ""),
                "model_type": project.get("model_type", ""),
                "created_date": project.get("created_date", ""),
                "version": project.get("version", "")
            },
            "counts": {},
            "structure": {},
            "errors": [],  # Track any errors during processing
            "warnings": []  # Track any warnings during processing
        }
        
        # Add counts for each element type
        element_types = ["fault_trees", "event_trees", "basic_events", "end_states", "sequences"]
        for element_type in element_types:
            elements = saphire_data.get(element_type, [])
            if not isinstance(elements, list):
                summary["errors"].append(f"{element_type} is not a list")
                elements = []
            summary["counts"][element_type] = len(elements)
            
            # Add sample items for each type (up to 3)
            if elements:
                # For fault trees, include more detailed structure
                if element_type == "fault_trees" and len(elements) > 0:
                    try:
                        # Get the first fault tree with its full structure
                        fault_tree = elements[0]
                        
                        # Extract gate relationships to understand structure
                        gates = fault_tree.get("gates", [])
                        basic_events = []
                        
                        # Try to extract basic events linked to this fault tree
                        for gate in gates:
                            gate_inputs = gate.get("inputs", [])
                            for input_item in gate_inputs:
                                # Handle both string and dict inputs
                                if isinstance(input_item, dict):
                                    if input_item.get("type") == "basic-event":
                                        basic_events.append(input_item.get("id"))
                                elif isinstance(input_item, str):
                                    # Assume string inputs are basic event IDs
                                    basic_events.append(input_item)
                                else:
                                    summary["warnings"].append(f"Unexpected input type in gate: {type(input_item)}")
                        
                        summary["structure"]["sample_fault_tree"] = {
                            "id": fault_tree.get("id", ""),
                            "name": fault_tree.get("name", ""),
                            "description": fault_tree.get("description", ""),
                            "gates": gates[:5],  # Limit to first 5 gates
                            "linked_basic_events": basic_events[:10]  # Limit to first 10 basic events
                        }
                    except Exception as e:
                        summary["errors"].append(f"Error processing fault tree: {str(e)}")
                
                try:
                    # Add samples of all element types
                    summary[element_type + "_samples"] = [
                        {k: v for k, v in (item.items() if isinstance(item, dict) else {"id": item}.items())
                         if k in ["id", "name", "description", "type", "probability"]} 
                        for item in elements[:3]
                    ]
                except Exception as e:
                    summary["errors"].append(f"Error processing {element_type} samples: {str(e)}")
        
        # Add a sample of relationships if they exist
        if "relationships" in saphire_data:
            try:
                rel_sample = saphire_data["relationships"][:5] if len(saphire_data["relationships"]) > 5 else saphire_data["relationships"]
                summary["relationships_sample"] = rel_sample
            except Exception as e:
                summary["errors"].append(f"Error processing relationships: {str(e)}")
        
        # Add special structural information that helps visualization
        if "fault_trees" in saphire_data and len(saphire_data["fault_trees"]) > 0:
            try:
                # Get hierarchical structure information
                ft = saphire_data["fault_trees"][0]
                top_gate = None
                
                # Find the top gate
                for gate in ft.get("gates", []):
                    is_input = False
                    # Check if this gate is an input to another gate
                    for g in ft.get("gates", []):
                        for input_item in g.get("inputs", []):
                            if isinstance(input_item, dict):
                                if input_item.get("type") == "gate" and input_item.get("id") == gate.get("id"):
                                    is_input = True
                                    break
                            elif isinstance(input_item, str) and input_item == gate.get("id"):
                                is_input = True
                                break
                    
                    if not is_input:
                        top_gate = gate
                        break
                
                if top_gate:
                    summary["structure"]["top_gate"] = {
                        "id": top_gate.get("id", ""),
                        "type": top_gate.get("type", ""),
                        "name": top_gate.get("name", "")
                    }
            except Exception as e:
                summary["errors"].append(f"Error processing top gate: {str(e)}")
        
        return summary
        
    except Exception as e:
        # Return a minimal summary with error information if something goes wrong
        return {
            "project": {"name": "Error processing data"},
            "counts": {},
            "structure": {},
            "errors": [f"Critical error in data summary: {str(e)}"],
            "warnings": []
        }

def extract_needed_data(data: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract only the data elements needed for visualization based on the plan.
    
    Args:
        data: Full SAPHIRE data dictionary
        plan: Visualization plan from the first stage
        
    Returns:
        Dictionary with only the necessary data elements
    """
    # Get the list of needed elements
    needed_elements = plan.get("needed_data_elements", [])
    
    # Extract SAPHIRE data from different possible locations
    saphire_data = data.get("saphire_data", {})
    if not saphire_data and "data" in data:
        saphire_data = data["data"]
    
    # Extract project info
    project = {}
    if "project" in saphire_data:
        project = saphire_data["project"]
    elif "project" in data:
        project = data["project"]
    
    # Start with basic project info
    focused_data = {
        "project": project
    }
    
    # Add count information (this is always useful and small)
    focused_data["counts"] = {}
    for element_type in ["fault_trees", "event_trees", "basic_events", "end_states", "sequences"]:
        focused_data["counts"][element_type] = len(saphire_data.get(element_type, []))
    
    # Add specific elements if needed
    for element in needed_elements:
        if element in saphire_data:
            focused_data[element] = saphire_data[element]
        elif element == "basic_counts":
            # Already added the counts
            continue
        elif "all" in element:
            # If requesting all data of a type (e.g., "all_fault_trees")
            type_name = element.split("_", 1)[1]
            if type_name in saphire_data:
                focused_data[type_name] = saphire_data[type_name]
    
    return focused_data

def generate_fallback_visualization(data: Dict[str, Any]) -> str:
    """
    Generate a simple fallback visualization when LLM generation fails.
    
    Args:
        data: SAPHIRE data dictionary
        
    Returns:
        HTML string with basic visualization
    """
    # Extract SAPHIRE data
    saphire_data = data.get("saphire_data", {})
    if not saphire_data and "data" in data:
        saphire_data = data["data"]
    
    # Extract counts
    ft_count = len(saphire_data.get("fault_trees", []))
    et_count = len(saphire_data.get("event_trees", []))
    be_count = len(saphire_data.get("basic_events", []))
    es_count = len(saphire_data.get("end_states", []))
    seq_count = len(saphire_data.get("sequences", []))
    
    # Project info
    project = {}
    if "project" in saphire_data:
        project = saphire_data["project"]
    elif "project" in data:
        project = data["project"]
    
    project_name = project.get("name", "Not specified")
    project_desc = project.get("description", "")
    
    # Generate a D3.js bar chart of counts
    fallback_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>SAPHIRE Model Overview</title>
    <style>
        body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; }}
        h1, h2 {{ color: #2c3e50; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .chart-container {{ height: 400px; margin: 30px 0; }}
        .bar {{ fill: #3498db; }}
        .bar:hover {{ fill: #2980b9; }}
        .axis text {{ font-size: 12px; }}
        .axis path, .axis line {{ fill: none; stroke: #ccc; shape-rendering: crispEdges; }}
        .x-axis .domain {{ display: none; }}
        .info-box {{ background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>SAPHIRE Model Overview</h1>
        
        <div class="info-box">
            <h2>Project Information</h2>
            <p><strong>Name:</strong> {project_name}</p>
            <p><strong>Description:</strong> {project_desc}</p>
        </div>
        
        <h2>Model Components</h2>
        <div class="chart-container" id="chart"></div>
        
        <script>
            // Inline D3.js to avoid external dependencies
            // D3.js v7 (minified)
            {d3_library_code}
            
            // Create the chart
            const data = [
                {{ name: "Fault Trees", value: {ft_count} }},
                {{ name: "Event Trees", value: {et_count} }},
                {{ name: "Basic Events", value: {be_count} }},
                {{ name: "End States", value: {es_count} }},
                {{ name: "Sequences", value: {seq_count} }}
            ];
            
            // Set dimensions and margins
            const margin = {{top: 30, right: 30, bottom: 70, left: 60}};
            const width = 900 - margin.left - margin.right;
            const height = 400 - margin.top - margin.bottom;
            
            // Create SVG
            const svg = d3.select("#chart")
                .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", `translate(${{margin.left}},${{margin.top}})`);
            
            // X axis
            const x = d3.scaleBand()
                .range([0, width])
                .domain(data.map(d => d.name))
                .padding(0.2);
            
            svg.append("g")
                .attr("class", "x-axis")
                .attr("transform", `translate(0,${{height}}`)
                .call(d3.axisBottom(x))
                .selectAll("text")
                .attr("transform", "translate(-10,0)rotate(-45)")
                .style("text-anchor", "end");
            
            // Y axis
            const y = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.value) * 1.1])
                .range([height, 0]);
            
            svg.append("g")
                .attr("class", "y-axis")
                .call(d3.axisLeft(y));
            
            // Bars
            svg.selectAll("rect")
                .data(data)
                .join("rect")
                .attr("class", "bar")
                .attr("x", d => x(d.name))
                .attr("y", d => y(d.value))
                .attr("width", x.bandwidth())
                .attr("height", d => height - y(d.value))
                .append("title")
                .text(d => `${{d.name}}: ${{d.value}}`);
            
            // Add labels
            svg.selectAll(".label")
                .data(data)
                .join("text")
                .attr("class", "label")
                .attr("text-anchor", "middle")
                .attr("x", d => x(d.name) + x.bandwidth()/2)
                .attr("y", d => y(d.value) - 5)
                .text(d => d.value);
        </script>
    </div>
</body>
</html>
"""
    
    # Replace the d3_library_code placeholder with actual minified D3 code or a CDN link
    # You can inline a minified version of D3.js here or use:
    d3_code = '<script src="https://d3js.org/d3.v7.min.js"></script>'
    fallback_html = fallback_html.replace('{d3_library_code}', d3_code)
    
    return fallback_html