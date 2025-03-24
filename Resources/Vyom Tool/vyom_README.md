# Vyom

Nuclear LMP Safety Case Acceleration using PRA

## Overview

Vyom is a tool for processing SAPHIRE probabilistic risk assessment (PRA) models and converting them to the OpenPRA intermediate representation format. It provides robust capabilities for extracting, analyzing, and converting SAPHIRE PRA data, with full support for SAPHIRE file formats and structures.

## Installation

```bash
pip install vyom
```

## Usage

Vyom provides a user-friendly command-line interface (CLI) with the following commands:

### Basic Commands

```bash
vyom import <zip_file>                          # Import SAPHIRE ZIP file
vyom list                                       # List all jobs
vyom explore <job_id> [--export] [--output=<file>] # Explore data, optionally export
vyom convert <job_id> [--output=<file>]         # Convert to OpenPRA format
vyom convert-file <input_file> [--output=<file>]# Convert a SAPHIRE JSON file directly
vyom view <job_id>                              # Visualize in browser
```

### Exploring and Exporting Data

The `explore` command provides a comprehensive interface for viewing and analyzing SAPHIRE data:

```bash
vyom explore <job_id>                      # Show job details and data
vyom explore <job_id> --export             # Export job data
vyom explore <job_id> --export -o data.json # Export with custom filename
```

The explore command supports various options:
- `--export` or `-e`: Export the raw job data
- `--output` or `-o`: Specify output file/directory path
- `--pretty/--compact`: Control JSON formatting
- `--format`: Specify output format (default: json)
- `--query`: Filter data using JSONPath queries

You can use `-` or `last` as shorthand for the most recent job ID.

### Command Aliases

For convenience, single-letter aliases are available for all commands:

```bash
vyom i <zip_file>       # Same as 'import'
vyom l                  # Same as 'list'
vyom e <job_id>         # Same as 'explore'
vyom c <job_id>         # Same as 'convert'
vyom cf <input_file>    # Same as 'convert-file'
vyom v <job_id>         # Same as 'view'
```

For backward compatibility, the following aliases are also available (but will be removed in a future version):
```bash
vyom process <zip_file>  # Same as 'import'
vyom jobs               # Same as 'list'
vyom visualize <job_id> # Same as 'view'
```

### Help and Version Information

```bash
vyom --help    # Show general help
vyom -h        # Short form for help
vyom --version # Show version information
vyom -v        # Short form for version
```

## SAPHIRE Support

Vyom supports a wide range of SAPHIRE file formats, including:

- `.MARD` - Master Relational Database files
- `.BEI` - Basic Event Information files
- `.FTL` - Fault Tree Logic files
- `.ETL` - Event Tree Logic files
- `.FAD` - Project Description files
- And many more

For detailed information on SAPHIRE file processing, see the [SAPHIRE Processing Guide](docs/SAPHIRE_USAGE.md).

### Importing a SAPHIRE ZIP File

```bash
vyom import path/to/saphire.zip
```

This will extract the ZIP file, analyze its contents, and store the results in a local database. The command will return a job ID that you can use for further operations.

### Showing Job Status

```bash
vyom show <job_id>
vyom show last          # Show the most recent job
```

### Exploring Data

```bash
vyom explore <job_id>
vyom explore -          # Explore the most recent job
```

You can also filter the data using JSONPath queries:

```bash
vyom explore <job_id> --query '$.files.*.type'
vyom explore last --query '$.saphire_data.basic_events'
```

### Converting to OpenPRA Format

```bash
vyom convert <job_id> --output openpra_result.json
vyom convert last --format json --pretty
```

### Direct File Conversion

If you have a SAPHIRE JSON file (perhaps from a previous export), you can convert it directly:

```bash
vyom convert-file saphire_data.json --output openpra_result.json
```

### Exporting Raw Data

```bash
vyom export <job_id> --output raw_data.json
vyom export - --compact  # Export most recent job as compact JSON
```

### Visualizing SAPHIRE Data

The visualization feature provides an interactive browser-based view of your SAPHIRE model:

```bash
vyom view <job_id>
vyom view last
```

This command generates an HTML file with a modern, interactive visualization of your SAPHIRE data and opens it in your default web browser. The visualization includes:

- Overview of model components
- Detailed lists of basic events, fault trees, and event trees
- Monaco-based editor for exploring the raw JSON data

You can also generate the visualization without opening the browser:

```bash
vyom view <job_id> --no-browser
```

All visualization files are stored in the `data/visual/` directory with timestamped filenames.

### Listing All Jobs

```bash
vyom list
```

## File Organization

Vyom uses a structured approach to file organization:

- **data/inputs/** - Contains original SAPHIRE ZIP files and other input files that need to be processed.
- **data/examples/** - Contains example and sample files for documentation, testing, and tutorials.
  - **data/examples/schema/** - OpenPRA schema example files
  - **data/examples/saphire/** - SAPHIRE model examples and samples
  - **data/examples/openpra/** - OpenPRA format examples 
- **data/exports/** - Contains exported data files from Vyom processing operations. Files are automatically named with timestamps.
- **data/visual/** - Contains HTML visualizations generated by the view command.

Files follow a consistent naming convention:
```
[project]_[type]_[date/timestamp].[extension]
```

Examples:
- `HTGR_PRA_10162024_Final.zip` (input file)
- `HTGR_PRA_saphire_20240320.json` (example file)
- `HTGR_PRA_openpra_20240319_143022.json` (export with timestamp)
- `saphire_viz_20240319_200507.html` (visualization file)

## Schema Versioning

Vyom implements a comprehensive schema versioning system for OpenPRA:

- Multiple schema versions are supported (1.0.0, 1.1.0, 2.0.0)
- Each schema version has well-defined validation rules
- Automatic schema upgrade functionality
- Schema version information is embedded in exported files

### Schema Versioning Tool

A schema versioning tool is provided to help manage OpenPRA schemas:

```bash
# Show information about available schema versions
python scripts/schema_versioning.py --info

# Validate a file against the schema
python scripts/schema_versioning.py --validate path/to/file.json

# Upgrade a file to a newer schema version
python scripts/schema_versioning.py --upgrade path/to/file.json 2.0.0

# Export a specific schema version template
python scripts/schema_versioning.py --export 1.1.0
```

## Development

To set up the development environment:

```bash
git clone https://github.com/yourusername/vyom.git
cd vyom
pip install -e .
```

## Testing

Vyom includes a comprehensive test suite to verify all functionality:

### Running Tests

To run all tests:

```bash
python run_tests.py
```

Or using pytest directly:

```bash
pytest
```

### Test Categories

- **Unit Tests**: Test individual components (schema validation, database functions)
- **Integration Tests**: Test interaction between components (converter, extractor)
- **Workflow Tests**: Test the full application workflow (import, explore, convert)
- **SAPHIRE Tests**: Test SAPHIRE file parsing and conversion

### Test Files

- `test_db.py`: Tests database functionality
- `test_schema.py`: Tests schema validation
- `test_converter.py`: Tests format conversion
- `test_saphire_extraction.py`: Tests ZIP extraction and file processing
- `test_saphire_parser.py`: Tests SAPHIRE file format parsing
- `test_saphire_to_openpra.py`: Tests SAPHIRE to OpenPRA conversion
- `test_integration.py`: Tests the entire workflow from extraction to conversion
- `test_end_to_end.py`: Tests end-to-end functionality with real data

## Architecture

Vyom is built with a modular architecture focused on simplicity and maintainability:

1. **Database Layer**: Uses DuckDB for efficient local data storage without requiring a separate server
2. **Extraction Engine**: Processes SAPHIRE files from ZIP archives
3. **Schema Definitions**: Clearly defined data structures for both SAPHIRE and OpenPRA formats
4. **Parsing Layer**: Specialized parsers for various SAPHIRE file formats (.BEI, .FTL, .ETL, etc.)
5. **Conversion Layer**: Transforms SAPHIRE data to OpenPRA format
6. **Data Exploration**: Tools for exploring and analyzing the extracted data
7. **CLI Interface**: Simple command-line interface for all operations

## Documentation

- [SAPHIRE Processing Guide](docs/SAPHIRE_USAGE.md) - Detailed guide for working with SAPHIRE files
- Command-specific help - Available via `vyom <command> --help`
- Schema documentation - Available in the `schema` directory

## License

MIT 

## New Visualization Features

Vyom now includes enhanced visualization capabilities using AI, all integrated within the `view` command:

### Natural Language Visualization Generation

Generate visualizations by describing what you want in plain English:

```bash
# Generate visualization from text description
vyom view --prompt "Create a fault tree showing power system failure modes"

# Use existing data to generate visualization
vyom view --data-file data/examples/saphire/sample.json --prompt "Visualize critical failure paths"
```

### Interactive Web Interface

Use the web interface for interactive visualization generation:

```bash
# Start the web server
vyom view --web

# Specify port and LLM service
vyom view --web --port 8080 --llm-service together
```

### Enhanced View Command Options

The view command now supports multiple modes:

```bash
# View a job with enhanced visualization
vyom view <job_id> --prompt "Focus on high-risk components"

# View with custom data file and output location
vyom view --data-file my_data.json --output my_visualization.html

# Test with LLM explicitly enabled/disabled
vyom view <job_id> --use-llm
vyom view <job_id> --no-llm
```

### API Key Setup

To use LLM features, set up API keys:

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

Or run the setup script:

```bash
python -m vyom.setup_api_keys
``` 

## Cost Tracking Functionality

### Overview

This document provides recommendations for implementing LLM cost tracking in vyom. The goal is to provide transparent reporting of model usage, token counts, and associated costs for all LLM operations.

### Implementation Recommendations

#### 1. Create a Cost Tracker Module

Create a dedicated `cost_tracker.py` module in the vyom directory:

```python
# vyom/cost_tracker.py
import tiktoken
from typing import Dict, Optional
from datetime import datetime

class CostTracker:
    """Tracks token usage and costs for LLM operations"""
    
    def __init__(self, model_name: str, encoding_name: str = "cl100k_base"):
        self.model_name = model_name
        self.encoding = tiktoken.get_encoding(encoding_name)
        self.session_start = datetime.now()
        self.calls = []
        self.total_tokens = {"input": 0, "output": 0}
        self.total_cost = 0.0
        self.last_call_info = None
        self.operation_stats = {}
        
        # Cost per 1K tokens (in USD)
        self.COST_PER_1K = {
            "mistralai/Mixtral-8x7B-Instruct-v0.1": {"input": 0.0006, "output": 0.0006},
            "llama3:latest": {"input": 0.0005, "output": 0.0005},
            "meta-llama/Llama-2-70b-chat": {"input": 0.0009, "output": 0.0009}
            # Add more models as needed
        }
    
    def log_call(self, operation: str, prompt: str, response: str) -> Dict:
        """Log a single LLM call and return usage stats"""
        input_tokens = len(self.encoding.encode(prompt))
        output_tokens = len(self.encoding.encode(response))
        
        # Calculate cost
        model_cost = self.COST_PER_1K.get(self.model_name, {"input": 0.001, "output": 0.001})
        cost = ((input_tokens * model_cost["input"] + 
                output_tokens * model_cost["output"]) / 1000)
        
        # Update totals
        self.total_tokens["input"] += input_tokens
        self.total_tokens["output"] += output_tokens
        self.total_cost += cost
        
        # Update operation-specific stats
        if operation not in self.operation_stats:
            self.operation_stats[operation] = {
                "count": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0
            }
        
        self.operation_stats[operation]["count"] += 1
        self.operation_stats[operation]["input_tokens"] += input_tokens
        self.operation_stats[operation]["output_tokens"] += output_tokens
        self.operation_stats[operation]["cost"] += cost
        
        # Store call details
        call_info = {
            "timestamp": datetime.now(),
            "operation": operation,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }
        self.calls.append(call_info)
        self.last_call_info = call_info
        
        return call_info
    
    def get_call_stats_message(self, call_info: Dict) -> str:
        """Get a formatted message with call statistics for user display"""
        return (
            f"Model: {self.model_name}\n"
            f"Input tokens: {call_info['input_tokens']}\n"
            f"Output tokens: {call_info['output_tokens']}\n"
            f"Cost: ${call_info['cost']:.6f}\n"
            f"Session total: ${self.total_cost:.6f}"
        )
    
    def get_session_summary(self) -> Dict:
        """Get summary of all usage in this session"""
        return {
            "session_start": self.session_start,
            "session_duration": datetime.now() - self.session_start,
            "total_calls": len(self.calls),
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "operation_stats": self.operation_stats,
            "calls": self.calls
        }
```

#### 2. Modify LLM Service Classes

Update the LLM service classes (`TogetherAIService` and `BraveAPIService`) to incorporate cost tracking:

```python
# Modification to llm_service.py classes

def __init__(self, api_key: Optional[str] = None):
    # Existing initialization code...
    
    # Add cost tracker with appropriate model name
    self.cost_tracker = CostTracker(self.model)
    
def generate_visualization(self, prompt: str, data_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    # Existing code to prepare prompt...
    
    try:
        # Make API request to Together AI
        # ... existing request code ...
        
        response.raise_for_status()
        result = response.json()
        
        # Extract the generated text
        generated_text = result.get("choices", [{}])[0].get("text", "")
        
        # Log the token usage and cost
        operation = "generate_visualization"
        call_info = self.cost_tracker.log_call(operation, self._format_together_prompt(messages), generated_text)
        
        # Add usage information to the result
        usage_info = {
            "model": self.model,
            "input_tokens": call_info["input_tokens"],
            "output_tokens": call_info["output_tokens"],
            "cost": call_info["cost"],
            "total_cost": self.cost_tracker.total_cost
        }
        
        # Continue with parsing the response...
        visualization_data = { 
            # ... existing visualization data ...
        }
        
        # Add usage information to the result
        visualization_data["usage"] = usage_info
        
        return visualization_data
```

#### 3. Add User-Facing Cost Display

Modify the CLI and viewer components to display cost information:

```python
# In cli.py or viewer.py where visualization results are processed

def display_visualization_result(result):
    # Display the visualization...
    
    # If usage information is available, display it
    if "usage" in result:
        usage = result["usage"]
        print("\nLLM Usage:")
        print(f"→ Model: {usage['model']}")
        print(f"→ Input tokens: {usage['input_tokens']}")
        print(f"→ Output tokens: {usage['output_tokens']}")
        print(f"→ Cost: ${usage['cost']:.6f}")
        print(f"→ Session total: ${usage['total_cost']:.6f}")
```

#### 4. Add Configuration for Cost Tracking

Allow users to enable/disable cost tracking with environment variables or configuration settings:

```python
# In .env or configuration file
VYOM_COST_TRACKING=1  # 1 to enable, 0 to disable
VYOM_COST_DISPLAY=1   # 1 to display costs to user, 0 to only track internally
```

#### 5. Add Requirements

Update the requirements.txt file to include the tiktoken package:

```
tiktoken>=0.5.0
```

### Benefits of This Approach

1. **Transparency**: Users are informed of costs for each LLM operation
2. **Tracking**: Session costs are tracked for budget management
3. **Modularity**: Cost tracking is contained in a dedicated module
4. **Extensibility**: Easy to add support for new models and pricing
5. **Minimal Overhead**: Efficient token counting with tiktoken

### Implementation Strategy`

1. Start with a basic implementation that tracks and displays costs
2. Add support for logging costs to file for persistent tracking
3. Add a dashboard or summary command to view cost history
4. Consider implementing cost limits/budgets for controlled usage

By implementing this cost tracking solution, vyom will provide transparency around model usage and associated costs, helping users make informed decisions about their LLM usage. 