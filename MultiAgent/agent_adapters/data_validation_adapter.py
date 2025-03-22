"""
Data Validation Agent Adapter

This adapter connects the Flask-based data validation agent with the central message hub.
Copy this file to your data-validation directory and import it in your app.py file.
"""

import requests
import json
from datetime import datetime
import os

class MessageHubClient:
    def __init__(self, hub_url="http://localhost:8000"):
        """Initialize the message hub client"""
        self.hub_url = hub_url
        self.agent_id = "agent2"
    
    def send_message(self, message_type, content, target="hub"):
        """Send a message to the central hub"""
        message = {
            "type": message_type,
            "content": content,
            "source": self.agent_id,
            "target": target,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.hub_url}/api/message",
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending message to hub: {e}")
            return False
    
    def send_validation_result(self, validation_result):
        """Send a validation result to the hub"""
        return self.send_message("validation.response", validation_result)
    
    def register_with_hub(self):
        """Register this agent with the hub (optional)"""
        message = {
            "type": "agent.register",
            "content": {
                "agent_id": self.agent_id,
                "agent_type": "validation",
                "capabilities": ["schema_validation", "naming_convention_check", "data_consistency"]
            },
            "source": self.agent_id,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.hub_url}/api/message",
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error registering with hub: {e}")
            return False

# Example usage in Flask app:
"""
from agent_adapters.data_validation_adapter import MessageHubClient

# Initialize the client
hub_client = MessageHubClient()

@app.route('/api/validate', methods=['POST'])
def validate_data():
    data = request.get_json()
    
    # Process the validation request
    result = your_validation_function(data['content'])
    
    # Send the result back to the hub
    hub_client.send_validation_result(result)
    
    return jsonify({"status": "success"})
""" 