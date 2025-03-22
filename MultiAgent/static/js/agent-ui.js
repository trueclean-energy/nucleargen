// WebSocket connection
let ws = null;

// Connect to WebSocket
function connectWebSocket() {
    // Use wss:// in production and ws:// in development
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
    
    ws.onmessage = function(event) {
        try {
            const message = JSON.parse(event.data);
            handleMessage(message);
            console.log("Received message:", message);
        } catch (e) {
            console.error("Error parsing message:", e);
        }
    };
    
    ws.onopen = function() {
        console.log('WebSocket connection opened');
        document.getElementById('message-log').innerHTML += 
            `<div class="log-entry"><span class="log-time">${new Date().toLocaleTimeString()}</span>Connected to server</div>`;
    };
    
    ws.onclose = function() {
        console.log('WebSocket connection closed');
        document.getElementById('message-log').innerHTML += 
            `<div class="log-entry"><span class="log-time">${new Date().toLocaleTimeString()}</span>Connection closed</div>`;
        setTimeout(connectWebSocket, 1000); // Reconnect after 1 second
    };

    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        document.getElementById('message-log').innerHTML += 
            `<div class="log-entry"><span class="log-time">${new Date().toLocaleTimeString()}</span>Connection error</div>`;
    };
}

// Handle incoming messages
function handleMessage(message) {
    if (!message) return;
    
    const { type, content } = message;
    console.log("Processing message type:", type);
    
    switch(type) {
        case 'schema.response':
            document.getElementById('tushin-output').innerHTML += 
                `<div class="agent-response">${content}</div>`;
            break;
            
        case 'validation.response':
            let validationContent = content;
            try {
                if (typeof content === 'string') {
                    try {
                        const parsed = JSON.parse(content);
                        validationContent = formatValidationResult(parsed);
                    } catch (e) {
                        // Keep as string if not valid JSON
                    }
                } else if (typeof content === 'object') {
                    validationContent = formatValidationResult(content);
                }
            } catch (e) {
                console.error("Error formatting validation result:", e);
            }
            
            document.getElementById('noah-output').innerHTML += 
                `<div class="agent-response">${validationContent}</div>`;
            break;
            
        case 'visualization.response':
            document.getElementById('bobber-output').innerHTML += 
                `<div class="agent-response">${content}</div>`;
            break;
            
        default:
            console.log("Unknown message type:", type);
    }
    
    // Update message log
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.innerHTML = `<span class="log-time">${new Date().toLocaleTimeString()}</span>${type}`;
    document.getElementById('message-log').appendChild(logEntry);
}

// Format validation results as HTML
function formatValidationResult(content) {
    if (!content) return "No validation data received";
    
    return `<div class="validation-report">
        <h4>Validation Results</h4>
        <div class="stats">
            <p><strong>Valid:</strong> ${content.valid}</p>
            ${content.errors ? `<p><strong>Errors:</strong> ${content.errors.map(err => `<br>- ${err}`).join('')}</p>` : ''}
            ${content.message ? `<p><strong>Message:</strong> ${content.message}</p>` : ''}
            ${content.stats ? `
                <p><strong>Statistics:</strong></p>
                <ul>
                    ${Object.entries(content.stats).map(([key, value]) => `<li>${key}: ${value}</li>`).join('')}
                </ul>
            ` : ''}
        </div>
    </div>`;
}

// Send message to server
function sendMessage(type, content) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        const message = {
            type,
            content,
            timestamp: new Date().toISOString()
        };
        
        console.log("Sending message:", message);
        ws.send(JSON.stringify(message));
        
        // Show the sent message in the UI as feedback
        switch(type) {
            case 'schema.question':
                document.getElementById('tushin-output').innerHTML += 
                    `<div class="user-message"><strong>You asked:</strong> ${content}</div>`;
                break;
            case 'validation.request':
                document.getElementById('noah-output').innerHTML += 
                    `<div class="user-message"><strong>Validation request:</strong> ${content}</div>`;
                break;
            case 'visualization.request':
                document.getElementById('bobber-output').innerHTML += 
                    `<div class="user-message"><strong>Visualization request:</strong> ${content}</div>`;
                break;
        }
    } else {
        console.error("WebSocket not connected");
        alert("WebSocket connection is closed. Please reload the page.");
    }
}

// Handle form submission
document.getElementById('question-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const input = document.getElementById('question-input');
    const question = input.value.trim();
    
    if (question) {
        // Determine message type based on question content
        determineMessageTypeAndSend(question);
        input.value = '';
    }
});

// Determine the appropriate message type based on content
function determineMessageTypeAndSend(question) {
    // Keywords for validation requests
    const validationKeywords = ['validate', 'validation', 'check', 'verify'];
    
    // Keywords for visualization requests
    const visualizationKeywords = ['show', 'display', 'visualize', 'diagram', 'tree', 'graph'];
    
    // Check for validation request
    if (validationKeywords.some(keyword => question.toLowerCase().includes(keyword))) {
        sendMessage('validation.request', question);
        return;
    }
    
    // Check for visualization request
    if (visualizationKeywords.some(keyword => question.toLowerCase().includes(keyword))) {
        sendMessage('visualization.request', question);
        return;
    }
    
    // Default to schema question
    sendMessage('schema.question', question);
}

// Handle demo button clicks
function askQuestion(question) {
    // Route to appropriate agent based on content
    determineMessageTypeAndSend(question);
}

// Add CSS for user messages
const style = document.createElement('style');
style.textContent = `
.user-message {
    background: #f8f9fa;
    padding: 8px;
    margin-bottom: 10px;
    border-left: 3px solid #6c757d;
}
`;
document.head.appendChild(style);

// Initialize WebSocket connection
connectWebSocket(); 