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

// Handle incoming messages
function handleMessage(message) {
    const { type, content } = message;
    
    switch(type) {
        case 'schema.response':
            document.getElementById('tushin-output').innerHTML += 
                `<div class="agent-response">${content}</div>`;
            break;
            
        case 'validation.response':
            document.getElementById('noah-output').innerHTML += 
                `<div class="agent-response">${content}</div>`;
            break;
            
        case 'visualization.response':
            document.getElementById('bobber-output').innerHTML += 
                `<div class="agent-response">${content}</div>`;
            break;
    }
    
    // Update message log
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.innerHTML = `<span class="log-time">${new Date().toLocaleTimeString()}</span>${type}`;
    document.getElementById('message-log').appendChild(logEntry);
}

// Send message to server
function sendMessage(type, content) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type,
            content,
            timestamp: new Date().toISOString()
        }));
    }
}

// Handle form submission
document.getElementById('question-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const input = document.getElementById('question-input');
    const question = input.value.trim();
    
    if (question) {
        sendMessage('schema.question', question);
        input.value = '';
    }
});

// Handle demo button clicks
function askQuestion(question) {
    sendMessage('schema.question', question);
}

// Initialize WebSocket connection
connectWebSocket(); 