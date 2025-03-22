# Add this to your project as llm_service.py

import requests
import json
import os
import re
from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env file in current directory and parent directories
    env_path = Path(__file__).resolve().parent / '.env'
    load_dotenv(dotenv_path=env_path)
    logger.info("Loaded environment variables from .env file")
except ImportError:
    logger.warning("python-dotenv not installed. Using environment variables directly.")
except Exception as e:
    logger.warning(f"Failed to load .env file: {e}")

class TogetherAIService:
    """Service for processing visualization prompts with Together AI's LLM API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the TogetherAI service
        
        Args:
            api_key: Together AI API key (defaults to TOGETHER_API_KEY env variable)
        """
        self.api_key = api_key or os.environ.get("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("Together AI API key is required. Set TOGETHER_API_KEY environment variable or pass directly.")
        
        self.api_url = "https://api.together.xyz/v1/chat/completions"
        self.model = "mistralai/Mixtral-8x7B-Instruct-v0.1" # You can change to a different model
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
    
    def generate_visualization(self, prompt: str, data_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate visualization code from a user prompt
        
        Args:
            prompt: User prompt describing the desired visualization
            data_context: Optional dictionary with data context
        
        Returns:
            Dict with visualization details including type and code
        """
        # Format context from data if available
        context = ""
        if data_context:
            context = "Available data structure:\n"
            for key, value in data_context.items():
                if isinstance(value, list):
                    if len(value) > 0:
                        sample = value[0]
                        if isinstance(sample, dict) and "id" in sample:
                            ids = [item.get("id") for item in value[:5] if isinstance(item, dict) and "id" in item]
                            context += f"- {key}: list with {len(value)} items. Example IDs: {', '.join(ids)}"
                            if len(value) > 5:
                                context += f" and {len(value)-5} more"
                            context += "\n"
                        else:
                            context += f"- {key}: list with {len(value)} items\n"
                    else:
                        context += f"- {key}: empty list\n"
                elif isinstance(value, dict):
                    context += f"- {key}: dictionary with keys {list(value.keys())}\n"
                else:
                    context += f"- {key}: {str(value)[:50]}\n"
        
        # Prepare system prompt
        visualization_system_prompt = f"""You are a specialized AI that converts user requests into visualization code.
When the user describes a visualization they want, analyze their request and generate appropriate code.

Types of visualizations you can generate:
1. Mermaid diagrams (flowchart, sequence diagram, class diagram, ER diagram)
2. Fault trees or event trees (for SAPHIRE data)

{context}

Your response must be in this JSON format:
{{
    "visualization_type": "mermaid" or "saphire",
    "diagram_type": "flowchart", "sequence", "class", "er", "fault_tree", or "event_tree",
    "code": "The visualization code",
    "explanation": "Brief explanation of the visualization" 
}}

Always output valid JSON only. No need for explanation or other text outside the JSON object.
"""

        # Create message payload for the LLM
        messages = [
            {"role": "system", "content": visualization_system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Make API request to Together AI
            self.logger.info("Making API request to Together AI")
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1500,
                    "stop": ["]}", "```"]
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the generated text
            generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parse the JSON response
            # First, find the JSON object using regex
            json_match = re.search(r'({[\s\S]*})', generated_text)
            if json_match:
                json_str = json_match.group(1)
                # Clean up any markdown code block syntax
                json_str = re.sub(r'```json|```', '', json_str).strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    print(f"Error parsing JSON: {json_str}")
            
            # Fallback response if parsing fails
            return {
                "visualization_type": "mermaid",
                "diagram_type": "flowchart",
                "code": "graph TD\n    A[Request] --> B[Parse]\n    B --> C[Visualize]\n    C --> D[Display]",
                "explanation": "Fallback visualization due to parsing error."
            }
            
        except Exception as e:
            print(f"Error calling Together AI API: {e}")
            # Return fallback visualization
            return {
                "visualization_type": "mermaid",
                "diagram_type": "flowchart",
                "code": "graph TD\n    A[Start] --> B[Error]\n    B --> C[Fallback]\n    C --> D[End]",
                "explanation": f"Error occurred: {str(e)}"
            }
    
    def _format_together_prompt(self, messages):
        """
        Format messages for Together AI API
        
        Args:
            messages: List of message dictionaries with role and content
        
        Returns:
            Formatted prompt string
        """
        prompt = ""
        for message in messages:
            if message["role"] == "system":
                prompt += f"<s>[INST] {message['content']} [/INST]\n\n"
            elif message["role"] == "user":
                prompt += f"[INST] {message['content']} [/INST]\n\n"
            elif message["role"] == "assistant":
                prompt += f"{message['content']}\n\n"
        return prompt

    def summarize_data(self, prompt: str, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        First stage: Analyze data summary and create visualization plan.
        
        Args:
            prompt: User's visualization request
            data_summary: Summarized SAPHIRE data
            
        Returns:
            Dictionary with visualization plan
        """
        # Convert data summary to a readable format
        context = json.dumps(data_summary, indent=2)
        
        # Create the system prompt for data summarization
        summarization_prompt = f"""You are a data visualization expert specializing in SAPHIRE probabilistic risk assessment models.
You will be given a summary of a SAPHIRE model and a user's visualization request.

Your task is to:
1. Understand the structure and content of the data
2. Create a plan for visualizing the data according to the user's request
3. Identify which specific data elements will be needed for the visualization

The data summary includes counts, sample elements, and basic structure information.

Your response must be in this JSON format:
{{
    "data_understanding": "Brief description of the data structure and content",
    "visualization_plan": "Description of the planned visualization approach",
    "needed_data_elements": ["list", "of", "specific", "data", "fields", "needed"],
    "visualization_type": "HTML, SVG, chart, etc."
}}

Always output valid JSON only. No need for explanation outside the JSON object.

SAPHIRE data summary:
{context}
"""

        # Create message payload for the LLM
        messages = [
            {"role": "system", "content": summarization_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            # Make API request to LLM provider
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "stop": ["]}", "```"]
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract and parse the response
            generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parse the JSON response
            json_match = re.search(r'({[\s\S]*})', generated_text)
            if json_match:
                json_str = json_match.group(1)
                json_str = re.sub(r'```json|```', '', json_str).strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    print(f"Error parsing JSON: {json_str}")
            
            # Fallback response if parsing fails
            return {
                "data_understanding": "Failed to parse data structure",
                "visualization_plan": "Generate a basic overview visualization",
                "needed_data_elements": ["basic_counts"],
                "visualization_type": "HTML"
            }
            
        except Exception as e:
            print(f"Error calling API: {e}")
            # Return fallback plan
            return {
                "data_understanding": f"Error occurred: {str(e)}",
                "visualization_plan": "Generate a basic overview visualization",
                "needed_data_elements": ["basic_counts"],
                "visualization_type": "HTML"
            }

    def generate_complete_visualization(self, prompt: str, focused_data: Dict[str, Any], plan: Dict[str, Any]) -> str:
        """
        Second stage: Generate complete HTML visualization based on focused data and plan.
        
        Args:
            prompt: User's visualization request
            focused_data: Extracted data elements needed for visualization
            plan: Visualization plan from the first stage
            
        Returns:
            Complete HTML string for visualization
        """
        # Log the visualization process
        self.logger.info("Generating complete visualization")
        self.logger.info(f"Visualization plan: {json.dumps(plan.get('visualization_plan', ''), indent=2)}")
        
        if os.getenv("VERBOSE_LLM") == "1":
            self.logger.info(f"Using focused data: {json.dumps(focused_data, indent=2)}")
        
        # Convert focused data to a string
        data_str = json.dumps(focused_data)
        
        # Create the system prompt for visualization generation with enhanced instructions
        visualization_prompt = f"""You are a visualization expert specializing in SAPHIRE probabilistic risk assessment models.
Generate a COMPLETE, SELF-CONTAINED HTML visualization based on the user's request and the provided data.

YOUR VISUALIZATION MUST START WITH THIS EXACT TEMPLATE:
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAPHIRE Visualization</title>
    <style>
        /* Base styles */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        /* Add your additional styles below this line */
    </style>
    <!-- Add your scripts here -->
</head>
<body>
    <div class="container">
        <!-- Add your visualization content here -->
    </div>
</body>
</html>

VISUALIZATION REQUIREMENTS:
1. Use the template above EXACTLY as shown - do not modify the base styles
2. Add your additional styles and scripts INSIDE the designated areas
3. Place all visualization content inside the container div
4. Include proper error handling with user-friendly messages
5. Make the visualization responsive and interactive
6. Use semantic HTML and proper ARIA attributes for accessibility

FAULT TREE VISUALIZATION REQUIREMENTS:
- Place the top gate at the top with components flowing downward
- Use standard shapes: OR gates as circles with curved bottoms, AND gates as rectangles with flat bottoms
- Connect all gates to their inputs with visible lines/paths
- Include clear labels for all components
- Color-code elements by type (gates, basic events, etc.)
- Include a clear legend explaining symbols and colors
- Use SVG for drawing shapes and connections
- Add tooltips for additional information
- Make the visualization zoomable and pannable
- Include a search/filter function for large trees

EVENT TREE VISUALIZATION REQUIREMENTS:
- Start with initiating event on the left
- Branch points should clearly show success/failure paths
- End states should be clearly labeled on the right
- Include probabilities where available
- Use clear directional indicators for paths
- Add tooltips for branch point details
- Make the visualization scrollable for large trees
- Include a legend for path types and symbols

IMPORTANT:
- DO NOT use external CDN links or resources
- Include all necessary JavaScript libraries directly in the code
- Handle all errors gracefully with user-friendly messages
- Ensure all font references use the system font stack from the template
- Test all JavaScript code for errors before including it
- Add clear error messages if data is missing or malformed
- Include a loading state for dynamic content
- Add proper ARIA labels for accessibility
- Use semantic HTML elements
- Include a fallback message if JavaScript is disabled

Visualization plan: {plan.get('visualization_plan')}

The data provided contains exactly the elements you need for this visualization.

Your response must be ONLY valid HTML code that can be directly inserted into an iframe.
Do not include markdown code fences, explanation text, or anything other than the HTML itself.

SAPHIRE data:
{data_str}
"""

        # Create message payload for the LLM
        messages = [
            {"role": "system", "content": visualization_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            self.logger.info("Making API request to LLM provider")
            # Make API request to LLM provider
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 4000,
                    "stop": ["</html>"]
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the generated HTML
            generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Clean up the response to ensure it's valid HTML
            html = generated_text.strip()
            
            # Log the size of the generated HTML
            self.logger.info(f"Generated HTML size: {len(html)} bytes")
            
            # Ensure the HTML starts with the proper doctype
            if not html.startswith("<!DOCTYPE html>"):
                self.logger.warning("Generated HTML missing doctype, adding wrapper")
                html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAPHIRE Visualization</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .error {{
            color: #721c24;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 20px;
            border-radius: 4px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html}
    </div>
</body>
</html>"""
            
            # If the HTML is incomplete, add closing tags
            if "</html>" not in html:
                self.logger.warning("Generated HTML missing closing tags, adding them")
                html += "</html>"
            
            return html
            
        except Exception as e:
            self.logger.error(f"Error generating visualization: {str(e)}")
            # Return error HTML with proper styling
            return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualization Error</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .error {{
            color: #721c24;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 20px;
            border-radius: 4px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Visualization Error</h1>
        <div class="error">
            <p><strong>Error generating visualization:</strong> {str(e)}</p>
            <p>Please try again with a different prompt or check the input data.</p>
        </div>
    </div>
</body>
</html>"""


class BraveAPIService:
    """Service for processing visualization prompts with Brave's AI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Brave API service
        
        Args:
            api_key: Brave API key (defaults to BRAVE_API_KEY env variable)
        """
        self.api_key = api_key or os.environ.get("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError("Brave API key is required. Set BRAVE_API_KEY environment variable or pass directly.")
        
        self.api_url = "https://api.search.brave.com/llm/v1/generate"
    
    def generate_visualization(self, prompt: str, data_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate visualization code from a user prompt using Brave API
        
        Args:
            prompt: User prompt describing the desired visualization
            data_context: Optional dictionary with data context
        
        Returns:
            Dict with visualization details including type and code
        """
        # Format context similar to the Together AI implementation
        context = ""
        if data_context:
            # Same context formatting as in TogetherAIService
            pass
        
        # Prepare system prompt (similar to Together AI version)
        visualization_system_prompt = f"""You are a specialized AI that converts user requests into visualization code.
When the user describes a visualization they want, analyze their request and generate appropriate code.

Types of visualizations you can generate:
1. Mermaid diagrams (flowchart, sequence diagram, class diagram, ER diagram)
2. Fault trees or event trees (for SAPHIRE data)

{context}

Your response must be in this JSON format:
{{
    "visualization_type": "mermaid" or "saphire",
    "diagram_type": "flowchart", "sequence", "class", "er", "fault_tree", or "event_tree",
    "code": "The visualization code",
    "explanation": "Brief explanation of the visualization" 
}}

Output valid JSON only. No explanation or other text outside the JSON object.
"""

        try:
            # Make API request to Brave
            response = requests.post(
                self.api_url,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "X-Brave-Key": self.api_key
                },
                json={
                    "model": "llama3:latest",  # Use the latest Llama model
                    "messages": [
                        {"role": "system", "content": visualization_system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "max_tokens": 1500
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the generated text
            generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parse the JSON response (similar to Together AI implementation)
            json_match = re.search(r'({[\s\S]*})', generated_text)
            if json_match:
                json_str = json_match.group(1)
                json_str = re.sub(r'```json|```', '', json_str).strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    print(f"Error parsing JSON: {json_str}")
            
            # Fallback response
            return {
                "visualization_type": "mermaid",
                "diagram_type": "flowchart",
                "code": "graph TD\n    A[Request] --> B[Process]\n    B --> C[Visualize]",
                "explanation": "Fallback visualization due to parsing error."
            }
            
        except Exception as e:
            print(f"Error calling Brave API: {e}")
            # Return fallback visualization
            return {
                "visualization_type": "mermaid",
                "diagram_type": "flowchart",
                "code": "graph TD\n    A[Start] --> B[Error]\n    B --> C[End]",
                "explanation": f"Error occurred: {str(e)}"
            }


def create_llm_service(service_name: str = "together"):
    """
    Factory function to create an LLM service based on the service name
    
    Args:
        service_name: Name of the LLM service to use ('together' or 'brave')
        
    Returns:
        An instance of the LLM service
        
    Raises:
        ValueError: If the service name is not supported
    """
    if service_name.lower() == "together":
        return TogetherAIService()
    elif service_name.lower() == "brave":
        return BraveAPIService()
    else:
        raise ValueError(f"Unsupported LLM service: {service_name}. Use 'together' or 'brave'.")