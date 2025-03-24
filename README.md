# NuclearGen

This repository contains four main components that can be run independently:

## Quick Start Guide

### Agent_1 (Node.js Application)
```bash
cd /Users/rahulagarwal/Documents/TrueClean_Code/Hackathon/nucleargen/Agent_1
# Create a .env file with your Together API key:
# TOGETHER_API_KEY=your_api_key_here
npm install
node server.js
```

### Viz-Agent (Python Visualization)
```bash
cd /Users/rahulagarwal/Documents/TrueClean_Code/Hackathon/nucleargen/viz-agent
pip install -r requirements.txt
# Create a .env file with your Gemini API key:
# GEMINI_API_KEY=your_api_key_here
python agent.py
```

### MultiAgent System
```bash
cd /Users/rahulagarwal/Documents/TrueClean_Code/Hackathon/nucleargen/MultiAgent
./run.sh
# Or alternatively
python main.py
```

The MultiAgent system provides:
- A WebSocket-based message bus (FastAPI) that orchestrates communication between components
- Real-time message routing for schema questions, model validation, and visualization requests
- Mock agent implementations for demonstration purposes, with predefined responses for common SAPHIRE schema queries

### Data Validation Tool
```bash
cd /Users/rahulagarwal/Documents/TrueClean_Code/Hackathon/nucleargen/data-validation
pip install -r requirements.txt
python app.py
```

The Data Validation Tool will be available at http://127.0.0.1:5001

## Dependencies

### Agent_1 Requirements
- Node.js
- Together API key (create a .env file with TOGETHER_API_KEY=your_api_key_here)

### Viz-Agent Requirements
- Python 3.x
- google-generativeai 0.3.2
- python-dotenv 1.0.1
- requests 2.31.0

### MultiAgent Requirements
- Python 3.x
- FastAPI
- WebSocket support
- asyncio

### Data Validation Tool Requirements
- Python 3.x
- Flask 3.0.2
- python-dotenv 1.0.1
- requests 2.31.0
- google-generativeai 0.3.2

## Development Notes
- The Data Validation Tool runs in debug mode by default
- For production deployment, use a production WSGI server
- The application is accessible on all network interfaces (0.0.0.0)
- The Viz-Agent requires a Google Gemini API key. Create a `.env` file in the viz-agent directory with your API key:
  ```
  GEMINI_API_KEY=your_api_key_here
  ```
- Agent_1 requires a Together API key. Create a `.env` file in the Agent_1 directory with your API key:
  ```
  TOGETHER_API_KEY=your_api_key_here
  ```