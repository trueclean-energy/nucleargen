# Vyom Project Structure

## Overview
Vyom is a sophisticated code analysis and visualization tool designed to help developers understand and navigate complex codebases. The project follows a modular architecture that separates concerns into distinct components while maintaining simplicity and long-term maintainability.

## Project Structure

```
vyom-alpha/
├── vyom/                    # Main package directory
│   ├── cli.py              # Command-line interface implementation
│   ├── viewer.py           # Code visualization and UI components
│   ├── llm_service.py      # Language model integration service
│   ├── extractor.py        # Code analysis and extraction logic
│   ├── converter.py        # Data format conversion utilities
│   ├── db.py              # Database operations and management
│   ├── schema/            # Data schema definitions
│   ├── importers/         # Code importers for different languages
│   └── setup_api_keys.py  # API key management
├── tests/                  # Test suite
├── docs/                   # Documentation
├── data/                   # Data storage
├── scripts/               # Utility scripts
└── requirements.txt       # Project dependencies
```

## Key Components

### Core Components

1. **CLI Interface** (`cli.py`)
   - Provides the command-line interface for Vyom
   - Handles user commands and interactions
   - Manages the workflow of code analysis and visualization

2. **Viewer** (`viewer.py`)
   - Implements the visualization engine
   - Renders code relationships and dependencies
   - Provides interactive UI components for code navigation

3. **LLM Service** (`llm_service.py`)
   - Integrates with language models for code analysis
   - Handles natural language processing of code
   - Provides intelligent code understanding capabilities

4. **Extractor** (`extractor.py`)
   - Analyzes source code to extract relationships
   - Identifies dependencies and code structures
   - Generates metadata for visualization

5. **Converter** (`converter.py`)
   - Handles data format conversions
   - Transforms code analysis results into visualizable formats
   - Manages data serialization and deserialization

6. **Database** (`db.py`)
   - Manages persistent storage of analysis results
   - Handles data caching and retrieval
   - Provides data persistence layer

### Supporting Components

1. **Schema** (`schema/`)
   - Defines data structures and relationships
   - Ensures consistent data representation
   - Provides type definitions and validation

2. **Importers** (`importers/`)
   - Contains language-specific code parsers
   - Supports multiple programming languages
   - Extends Vyom's language support capabilities

3. **API Key Management** (`setup_api_keys.py`)
   - Manages API key configuration
   - Handles secure credential storage
   - Provides key setup utilities

### Development Tools

1. **Tests** (`tests/`)
   - Comprehensive test suite
   - Ensures code quality and reliability
   - Supports continuous integration

2. **Documentation** (`docs/`)
   - Project documentation
   - Usage guides and examples
   - API references

3. **Scripts** (`scripts/`)
   - Development and maintenance utilities
   - Build and deployment tools
   - Automation scripts

## Design Philosophy

Vyom is designed with the following principles in mind:

- **Simplicity**: Each component has a single, well-defined responsibility
- **Maintainability**: Clear separation of concerns and modular architecture
- **Extensibility**: Easy to add new features and language support
- **Reliability**: Comprehensive testing and error handling
- **Performance**: Efficient data processing and visualization

## LLM Implementation

The LLM (Large Language Model) integration in Vyom is implemented through the `llm_service.py` module, which provides a flexible and extensible interface for AI-powered code analysis and visualization. The implementation supports multiple LLM providers and is designed for long-term maintainability.

### Core Features

1. **Multi-Provider Support**
   - Currently supports Together AI and Brave API
   - Modular design allows easy addition of new LLM providers
   - Provider selection through environment configuration

2. **Visualization Generation**
   - Converts natural language requests into visualization code
   - Supports multiple visualization types:
     - Mermaid diagrams (flowcharts, sequence diagrams, class diagrams, ER diagrams)
     - SAPHIRE-specific visualizations (fault trees, event trees)
   - Context-aware generation using code structure and relationships

3. **Data Analysis Pipeline**
   - Two-stage visualization process:
     1. Data summarization and planning
     2. Detailed visualization generation
   - Intelligent context handling for large codebases
   - Fallback mechanisms for error handling

### Implementation Details

1. **TogetherAIService Class**
   ```python
   class TogetherAIService:
       def __init__(self, api_key: Optional[str] = None)
       def generate_visualization(self, prompt: str, data_context: Optional[Dict[str, Any]] = None)
       def summarize_data(self, prompt: str, data_summary: Dict[str, Any])
       def generate_complete_visualization(self, prompt: str, focused_data: Dict[str, Any], plan: Dict[str, Any])
   ```

2. **Key Methods**
   - `generate_visualization`: Creates visualization code from user prompts
   - `summarize_data`: Analyzes data structure and creates visualization plans
   - `generate_complete_visualization`: Produces final visualization with detailed data

3. **Error Handling**
   - Graceful fallback mechanisms
   - Comprehensive logging
   - JSON response validation
   - API error handling

### Configuration

The LLM service can be configured through:
- Environment variables (TOGETHER_API_KEY, BRAVE_API_KEY)
- .env file in the project root
- Direct API key passing to service constructors

### Usage Example

```python
from vyom.llm_service import create_llm_service

# Create LLM service (defaults to Together AI)
llm_service = create_llm_service()

# Generate visualization
result = llm_service.generate_visualization(
    prompt="Show me the class hierarchy of the project",
    data_context={"classes": [...]}
)
```

## Getting Started

1. Install dependencies:
   ```