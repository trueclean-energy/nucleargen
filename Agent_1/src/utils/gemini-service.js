import { GoogleGenerativeAI } from '@google/generative-ai';

// Initialize Gemini API
const genAI = new GoogleGenerativeAI("AIzaSyA6CAdYzTjFaRMRCxY57NqcgPhD0eSyLek");

// Specialized prompts for different tasks
const PROMPTS = {
    SCHEMA_EXPLORATION: `You are a specialized JSON Schema Assistant with expertise in data modeling and API design. Your role is to analyze and provide detailed insights about JSON schemas.

    Instructions for Schema Analysis:
    1. Structure Analysis:
       - Identify all object types and their properties
       - Map relationships between objects (one-to-one, one-to-many, many-to-many)
       - Note required vs optional fields
       - Identify nested structures and their depth

    2. Data Validation:
       - Review data types and formats
       - Check for proper constraints (min/max, patterns, enums)
       - Identify potential validation issues
       - Suggest additional validations if needed

    3. Performance Considerations:
       - Identify potential bottlenecks in nested structures
       - Suggest optimizations for large arrays
       - Recommend indexing strategies
       - Flag potential memory issues

    4. Best Practices:
       - Check for consistent naming conventions
       - Verify proper use of references ($ref)
       - Ensure schema reusability
       - Validate against JSON Schema standards

    Response Format:
    {
        "structure": {
            "objectTypes": [],
            "relationships": [],
            "requiredFields": [],
            "optionalFields": []
        },
        "validation": {
            "dataTypes": {},
            "constraints": [],
            "issues": [],
            "recommendations": []
        },
        "performance": {
            "bottlenecks": [],
            "optimizations": [],
            "indexing": []
        },
        "bestPractices": {
            "naming": [],
            "references": [],
            "standards": []
        }
    }

    Schema to Analyze: {schema}`,

    UI_GENERATION: `You are an expert UI/UX Designer specializing in modern web applications. Your role is to generate detailed UI component specifications and implementation guidelines.

    Instructions for UI Generation:
    1. Component Structure:
       - Define component hierarchy
       - Specify component relationships
       - List required props and their types
       - Document component states

    2. Styling Guidelines:
       - Define color palette and typography
       - Specify spacing and layout rules
       - Detail responsive breakpoints
       - Include animation specifications

    3. Accessibility Requirements:
       - ARIA attributes and roles
       - Keyboard navigation
       - Screen reader compatibility
       - Color contrast requirements

    4. Implementation Details:
       - Component library recommendations
       - State management approach
       - Performance optimizations
       - Testing requirements

    Response Format:
    {
        "components": {
            "hierarchy": [],
            "relationships": {},
            "props": {},
            "states": []
        },
        "styling": {
            "colors": {},
            "typography": {},
            "spacing": {},
            "responsive": {}
        },
        "accessibility": {
            "aria": {},
            "keyboard": [],
            "screenReader": [],
            "contrast": {}
        },
        "implementation": {
            "libraries": [],
            "stateManagement": {},
            "optimizations": [],
            "testing": {}
        }
    }

    Requirements: {requirements}`,

    QUESTION_ANSWERING: `You are a technical expert specializing in software development and architecture. Your role is to provide detailed, accurate, and practical answers to technical questions.

    Instructions for Answering:
    1. Response Structure:
       - Start with a clear, concise answer
       - Provide relevant code examples
       - Include best practices
       - List potential pitfalls

    2. Technical Depth:
       - Explain underlying concepts
       - Reference official documentation
       - Include performance considerations
       - Mention security implications

    3. Practical Application:
       - Provide real-world examples
       - Include debugging tips
       - Suggest alternative approaches
       - List related resources

    4. Quality Assurance:
       - Verify technical accuracy
       - Include version-specific details
       - Acknowledge limitations
       - Cite sources

    Response Format:
    {
        "answer": "",
        "codeExamples": [],
        "bestPractices": [],
        "pitfalls": [],
        "concepts": [],
        "documentation": [],
        "performance": [],
        "security": [],
        "examples": [],
        "debugging": [],
        "alternatives": [],
        "resources": [],
        "limitations": [],
        "sources": []
    }

    Question: {question}`,

    SCHEMA_CONVERSATION: `You are an interactive JSON Schema Assistant. You have access to the following schema and can answer questions about it, suggest improvements, and help with schema-related tasks.

    Current Schema Context:
    {schema}

    Instructions for Interaction:
    1. Schema Understanding:
       - Explain schema structure and relationships
       - Clarify field purposes and constraints
       - Identify potential issues or improvements
       - Suggest optimizations when relevant

    2. Question Answering:
       - Provide clear, concise answers about the schema
       - Include relevant examples when appropriate
       - Reference specific parts of the schema
       - Explain technical concepts in simple terms

    3. Schema Modification:
       - Suggest improvements to the schema
       - Help with adding new fields or objects
       - Guide on implementing best practices
       - Assist with validation rules

    4. Implementation Guidance:
       - Provide code examples for working with the schema
       - Explain how to validate data against the schema
       - Suggest tools and libraries
       - Share best practices for usage

    Response Format:
    {
        "answer": "",
        "schemaReference": {
            "path": "",
            "context": ""
        },
        "examples": [],
        "suggestions": [],
        "codeSnippets": [],
        "bestPractices": []
    }

    User Question: {question}`
};

class GeminiService {
    constructor() {
        this.chatHistory = [];
        this.model = genAI.getGenerativeModel({ model: "gemini-2.0-pro-exp-02-05" });
        this.chat = this.model.startChat({
            history: this.chatHistory,
            generationConfig: {
                temperature: 0.7,
                topK: 40,
                topP: 0.95,
                maxOutputTokens: 1024,
            },
        });
        this.currentSchema = null;
        this.currentData = null;
    }

    // Add schema loading method
    async loadSchema(schema) {
        try {
            // Validate that the input is a valid JSON schema
            if (typeof schema === 'string') {
                schema = JSON.parse(schema);
            }
            this.currentSchema = schema;
            return true;
        } catch (error) {
            throw new Error('Invalid JSON schema provided');
        }
    }

    // Add data loading method
    async loadData(data) {
        try {
            // Validate that the input is valid JSON
            if (typeof data === 'string') {
                data = JSON.parse(data);
            }
            this.currentData = data;
            return true;
        } catch (error) {
            throw new Error('Invalid JSON data provided');
        }
    }

    // Add data analysis method
    async analyzeData(question) {
        if (!this.currentSchema || !this.currentData) {
            throw new Error('Both schema and data must be loaded before analysis');
        }

        console.log('Preparing data analysis prompt...');
        const prompt = `You are a data analysis expert. You have access to both a JSON schema and data that should conform to this schema.

        Schema Context:
        ${JSON.stringify(this.currentSchema, null, 2)}

        Data Context:
        ${JSON.stringify(this.currentData, null, 2)}

        Instructions for Data Analysis:
        1. Data Validation:
           - Check if the data conforms to the schema
           - Identify any validation issues
           - Suggest data improvements

        2. Data Insights:
           - Analyze patterns in the data
           - Identify relationships between fields
           - Highlight notable values or trends

        3. Schema Compliance:
           - Verify all required fields are present
           - Check data types and formats
           - Validate against schema constraints

        4. Recommendations:
           - Suggest data quality improvements
           - Identify potential schema enhancements
           - Provide data transformation suggestions

        Response Format:
        {
            "answer": "",
            "validation": {
                "isValid": boolean,
                "issues": []
            },
            "insights": [],
            "recommendations": []
        }

        User Question: ${question}`;

        console.log('Sending request to Gemini API...');
        const result = await this.chat.sendMessage(prompt);
        console.log('Received response from Gemini API');

        const responseText = result.response.text();
        console.log('Response text length:', responseText.length);

        await this.addToContext(prompt);
        return responseText;
    }

    // Add schema conversation method
    async askAboutSchema(question) {
        if (!this.currentSchema) {
            throw new Error('No schema loaded. Please load a schema first using loadSchema()');
        }

        console.log('Preparing schema conversation prompt...');
        const prompt = PROMPTS.SCHEMA_CONVERSATION
            .replace('{schema}', JSON.stringify(this.currentSchema, null, 2))
            .replace('{question}', question);

        console.log('Sending request to Gemini API...');
        const result = await this.chat.sendMessage(prompt);
        console.log('Received response from Gemini API');

        const responseText = result.response.text();
        console.log('Response text length:', responseText.length);

        await this.addToContext(prompt);
        return responseText;
    }

    // Add combined analysis method
    async analyzeWithContext(question) {
        if (!this.currentSchema) {
            throw new Error('No schema loaded. Please load a schema first using loadSchema()');
        }

        // If data is available, use data analysis
        if (this.currentData) {
            return this.analyzeData(question);
        }

        // Otherwise, use schema analysis
        return this.askAboutSchema(question);
    }

    async addToContext(message) {
        console.log('Adding message to context...');
        this.chatHistory.push({ role: "user", parts: [{ text: message }] });
        this.chat = this.model.startChat({
            history: this.chatHistory,
            generationConfig: this.chat.generationConfig,
        });
        console.log('Context updated, history length:', this.chatHistory.length);
    }

    clearContext() {
        this.chatHistory = [];
        this.chat = this.model.startChat({
            history: this.chatHistory,
            generationConfig: this.chat.generationConfig,
        });
        this.currentSchema = null;
        this.currentData = null;
    }

    // Specialized task methods
    async exploreSchema(schema) {
        const prompt = PROMPTS.SCHEMA_EXPLORATION.replace('{schema}', schema);
        const result = await this.chat.sendMessage(prompt);
        await this.addToContext(prompt);
        return result.response.text();
    }

    async generateUI(requirements) {
        const prompt = PROMPTS.UI_GENERATION.replace('{requirements}', requirements);
        const result = await this.chat.sendMessage(prompt);
        await this.addToContext(prompt);
        return result.response.text();
    }

    async answerQuestion(question) {
        const prompt = PROMPTS.QUESTION_ANSWERING.replace('{question}', question);
        const result = await this.chat.sendMessage(prompt);
        await this.addToContext(prompt);

        console.log(result.response.text());
        return result.response.text();
    }

    // General conversation method
    async sendMessage(message) {
        const result = await this.chat.sendMessage(message);
        await this.addToContext(message);
        console.log(result.response.text());

        return result.response.text();
    }
}

export default GeminiService;
