# Nuclear PRA Multi-Agent System Hub

This project serves as a central message hub for a multi-agent system focused on nuclear Probabilistic Risk Assessment (PRA). The hub orchestrates communication between different specialized agents and provides visualization of their interactions.

## Architecture

The system consists of:

1. **Central Message Hub (this project)**: 
   - Orchestrates communication between agents
   - Visualizes agent interactions
   - Provides a message logging system
   - Handles message routing

2. **Agent 1 - Schema Assistant**:
   - Handles JSON schema analysis and generation
   - Running on a separate Node.js server

3. **Agent 2 - Data Validator**:
   - Validates data against schemas
   - Checks naming conventions and consistency
   - Running on a separate Flask server

4. **Agent 3 - Visualization Agent**:
   - Generates visualizations of PRA models
   - Integrated with the central hub

## Setup and Usage

### Running the Hub

1. Make sure you have Python 3.8+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Connecting Agents

1. Copy the relevant adapter from the `agent_adapters` directory to each agent's project:
   - For Agent 1 (Schema Assistant): Copy `schema_assistant_adapter.js` to your Node.js project
   - For Agent 2 (Data Validator): Copy `data_validation_adapter.py` to your Flask project

2. Import and use the adapter in each agent as shown in the adapter example code.

3. Make sure all agents expose the required API endpoints to receive messages from the hub.

## Message Format

All messages between agents use this standardized format:

```json
{
  "type": "message.type",
  "content": "Message content or object",
  "source": "agent_id",
  "target": "recipient_agent_id",
  "timestamp": "ISO timestamp"
}
```

Common message types:
- `schema.question` - Questions about schema structure
- `schema.response` - Responses to schema questions
- `validation.request` - Requests for data validation
- `validation.response` - Validation results
- `visualization.request` - Requests for visualization
- `visualization.response` - Visualization results

## Deployment

To deploy to Fly.io:

```bash
# If you haven't already created the app
flyctl launch --generate-name

# If the app already exists, just deploy
flyctl deploy
```

## Demo

The central message hub provides:

1. A visual representation of agents and message flow
2. Real-time monitoring of agent status
3. A message log showing all inter-agent communication
4. Links to open individual agent UIs in separate tabs
5. A test panel to send messages to agents

## Development

- The hub is built with FastAPI, providing both WebSocket and REST API interfaces
- The frontend visualization uses plain JavaScript with a simple animated UI
- Adapters are provided for Python (Flask) and Node.js agents

Let's deploy to Fly.io. Since the app is working locally, we'll follow these steps:

1. **First, let's verify we're in the correct directory**:
```bash
cd nucleargen/MultiAgent
```

2. **Update the WebSocket connection in agent-ui.js** to use secure WebSocket (wss://) for production:

```javascript:nucleargen/MultiAgent/static/js/agent-ui.js
// WebSocket connection
let ws = null;

// Connect to WebSocket
function connectWebSocket() {
    // Use wss:// in production and ws:// in development
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
    
    ws.onmessage = function(event) {
        const message = JSON.parse(event.data);
        handleMessage(message);
    };
    
    ws.onclose = function() {
        console.log('WebSocket connection closed');
        setTimeout(connectWebSocket, 1000); // Reconnect after 1 second
    };

    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
}

// Rest of the code remains the same
// ... existing code ...
```
3. **Deploy to Fly.io**:

```bash
# If you haven't already created the app
flyctl launch --generate-name

# If the app already exists, just deploy
flyctl deploy
```

4. **After deployment, check the status**:
```bash
flyctl status
```

5. **Monitor the logs for any issues**:
```bash
flyctl logs
```

6. **Open the app in your browser**:
```bash
flyctl open
```

The app should now be accessible at your Fly.io URL (e.g., https://thrumming-haze-5713.fly.dev/).

Important things to verify after deployment:
1. The UI loads correctly
2. WebSocket connection is established (check browser console)
3. Demo buttons work
4. Messages are being sent and received

Would you like me to help you with any of these steps or verify anything specific?
