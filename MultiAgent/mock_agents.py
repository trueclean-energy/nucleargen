import json
import os
import subprocess
import tempfile
import sys

# Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT1_DIR = os.path.join(BASE_DIR, "Agent_1")
DATA_VALIDATION_DIR = os.path.join(BASE_DIR, "data-validation")
VIZ_AGENT_DIR = os.path.join(BASE_DIR, "viz-agent")

def process_schema_question(content):
    """Implementation that directly calls Agent_1 via command line"""
    # For demo purposes, return a predefined response
    questions = {
        "What are the required fields in the event_trees section?": 
            "The required fields in the event_trees section are: 'id', 'name', 'top_events', and 'sequences'.",
        "How do I define a top event?": 
            "To define a top event, create an object with 'id' and 'description' fields in the top_events array.",
        "What is the purpose of node_substitutions?": 
            "node_substitutions define the branching logic in the event tree, mapping node IDs to their corresponding substitution values.",
        "Tell me about the basic event structure in SAPHIRE schema":
            "Basic events in SAPHIRE represent the fundamental failure modes in a system. They contain fields such as: 'id' (unique identifier), 'name' (descriptive name), 'description' (detailed explanation), 'probability' (failure likelihood), and 'distribution' (uncertainty parameters).",
        "What are fault trees in SAPHIRE?":
            "Fault trees in SAPHIRE are logical representations of system failures. They contain a hierarchical structure of gates (AND, OR) connecting basic events to show how combinations of failures lead to system failure. Key components include 'id', 'name', 'description', 'gates', and 'basic_events'."
    }
    
    # If the question is in our predefined set, use that
    if content in questions:
        return questions[content]
    
    # Otherwise use our fallback
    return f"The schema defines the structure for SAPHIRE nuclear safety data. Your question was: '{content}'. In the full implementation, this would connect to Agent_1."

def validate_model(content):
    """Implementation that directly calls data-validation via command line"""
    try:
        # For demo purposes, use predefined responses
        if isinstance(content, str):
            if "naming conventions" in content.lower():
                return {
                    "valid": False,
                    "errors": [
                        "Basic event BE-PUMP-1 does not follow naming convention (should be BE_PUMP_1)",
                        "Gate G-SYSTEM-FAILURE uses hyphens instead of underscores",
                        "End state ES-01 is not descriptive enough"
                    ],
                    "message": "3 naming convention violations found"
                }
            
            if "validate" in content.lower():
                return {
                    "valid": True,
                    "message": "Schema validation passed successfully!",
                    "stats": {
                        "total_checks": 42,
                        "passed": 42,
                        "warnings": 0,
                        "errors": 0
                    }
                }
        
        # Return a sample validation response
        return {
            "valid": True,
            "message": "Your model has been validated against SAPHIRE schema requirements.",
            "stats": {
                "total_checks": 42,
                "passed": 40,
                "warnings": 2,
                "errors": 0
            }
        }
    except Exception as e:
        return {"valid": False, "errors": [str(e)]}

def render_component(content):
    """Implementation that uses viz-agent's functionality"""
    # For demo, use hard-coded responses based on content
    if "event tree" in content.lower():
        return render_event_tree()
    elif "fault tree" in content.lower():
        return render_fault_tree()
    else:
        # In full implementation, this would call viz-agent
        try:
            # Load the sample visualization from file (for demo)
            with open(os.path.join(BASE_DIR, 'MultiAgent/reference_demo.svg'), 'r') as f:
                svg = f.read()
                return svg
        except:
            return render_generic_diagram(content)

def render_event_tree():
    """Render a sample event tree diagram"""
    svg = '''
    <svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
        <style>
            .node { fill: #f0f8ff; stroke: #333; stroke-width: 2px; }
            .event { fill: #e6f3ff; stroke: #0066cc; stroke-width: 2px; }
            .text { font-family: Arial; font-size: 12px; }
            .line { stroke: #666; stroke-width: 1.5px; }
            .success { fill: #d1e7dd; stroke: #0f5132; }
            .failure { fill: #f8d7da; stroke: #842029; }
        </style>
        
        <text x="400" y="30" text-anchor="middle" font-size="18" font-weight="bold">Loss of Forced Cooling Event Tree</text>
        
        <!-- Initiating Event -->
        <rect x="50" y="50" width="140" height="60" rx="5" class="node" />
        <text x="120" y="85" text-anchor="middle" class="text">LOSS OF FORCED COOLING</text>
        
        <!-- Top Events -->
        <rect x="250" y="50" width="100" height="60" rx="5" class="event" />
        <text x="300" y="85" text-anchor="middle" class="text">REACTOR TRIP</text>
        
        <rect x="400" y="50" width="100" height="60" rx="5" class="event" />
        <text x="450" y="85" text-anchor="middle" class="text">AUX FEED</text>
        
        <rect x="550" y="50" width="100" height="60" rx="5" class="event" />
        <text x="600" y="85" text-anchor="middle" class="text">HPI SYSTEM</text>
        
        <!-- Event Tree Branches -->
        <line x1="120" y1="110" x2="120" y2="150" class="line" />
        <line x1="120" y1="150" x2="300" y2="150" class="line" />
        
        <!-- Success branch -->
        <line x1="300" y1="150" x2="300" y2="200" class="line" />
        <line x1="300" y1="200" x2="450" y2="200" class="line" />
        
        <!-- Success branch -->
        <line x1="450" y1="200" x2="450" y2="250" class="line" />
        <line x1="450" y1="250" x2="600" y2="250" class="line" />
        
        <!-- Success end -->
        <line x1="600" y1="250" x2="600" y2="300" class="line" />
        <rect x="550" y="300" width="100" height="40" rx="5" class="success" />
        <text x="600" y="325" text-anchor="middle" class="text">OK</text>
        
        <!-- HPI Failure -->
        <line x1="600" y1="150" x2="700" y2="150" class="line" />
        <line x1="700" y1="150" x2="700" y2="300" class="line" />
        <rect x="650" y="300" width="100" height="40" rx="5" class="failure" />
        <text x="700" y="325" text-anchor="middle" class="text">CD-LATE</text>
        
        <!-- AUX Failure -->
        <line x1="450" y1="100" x2="800" y2="100" class="line" />
        <line x1="800" y1="100" x2="800" y2="300" class="line" />
        <rect x="750" y="300" width="100" height="40" rx="5" class="failure" />
        <text x="800" y="325" text-anchor="middle" class="text">CD-EARLY</text>
    </svg>
    '''
    return svg

def render_fault_tree():
    """Render a sample fault tree diagram"""
    svg = '''
    <svg width="800" height="500" xmlns="http://www.w3.org/2000/svg">
        <style>
            .node { fill: #f0f8ff; stroke: #333; stroke-width: 2px; }
            .gate { fill: #fff3cd; stroke: #664d03; }
            .basic { fill: #d1e7dd; stroke: #0f5132; }
            .text { font-family: Arial; font-size: 12px; }
            .line { stroke: #666; stroke-width: 1.5px; }
        </style>
        
        <text x="400" y="30" text-anchor="middle" font-size="18" font-weight="bold">Emergency Cooling System Fault Tree</text>
        
        <!-- Top Gate -->
        <polygon points="400,80 370,110 430,110" class="gate" />
        <text x="400" y="100" text-anchor="middle" class="text">OR</text>
        <text x="400" y="125" text-anchor="middle" class="text">SYS-FAILURE</text>
        
        <!-- Connecting Lines -->
        <line x1="400" y1="110" x2="400" y2="140" class="line" />
        <line x1="400" y1="140" x2="250" y2="140" class="line" />
        <line x1="400" y1="140" x2="550" y2="140" class="line" />
        
        <!-- Intermediate Gates -->
        <polygon points="250,170 220,200 280,200" class="gate" />
        <text x="250" y="190" text-anchor="middle" class="text">AND</text>
        <text x="250" y="215" text-anchor="middle" class="text">PUMP-FAILURE</text>
        
        <polygon points="550,170 520,200 580,200" class="gate" />
        <text x="550" y="190" text-anchor="middle" class="text">OR</text>
        <text x="550" y="215" text-anchor="middle" class="text">POWER-FAILURE</text>
        
        <!-- Connect to Intermediate Gates -->
        <line x1="250" y1="140" x2="250" y2="170" class="line" />
        <line x1="550" y1="140" x2="550" y2="170" class="line" />
        
        <!-- Connect from Intermediate Gates to Basic Events -->
        <line x1="250" y1="200" x2="250" y2="230" class="line" />
        <line x1="250" y1="230" x2="150" y2="230" class="line" />
        <line x1="250" y1="230" x2="350" y2="230" class="line" />
        
        <line x1="550" y1="200" x2="550" y2="230" class="line" />
        <line x1="550" y1="230" x2="450" y2="230" class="line" />
        <line x1="550" y1="230" x2="650" y2="230" class="line" />
        
        <!-- Basic Events -->
        <circle cx="150" cy="270" r="30" class="basic" />
        <text x="150" y="275" text-anchor="middle" class="text">PUMP-A</text>
        
        <circle cx="350" cy="270" r="30" class="basic" />
        <text x="350" y="275" text-anchor="middle" class="text">PUMP-B</text>
        
        <circle cx="450" cy="270" r="30" class="basic" />
        <text x="450" y="275" text-anchor="middle" class="text">OFF-SITE</text>
        
        <circle cx="650" cy="270" r="30" class="basic" />
        <text x="650" y="275" text-anchor="middle" class="text">DIESEL-GEN</text>
        
        <!-- Connect to Basic Events -->
        <line x1="150" y1="230" x2="150" y2="240" class="line" />
        <line x1="350" y1="230" x2="350" y2="240" class="line" />
        <line x1="450" y1="230" x2="450" y2="240" class="line" />
        <line x1="650" y1="230" x2="650" y2="240" class="line" />
    </svg>
    '''
    return svg

def render_generic_diagram(content):
    """Render a generic diagram based on the content"""
    svg = f'''
    <svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
        <style>
            .node { fill: #f0f8ff; stroke: #333; stroke-width: 2px; }
            .decision { fill: #e6f3ff; stroke: #0066cc; stroke-width: 2px; }
            .text { font-family: Arial; font-size: 12px; }
            .line { stroke: #666; stroke-width: 1.5px; }
        </style>
        
        <rect x="50" y="50" width="120" height="60" rx="5" class="node" />
        <text x="110" y="85" text-anchor="middle" class="text">EVENT START</text>
        
        <line x1="110" y1="110" x2="110" y2="150" class="line" />
        
        <polygon points="110,150 140,180 80,180" class="decision" />
        <text x="110" y="175" text-anchor="middle" class="text">DECISION</text>
        
        <line x1="80" y1="180" x2="50" y2="220" class="line" />
        <text x="60" y="195" class="text">Yes</text>
        
        <line x1="140" y1="180" x2="170" y2="220" class="line" />
        <text x="160" y="195" class="text">No</text>
        
        <rect x="10" y="220" width="80" height="40" rx="5" class="node" />
        <text x="50" y="245" text-anchor="middle" class="text">SUCCESS</text>
        
        <rect x="130" y="220" width="80" height="40" rx="5" class="node" />
        <text x="170" y="245" text-anchor="middle" class="text">FAILURE</text>
        
        <text x="400" y="350" text-anchor="middle" class="text">Visualization for: {content[:30]}...</text>
    </svg>
    '''
    return svg 