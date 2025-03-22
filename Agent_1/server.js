import express from 'express';
// const cors = require('cors');
import cors from 'cors';
// const dotenv = require('dotenv');
import dotenv from 'dotenv';
// const path = require('path');
import path from 'path';

import GeminiService from './src/utils/gemini-service.js';

import { fileURLToPath } from 'url';
import { dirname } from 'path';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const geminiService = new GeminiService();
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.static('public'));

// Schema and data storage - in-memory for prototype
let jsonSchema = null;
let jsonData = null;
let schemaChunks = [];
const MAX_CHUNK_SIZE = 10000; // Adjust based on token limits

// Helper function to chunk the schema
function chunkSchema(schema) {
    const schemaStr = JSON.stringify(schema);
    const chunks = [];

    // Simple chunking by properties for prototype
    if (schema.properties) {
        const properties = Object.keys(schema.properties);
        let currentChunk = { type: schema.type, properties: {} };
        let currentSize = 0;

        for (const prop of properties) {
            const propData = schema.properties[prop];
            const propSize = JSON.stringify(propData).length;

            if (currentSize + propSize > MAX_CHUNK_SIZE) {
                chunks.push(currentChunk);
                currentChunk = { type: schema.type, properties: {} };
                currentSize = 0;
            }

            currentChunk.properties[prop] = propData;
            currentSize += propSize;
        }

        if (Object.keys(currentChunk.properties).length > 0) {
            chunks.push(currentChunk);
        }
    } else {
        // For non-object schemas, just use as is
        chunks.push(schema);
    }

    return chunks;
}


// API route for uploading schema
app.post('/api/schema', async (req, res) => {
    try {
        jsonSchema = req.body.schema;
        schemaChunks = chunkSchema(jsonSchema);

        // Load schema into Gemini service
        await geminiService.loadSchema(jsonSchema);

        // Generate a summary of the schema
        const schemaSummary = {
            type: jsonSchema.type,
            propertyCount: Object.keys(jsonSchema.properties || {}).length,
            chunkCount: schemaChunks.length
        };

        res.json({
            success: true,
            message: 'Schema uploaded successfully',
            summary: schemaSummary
        });
    } catch (error) {
        console.error('Schema upload error:', error);
        res.status(400).json({ success: false, error: error.message });
    }
});

// API route for uploading data
app.post('/api/data', async (req, res) => {
    try {
        jsonData = req.body.data;

        // Load data into Gemini service
        await geminiService.loadData(jsonData);

        // Generate a summary of the data
        const dataSummary = {
            type: Array.isArray(jsonData) ? 'array' : typeof jsonData,
            size: Array.isArray(jsonData) ? jsonData.length : 1,
            properties: Object.keys(jsonData)
        };

        res.json({
            success: true,
            message: 'Data uploaded successfully',
            summary: dataSummary
        });
    } catch (error) {
        console.error('Data upload error:', error);
        res.status(400).json({ success: false, error: error.message });
    }
});

// API route for chat with context
app.post('/api/chat', async (req, res) => {
    try {
        const { message } = req.body;

        // Ensure schema is uploaded
        if (!jsonSchema) {
            return res.status(400).json({
                success: false,
                error: 'No schema available. Please upload a schema first.'
            });
        }

        console.log('User message:', message);

        // Use the combined analysis method that handles both schema and data
        const response = await geminiService.analyzeWithContext(message);
        console.log('Raw Gemini response:', response);

        // Clean up the response by removing markdown code blocks
        let cleanedResponse = response.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
        console.log('Cleaned response:', cleanedResponse);

        // Try to parse as JSON first, if it fails, use the raw text
        let formattedResponse;
        let examples = [];
        try {
            console.log('Attempting to parse response as JSON...');
            const parsedResponse = JSON.parse(cleanedResponse);
            console.log('Successfully parsed JSON response:', parsedResponse);

            // Extract answer and additional fields
            formattedResponse = parsedResponse.answer || cleanedResponse;

            // Add validation results if available
            if (parsedResponse.validation) {
                formattedResponse += '\n\nValidation Results:\n';
                formattedResponse += `Valid: ${parsedResponse.validation.isValid}\n`;
                if (parsedResponse.validation.issues.length > 0) {
                    formattedResponse += 'Issues:\n' + parsedResponse.validation.issues.join('\n');
                }
            }

            // Add insights if available
            if (parsedResponse.insights && parsedResponse.insights.length > 0) {
                formattedResponse += '\n\nInsights:\n' + parsedResponse.insights.join('\n');
            }

            // Add recommendations if available
            if (parsedResponse.recommendations && parsedResponse.recommendations.length > 0) {
                formattedResponse += '\n\nRecommendations:\n' + parsedResponse.recommendations.join('\n');
            }

            // Add examples if available
            if (parsedResponse.examples && Array.isArray(parsedResponse.examples)) {
                examples = parsedResponse.examples.map(example => example.description);
            }
            console.log('Extracted answer and additional fields:', { formattedResponse, examples });
        } catch (e) {
            console.log('JSON parsing failed, attempting regex extraction...');
            console.log('Parse error:', e.message);

            // If not valid JSON, try to extract answer from raw text
            const answerMatch = cleanedResponse.match(/"answer":\s*"([^"]+)"/);
            formattedResponse = answerMatch ? answerMatch[1] : cleanedResponse;
            console.log('Regex extraction result:', formattedResponse);
        }

        // Clean up the response
        console.log('Cleaning up response...');
        formattedResponse = formattedResponse
            .replace(/\\n/g, '\n')
            .replace(/\\"/g, '"');
        console.log('Final formatted response:', formattedResponse);

        // Combine answer with examples if available
        let finalResponse = formattedResponse;
        if (examples.length > 0) {
            finalResponse += '\n\nExamples:\n' + examples.join('\n\n');
        }

        // Check if response is too short or incomplete
        if (finalResponse.length < 50) {
            console.log('Warning: Response seems too short or incomplete');
        }

        res.json({
            success: true,
            message: finalResponse
        });
    } catch (error) {
        console.error('Chat API error:', error);
        console.error('Error stack:', error.stack);
        res.status(500).json({
            success: false,
            error: 'Error processing request',
            details: error.message
        });
    }
});

// API route for clear context
app.post('/api/clear', (req, res) => {
    try {
        geminiService.clearContext();
        res.json({ success: true, message: 'Conversation context cleared' });
    } catch (error) {
        console.error('Context clear error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

// Simple intent detection - can be improved
function detectIntent(message) {
    const lowerMsg = message.toLowerCase();

    if (lowerMsg.includes('structure') ||
        lowerMsg.includes('schema') ||
        lowerMsg.includes('properties') ||
        lowerMsg.includes('fields')) {
        return 'SCHEMA_EXPLORATION';
    }

    if (lowerMsg.includes('ui') ||
        lowerMsg.includes('interface') ||
        lowerMsg.includes('component') ||
        lowerMsg.includes('design')) {
        return 'UI_GENERATION';
    }

    return 'QUESTION';
}

// Find the most relevant chunk for a query
function findRelevantChunk(message, chunks) {
    const lowerMsg = message.toLowerCase();

    // For prototype, use simple keyword matching
    // In a real app, you'd use embeddings or more sophisticated matching
    for (const chunk of chunks) {
        const properties = Object.keys(chunk.properties || {});
        for (const prop of properties) {
            if (lowerMsg.includes(prop.toLowerCase())) {
                return chunk;
            }
        }
    }

    // If no specific match, return first chunk as default
    return chunks[0];
}

// Extract UI requirements from a message
function extractUIRequirements(message, schema) {
    // For prototype, extract mentioned properties
    const lowerMsg = message.toLowerCase();
    const properties = Object.keys(schema.properties || {});
    const mentionedProps = {};

    for (const prop of properties) {
        if (lowerMsg.includes(prop.toLowerCase())) {
            mentionedProps[prop] = schema.properties[prop];
        }
    }

    // If no specific properties mentioned, use entire schema
    return Object.keys(mentionedProps).length > 0 ?
        { type: schema.type, properties: mentionedProps } :
        schema;
}


// Format JSON response to readable text
function formatResponse(parsedResponse) {
    // This is a simple formatter for the prototype
    // You would customize this based on response structure

    if (typeof parsedResponse === 'string') {
        return parsedResponse;
    }

    let formattedText = '';

    // Handle common response formats
    if (parsedResponse.answer) {
        formattedText = parsedResponse.answer;
    } else if (parsedResponse.structure) {
        formattedText = `Schema Analysis:\n${JSON.stringify(parsedResponse.structure, null, 2)}`;
    } else if (parsedResponse.components) {
        formattedText = `UI Components:\n${JSON.stringify(parsedResponse.components, null, 2)}`;
    } else {
        // Default fallback
        formattedText = JSON.stringify(parsedResponse, null, 2);
    }

    return formattedText;
}


// Serve the main app
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});