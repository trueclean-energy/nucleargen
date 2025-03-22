// Update public/js/app.js

document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const uploadSchemaBtn = document.getElementById('upload-schema-btn');
    const uploadDataBtn = document.getElementById('upload-data-btn');
    const schemaFileInput = document.getElementById('schema-file');
    const dataFileInput = document.getElementById('data-file');
    const uiContainer = document.getElementById('ui-container');
    const clearBtn = document.createElement('button');
    const schemaStatus = document.getElementById('schema-status');
    const dataStatus = document.getElementById('data-status');

    // Add clear button
    clearBtn.textContent = 'Clear Chat';
    clearBtn.className = 'clear-btn';
    document.querySelector('.chat-input').appendChild(clearBtn);

    let currentSchema = null;
    let currentData = null;
    let isProcessing = false;

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

    // Function to upload schema
    async function uploadSchema(file) {
        try {
            const schema = await readJSONFile(file);
            const response = await fetch('/api/schema', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ schema })
            });

            const result = await response.json();
            if (result.success) {
                currentSchema = schema;
                schemaStatus.textContent = `Schema loaded: ${result.summary.type} with ${result.summary.propertyCount} properties`;
                schemaStatus.classList.add('loaded');
                addMessage('System', 'Schema uploaded successfully! You can now ask questions about the schema.');
                // Enable chat after schema upload
                userInput.disabled = false;
                sendBtn.disabled = false;
                userInput.placeholder = "Ask about your JSON schema...";
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            addMessage('System', `Error uploading schema: ${error.message}`);
        }
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
                currentData = data;
                dataStatus.textContent = `Data loaded: ${result.summary.type} with ${result.summary.size} items`;
                dataStatus.classList.add('loaded');
                addMessage('System', 'Data uploaded successfully! You can now ask questions about the data.');
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            addMessage('System', `Error uploading data: ${error.message}`);
        }
    }

    // Event listeners for upload buttons
    uploadSchemaBtn.addEventListener('click', () => {
        const file = schemaFileInput.files[0];
        if (file) {
            uploadSchema(file);
        } else {
            addMessage('System', 'Please select a schema file first!');
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

    // Send message to the assistant
    sendBtn.addEventListener('click', sendMessage);

    // Also send on Enter key (but allow shift+enter for new lines)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Clear chat and context
    clearBtn.addEventListener('click', () => {
        // Clear UI
        chatMessages.innerHTML = '';
        uiContainer.innerHTML = '';

        // Clear server context
        fetch('/api/clear', {
            method: 'POST',
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addMessage('System', 'Conversation cleared');
                }
            })
            .catch(error => {
                console.error('Error clearing context:', error);
            });
    });

    // Send message function
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message || isProcessing) return;

        if (!currentSchema) {
            addMessage('System', 'Please upload a schema first!');
            return;
        }

        // Show user message
        addMessage('User', message);
        userInput.value = '';

        // Show loading indicator
        isProcessing = true;
        const loadingMsg = addMessage('Assistant', '...');

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const result = await response.json();
            if (result.success) {
                // Remove loading indicator
                chatMessages.removeChild(loadingMsg);
                isProcessing = false;

                // Add assistant response
                addMessage('Assistant', result.message);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            // Remove loading indicator
            chatMessages.removeChild(loadingMsg);
            isProcessing = false;

            console.error('Error:', error);
            addMessage('System', 'Error communicating with the assistant: ' + error.message);
        }
    }

    // Add message to chat
    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender.toLowerCase()}-message`;

        // Format code blocks if present
        const formattedText = formatMessageText(text);

        messageDiv.innerHTML = `<strong>${sender}:</strong> ${formattedText}`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        return messageDiv;
    }

    // Format message text with code highlighting
    function formatMessageText(text) {
        // Simple code block formatting
        let formattedText = text;

        // Replace code blocks with formatted HTML
        formattedText = formattedText.replace(/```(\w*)\n([\s\S]*?)```/g, (match, language, code) => {
            return `<pre class="code-block ${language}"><code>${escapeHTML(code)}</code></pre>`;
        });

        // Replace line breaks with <br>
        formattedText = formattedText.replace(/\n/g, '<br>');

        // Format inline code
        formattedText = formattedText.replace(/`([^`]+)`/g, '<code>$1</code>');

        return formattedText;
    }

    // Escape HTML special characters
    function escapeHTML(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Render UI components from assistant response
    function renderUI(uiComponents) {
        uiContainer.innerHTML = '';

        // Create a title
        const title = document.createElement('h4');
        title.textContent = 'Generated UI Components';
        uiContainer.appendChild(title);

        // Create tabs if multiple components
        if (Array.isArray(uiComponents) && uiComponents.length > 1) {
            const tabContainer = document.createElement('div');
            tabContainer.className = 'tab-container';

            const contentContainer = document.createElement('div');
            contentContainer.className = 'tab-content-container';

            uiComponents.forEach((component, index) => {
                // Create tab
                const tab = document.createElement('button');
                tab.className = 'tab-button';
                tab.textContent = component.name || `Component ${index + 1}`;

                // Create content
                const content = document.createElement('div');
                content.className = 'tab-content';
                content.style.display = index === 0 ? 'block' : 'none';

                // Render component mockup
                content.innerHTML = renderMockComponent(component);

                // Add click handler
                tab.addEventListener('click', () => {
                    // Hide all content
                    document.querySelectorAll('.tab-content').forEach(el => {
                        el.style.display = 'none';
                    });

                    // Remove active class
                    document.querySelectorAll('.tab-button').forEach(el => {
                        el.classList.remove('active');
                    });

                    // Show this content
                    content.style.display = 'block';
                    tab.classList.add('active');
                });

                // Activate first tab
                if (index === 0) {
                    tab.classList.add('active');
                }

                tabContainer.appendChild(tab);
                contentContainer.appendChild(content);
            });

            uiContainer.appendChild(tabContainer);
            uiContainer.appendChild(contentContainer);
        } else {
            // Single component or object
            const component = Array.isArray(uiComponents) ? uiComponents[0] : uiComponents;
            uiContainer.innerHTML += renderMockComponent(component);
        }
    }

    // Render a mock UI component based on description
    function renderMockComponent(component) {
        // This is a simple mockup renderer
        // In a real app, you'd use a proper UI library

        let html = '<div class="mock-component">';

        // Component name/type
        const componentName = component.name || component.type || 'Component';
        html += `<div class="component-header">${componentName}</div>`;

        // For form components
        if (component.type === 'form' || componentName.toLowerCase().includes('form')) {
            html += renderMockForm(component);
        }
        // For data display components
        else if (component.type === 'table' || componentName.toLowerCase().includes('table')) {
            html += renderMockTable(component);
        }
        // For container components
        else if (component.type === 'container' || component.children) {
            html += renderMockContainer(component);
        }
        // Default fallback
        else {
            html += `<div class="component-body">
          <pre>${JSON.stringify(component, null, 2)}</pre>
        </div>`;
        }

        html += '</div>';
        return html;
    }

    // Render a mock form
    function renderMockForm(component) {
        let html = '<div class="mock-form">';

        // Fields
        const fields = component.fields || component.properties || [];

        if (Array.isArray(fields)) {
            fields.forEach(field => {
                html += renderFormField(field);
            });
        } else if (typeof fields === 'object') {
            // Handle when fields is an object
            Object.keys(fields).forEach(key => {
                const field = fields[key];
                field.name = field.name || key;
                html += renderFormField(field);
            });
        }

        // Add submit button
        html += `<button class="mock-button">Submit</button>`;

        html += '</div>';
        return html;
    }

    // Render a form field
    function renderFormField(field) {
        const fieldType = field.type || 'text';
        const fieldName = field.name || 'field';
        const fieldLabel = field.label || fieldName;
        const required = field.required ? 'required' : '';

        let html = `<div class="mock-field">
        <label>${fieldLabel}${required ? ' *' : ''}</label>`;

        // Different input types
        switch (fieldType) {
            case 'textarea':
                html += `<textarea class="mock-input" placeholder="${fieldLabel}"></textarea>`;
                break;
            case 'select':
                html += `<select class="mock-select">
            ${(field.options || []).map(opt => `<option>${opt.label || opt}</option>`).join('')}
          </select>`;
                break;
            case 'checkbox':
                html += `<input type="checkbox" class="mock-checkbox" /> ${field.description || ''}`;
                break;
            default:
                html += `<input type="${fieldType}" class="mock-input" placeholder="${fieldLabel}" />`;
        }

        html += '</div>';
        return html;
    }

    // Render a mock table
    function renderMockTable(component) {
        let html = '<div class="mock-table-container">';

        // Table
        html += '<table class="mock-table">';

        // Headers
        const columns = component.columns || [];
        if (columns.length > 0) {
            html += '<thead><tr>';
            columns.forEach(column => {
                html += `<th>${column.label || column}</th>`;
            });
            html += '</tr></thead>';
        }

        // Body
        html += '<tbody>';
        for (let i = 0; i < 3; i++) {
            html += '<tr>';
            columns.forEach(() => {
                html += `<td>Sample data</td>`;
            });
            html += '</tr>';
        }
        html += '</tbody>';

        html += '</table>';
        html += '</div>';

        return html;
    }

    // Render a container
    function renderMockContainer(component) {
        let html = '<div class="mock-container">';

        const children = component.children || [];
        children.forEach(child => {
            html += renderMockComponent(child);
        });

        if (children.length === 0) {
            html += '<div class="empty-container">Container</div>';
        }

        html += '</div>';
        return html;
    }

    // Disable chat until schema is uploaded
    userInput.disabled = true;
    sendBtn.disabled = true;
    userInput.placeholder = "Upload a schema first...";
});