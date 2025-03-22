
Simple Plan

Input SAPHIRE Schemas

0) I will generate more examples from SAPHIRE (Domain)

1) Agent 1 - Schema Converstion (Tushin)

As a PRA analyst with a non-OpenPRA model, I want to convert my model to OpenPRA format with minimal manual effort.
- Automatic detection of common schema types
- Suggested field mappings between schemas
- Ability to adjust mappings when needed
- Preview of conversion results before finalizing

2) Agent 2 - Schema Validation (Noah)

As a PRA analyst, I want a clear summary of validation issues in my model, so I can understand what needs to be fixed.
- Explanation of each issue with example fixes
- Ability to export the validation report
- Summary statistics of model completeness
Examples
Detection of inconsistent naming conventions for the same components
Detection of event trees with physically implausible success paths (like DHR after failed SCRAM)
https://www.google.com/url?q=https://docs.google.com/spreadsheets/d/1LoMjJOOmrOjQAZlhDLOyP94MHxZV0xxDzs2LTuO4ooM/edit?gid%3D764428722%23gid%3D764428722&sa=D&source=docs&ust=1742672846100968&usg=AOvVaw1wpNvTPhqQI77_RK2_N5Ov 

3) Agent 3 - Schema Visualization (Bobber)
   
"Show me the event tree for loss of forced cooling"
   - Agent renders SVG diagram of the event tree with proper branching
   
"Highlight high-risk paths in this fault tree"
   - Agent color-codes paths based on risk significance

## Expected Demo Outputs
- SVG diagrams of event trees with proper formatting and labels
- Fault tree visualizations with component relationships
- Ability to modify visualizations through conversation (Maybe)





