import json
import os
from typing import Dict, Any
import google.generativeai as genai
from pathlib import Path

class VisualizationAgent:
    def __init__(self):
        # Initialize Gemini model
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Load SAPHIRE data
        self.saphire_data = self._load_saphire_data()
    
    def _load_saphire_data(self) -> Dict[str, Any]:
        """Load SAPHIRE schema and data files"""
        base_path = Path(__file__).parent.parent
        with open(base_path / "Resources/SAPHIRE/saphire_schema20march.json", "r") as f:
            schema = json.load(f)
        with open(base_path / "Resources/SAPHIRE/event_trees.json", "r") as f:
            event_trees = json.load(f)
        with open(base_path / "Resources/SAPHIRE/basic_events.json", "r") as f:
            basic_events = json.load(f)
        return {
            "schema": schema,
            "event_trees": event_trees,
            "basic_events": basic_events
        }
    
    def render_event_tree(self, query: str) -> str:
        """Render SVG diagram of event tree based on query"""
        prompt = f"""
        Based on the following SAPHIRE data, create an SVG diagram for the event tree query: {query}
        
        Data:
        {json.dumps(self.saphire_data, indent=2)}
        
        Generate an SVG diagram that:
        1. Shows proper branching structure
        2. Uses clear visual hierarchy
        3. Includes labels and descriptions
        4. Follows the schema structure
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def highlight_risk_paths(self, query: str) -> str:
        """Generate SVG with color-coded risk paths"""
        prompt = f"""
        Based on the following SAPHIRE data, create an SVG diagram highlighting high-risk paths for: {query}
        
        Data:
        {json.dumps(self.saphire_data, indent=2)}
        
        Generate an SVG diagram that:
        1. Shows the fault tree structure
        2. Color-codes paths based on risk significance (red for high risk, yellow for medium, green for low)
        3. Includes risk scores and descriptions
        4. Uses clear visual hierarchy
        """
        
        response = self.model.generate_content(prompt)
        return response.text

# Create singleton instance
viz_agent = VisualizationAgent() 