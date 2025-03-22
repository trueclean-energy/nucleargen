// Update public/js/app.js

document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const uploadDataBtn = document.getElementById('upload-data-btn');
    const dataFileInput = document.getElementById('data-file');
    const schemaStatus = document.getElementById('schema-status');
    const dataStatus = document.getElementById('data-status');

    // Add clear button
    const clearBtn = document.createElement('button');
    clearBtn.textContent = 'Clear Chat';
    clearBtn.className = 'clear-btn';
    document.querySelector('.chat-input').appendChild(clearBtn);

    let isProcessing = false;

    // Function to create typing indicator
    function createTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator message assistant-message';
        indicator.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        return indicator;
    }

    // Initialize the schema on page load
    async function initializeSchema() {
        try {
            const response = await fetch('/api/schema', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ schema: {} })
            });

            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error);
            }
        } catch (error) {
            schemaStatus.textContent = 'Error loading schema';
            schemaStatus.classList.add('error');
            console.error('Schema initialization error:', error);
        }
    }

    // Function to read JSON file
    async function readJSONFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const json = JSON.parse(e.target.result);
                    resolve(json);
                } catch (error) {
                    reject(new Error('Invalid JSON file'));
                }
            };
            reader.onerror = () => reject(new Error('Error reading file'));
            reader.readAsText(file);
        });
    }

    // Function to upload data
    async function uploadData(file) {
        try {
            const data = await readJSONFile(file);
            const response = await fetch('/api/data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ data })
            });

            const result = await response.json();
            if (result.success) {
                dataStatus.textContent = `Data loaded: ${result.summary.type} with ${result.summary.size} items`;
                dataStatus.classList.add('loaded');
                addMessage('System', 'Data uploaded successfully! You can now ask questions about both the schema and data.');
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            dataStatus.textContent = 'Error loading data';
            dataStatus.classList.remove('loaded');
            dataStatus.classList.add('error');
            addMessage('System', `Error uploading data: ${error.message}`);
        }
    }

    // Function to add a message to the chat
    function addMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender.toLowerCase()}-message`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return messageDiv;
    }

    // Function to send message to the assistant
    async function sendMessage() {
        if (isProcessing || !userInput.value.trim()) return;

        const message = userInput.value.trim();
        userInput.value = '';
        addMessage('User', message);
        isProcessing = true;

        // Add typing indicator
        const typingIndicator = createTypingIndicator();
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            // Remove typing indicator
            chatMessages.removeChild(typingIndicator);

            const result = await response.json();
            if (result.success) {
                addMessage('Assistant', result.message);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            // Remove typing indicator if still present
            if (typingIndicator.parentNode === chatMessages) {
                chatMessages.removeChild(typingIndicator);
            }
            addMessage('System', `Error: ${error.message}`);
        } finally {
            isProcessing = false;
        }
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    uploadDataBtn.addEventListener('click', () => {
        const file = dataFileInput.files[0];
        if (file) {
            uploadData(file);
        } else {
            addMessage('System', 'Please select a data file first!');
        }
    });

    clearBtn.addEventListener('click', async () => {
        chatMessages.innerHTML = '';
        try {
            await fetch('/api/clear', { method: 'POST' });
            addMessage('System', 'Conversation cleared');
        } catch (error) {
            addMessage('System', 'Error clearing conversation');
        }
    });

    // Initialize the application
    initializeSchema();
});