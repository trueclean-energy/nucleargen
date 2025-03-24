# OpenPRA Schema

This directory contains a simplified and modular version of the OpenPRA schema, designed to be more manageable for LLM processing while maintaining the essential structure and relationships.

## File Structure

1. `schema-summary.json`: High-level overview of the schema structure, including:
   - Schema purpose
   - Key concepts
   - Main relationships
   - Critical constraints

2. `core-definitions.json`: Core data structures that are fundamental to the schema:
   - Base Event types
   - Component definitions
   - Assumptions
   - Uncertainty information

3. `analysis-definitions.json`: Analysis-specific definitions:
   - Analysis types
   - Atmospheric dispersion analysis
   - Bayesian update process

## Usage

When providing context to an LLM:

1. Start with `schema-summary.json` for high-level understanding
2. Include relevant sections from `core-definitions.json` for basic structure
3. Add specific definitions from `analysis-definitions.json` as needed

## Key Features

- Modular structure for easier context management
- Maintained essential relationships and constraints
- Simplified but complete type definitions
- Consistent UUID-based identification
- Clear required field specifications

## Notes

- All files follow JSON Schema Draft-07
- Each definition includes a UUID field for identification
- Required fields are explicitly specified
- Enums are used for constrained choices 