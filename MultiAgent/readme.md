# Nuclear Generation Multi-Agent Demo

This is a minimalistic integration of three specialized agents:

1. **Schema Conversation Agent** (from Agent_1) - Answers questions about the SAPHIRE schema
2. **Data Validation Agent** (from data-validation) - Validates JSON data against schema requirements
3. **Visualization Agent** (from viz-agent) - Renders visual components from SAPHIRE data

## Quick Start

Run the demo with:

```bash
# Make sure you're in the MultiAgent directory
cd MultiAgent

# Run the demo
./run.sh
```

The demo will be accessible at http://localhost:8000

## Architecture

The system uses a simple message bus architecture:

1. Frontend sends messages through WebSocket
2. Message Bus routes messages to appropriate agent based on message type
3. Agents process requests and return responses
4. Message Bus broadcasts responses back to all connected clients

## Message Types

- `schema.question` - Questions about the schema (handled by Agent_1)
- `validation.request` - Requests to validate JSON data (handled by data-validation)
- `visualization.request` - Requests to generate visualizations (handled by viz-agent)

## Demo Walkthrough

1. Open the UI at http://localhost:8000
2. Enter a question about the schema in the input field (e.g., "What are the required fields in the event_trees section?")
3. Upload a JSON file for validation
4. Request a visualization of a component

## Integration Notes

This demo integrates the agents with minimal coupling:
- Original agent code remains in their respective directories
- The MultiAgent uses adapter functions to communicate with each agent
- Each agent maintains its independence and can be updated separately

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
