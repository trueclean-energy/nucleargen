import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
# You need to create a .env file with GOOGLE_API_KEY=your_api_key
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    print("Please create a .env file with GOOGLE_API_KEY=your_api_key")
    exit(1)

# Initialize the Gemini API
genai.configure(api_key=api_key)

def generate_content(prompt):
    """Generate content using Gemini model."""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating content: {str(e)}"

# Example usage
if __name__ == "__main__":
    user_prompt = "Explain how AI works"
    result = generate_content(user_prompt)
    print("\nGemini Response:")
    print("-" * 40)
    print(result)
    print("-" * 40)

    # Interactive mode
    print("\nInteractive Mode (type 'exit' to quit):")
    while True:
        user_input = input("\nEnter your prompt: ")
        if user_input.lower() in ['exit', 'quit', 'q']:
            break
        
        result = generate_content(user_input)
        print("\nGemini Response:")
        print("-" * 40)
        print(result)
        print("-" * 40) 