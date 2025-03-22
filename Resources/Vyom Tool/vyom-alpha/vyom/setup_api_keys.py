#!/usr/bin/env python
"""
Utility script to help users set up API keys for the visualization tool.
"""
import os
import sys
from pathlib import Path

def setup_api_keys():
    """Set up API keys for the visualization tool."""
    print("Setting up API keys for the visualization tool")
    print("=" * 50)
    print("\nThis script will help you set up API keys for the LLM services.")
    print("The keys will be stored in a .env file in the current directory.")
    print("The .env file is gitignored to prevent accidental commits of API keys.")
    
    # Check if .env file already exists
    env_path = Path(__file__).resolve().parent / '.env'
    if env_path.exists():
        print("\nA .env file already exists. Do you want to overwrite it?")
        response = input("Enter 'yes' to overwrite, or any other key to abort: ")
        if response.lower() != 'yes':
            print("Aborted. Your existing .env file was not modified.")
            return
    
    # Get API keys from user
    print("\nPlease enter your API keys:")
    together_key = input("Together AI API key (leave empty to skip): ").strip()
    brave_key = input("Brave API key (leave empty to skip): ").strip()
    
    if not together_key and not brave_key:
        print("\nError: You must provide at least one API key.")
        print("You can get a Together AI API key from https://together.ai")
        print("You can get a Brave API key from https://brave.com/search/api/")
        return
    
    # Set default values
    use_llm = 'true'
    llm_service = 'together' if together_key else 'brave'
    
    # Create .env file
    with open(env_path, 'w') as f:
        f.write("# LLM API Keys\n")
        if together_key:
            f.write(f"TOGETHER_API_KEY={together_key}\n")
        if brave_key:
            f.write(f"BRAVE_API_KEY={brave_key}\n")
        f.write("\n# LLM Configuration\n")
        f.write(f"USE_LLM={use_llm}\n")
        f.write(f"LLM_SERVICE={llm_service}\n")
    
    print(f"\nAPI keys successfully saved to {env_path}")
    print("You're now ready to use the visualization tool!")
    print("\nTo test your setup, try running:")
    print("  python cli.py generate \"Create a simple flowchart\"")
    
    # Optional: Test the API key
    print("\nWould you like to test your API key now?")
    test_response = input("Enter 'yes' to test, or any other key to skip: ")
    if test_response.lower() == 'yes':
        try:
            # Set environment variables
            os.environ["USE_LLM"] = use_llm
            os.environ["LLM_SERVICE"] = llm_service
            if together_key:
                os.environ["TOGETHER_API_KEY"] = together_key
            if brave_key:
                os.environ["BRAVE_API_KEY"] = brave_key
                
            # Test API key
            print("\nTesting API key...")
            from llm_service import create_llm_service
            service = create_llm_service(llm_service)
            result = service.generate_visualization("Create a simple test diagram")
            print("API key is working correctly!")
            print(f"Generated a {result['visualization_type']} {result['diagram_type']} diagram")
            
        except Exception as e:
            print(f"\nError testing API key: {e}")
            print("Please check your API key and try again.")

if __name__ == "__main__":
    setup_api_keys() 