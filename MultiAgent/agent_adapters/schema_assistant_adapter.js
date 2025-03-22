/**
 * Schema Assistant Adapter
 * 
 * This adapter connects the Node.js-based schema assistant agent with the central message hub.
 * Copy this file to your Agent_1 directory and import it in your server.js file.
 */

const axios = require('axios');

class MessageHubClient {
  constructor(hubUrl = 'http://localhost:8000') {
    this.hubUrl = hubUrl;
    this.agentId = 'agent1';
  }

  /**
   * Send a message to the central hub
   * @param {string} messageType - Type of message
   * @param {any} content - Message content
   * @param {string} target - Target agent (default: 'hub')
   * @returns {Promise<boolean>} - Success status
   */
  async sendMessage(messageType, content, target = 'hub') {
    const message = {
      type: messageType,
      content,
      source: this.agentId,
      target,
      timestamp: new Date().toISOString()
    };

    try {
      const response = await axios.post(
        `${this.hubUrl}/api/message`,
        message,
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 5000
        }
      );
      return response.status === 200;
    } catch (error) {
      console.error('Error sending message to hub:', error.message);
      return false;
    }
  }

  /**
   * Send a schema response to the hub
   * @param {any} schemaResponse - The schema response to send
   * @returns {Promise<boolean>} - Success status
   */
  async sendSchemaResponse(schemaResponse) {
    return this.sendMessage('schema.response', schemaResponse);
  }

  /**
   * Register this agent with the hub (optional)
   * @returns {Promise<boolean>} - Success status
   */
  async registerWithHub() {
    const message = {
      type: 'agent.register',
      content: {
        agent_id: this.agentId,
        agent_type: 'schema',
        capabilities: ['schema_analysis', 'schema_generation', 'schema_explanation']
      },
      source: this.agentId,
      timestamp: new Date().toISOString()
    };

    try {
      const response = await axios.post(
        `${this.hubUrl}/api/message`,
        message,
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 5000
        }
      );
      return response.status === 200;
    } catch (error) {
      console.error('Error registering with hub:', error.message);
      return false;
    }
  }
}

module.exports = MessageHubClient;

/**
 * Example usage in Express app:
 * 
 * ```javascript
 * const MessageHubClient = require('./agent_adapters/schema_assistant_adapter');
 * 
 * // Initialize the client
 * const hubClient = new MessageHubClient();
 * 
 * // Register with the hub when the server starts
 * hubClient.registerWithHub().then(success => {
 *   console.log('Hub registration:', success ? 'successful' : 'failed');
 * });
 * 
 * // Add an endpoint to handle messages from the hub
 * app.post('/api/message', async (req, res) => {
 *   const { type, content } = req.body;
 *   
 *   if (type === 'schema.question') {
 *     // Process the schema question
 *     const result = await yourSchemaProcessor(content);
 *     
 *     // Send the result back to the hub
 *     hubClient.sendSchemaResponse(result);
 *   }
 *   
 *   res.json({ status: 'success' });
 * });
 * ```
 */ 