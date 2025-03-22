# Migration Guide: Vyom Visualization Update

This guide helps you migrate from the previous version of Vyom to the new version with enhanced visualization capabilities.

## What's New

- **Natural Language Visualization**: Generate visualizations by describing what you want in English
- **Interactive Web Interface**: Use a browser-based interface for visualization
- **Enhanced View Command**: Customize visualizations with natural language prompts
- **LLM Integration**: AI-powered visualization generation

## Upgrading

1. Update your installation:

```bash
# Pull the latest code
git pull

# Install updated dependencies
pip install -r requirements.txt
```

2. Set up API keys for LLM features:

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

## Command Changes

The existing commands continue to work as before, with these additions:

- `vyom view` now accepts `--prompt` and `--use-llm/--no-llm` options
- New command: `vyom generate` for creating visualizations from text descriptions
- New command: `vyom web` for starting the browser-based visualization interface

## Backward Compatibility

All existing functionality continues to work as before. The enhanced visualization features are opt-in through new command-line options.

## Troubleshooting

If you encounter issues with LLM-based features:

1. Ensure your API keys are correctly set in the `.env` file
2. Try using the `--no-llm` flag to fall back to rule-based visualization
3. Check the log output for specific error messages 