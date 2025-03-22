from google.generativeai import GenerativeModel
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiAgent:
    def __init__(self):
        self.model = GenerativeModel('gemini-pro')
        self.api_key = os.getenv('GOOGLE_API_KEY')
        
    async def process_chat(self, message: str) -> str:
        """
        Process a chat message using Gemini API
        """
        try:
            response = self.model.generate_content(message)
            return response.text
        except Exception as e:
            return f"Error processing chat: {str(e)}" 