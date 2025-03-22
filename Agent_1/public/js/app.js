document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const schemaFileInput = document.getElementById('schema-file');
    const uiContainer = document.getElementById('ui-container');

    let jsonSchema = null;

    // Upload and parse JSON schema
    uploadBtn.addEventListener('click', () => {
        const file = schemaFileInput.files[0];
        if (!file) {
            alert('Please select a JSON schema file first');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                jsonSchema = JSON.parse(e.target.result);
                addMessage('System', 'JSON Schema uploaded successfully!');
            } catch (error) {
                alert('Error parsing JSON file: ' + error.message);
            }
        };
        reader.readAsText(file);
    });

    // Send message to the assistant
    sendBtn.addEventListener('click', () => {
        const message = userInput.value.trim();
        if (!message) return;

        if (!jsonSchema) {
            alert('Please upload a JSON schema first');
            return;
        }

        addMessage('User', message);
        userInput.value = '';

        // Call to backend API will go here
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message,
                schema: jsonSchema
            }),
        })
            .then(response => response.json())
            .then(data => {
                addMessage('Assistant', data.message);

                // If there's UI to render
                if (data.ui) {
                    renderUI(data.ui);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('System', 'Error communicating with the assistant');
            });
    });

    // Add message to chat
    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender.toLowerCase()}-message`;
        messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Render UI from assistant response
    function renderUI(uiConfig) {
        // This will be implemented later
        uiContainer.innerHTML = '<pre>' + JSON.stringify(uiConfig, null, 2) + '</pre>';
    }
});