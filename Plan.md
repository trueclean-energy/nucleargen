
Simple Plan

Input SAPHIRE Schemas

0) I will generate more examples from SAPHIRE (Domain)
 - Common Tool - https://thrumming-haze-5713.fly.dev/

1) Agent 1 - Schema Converstion (Tushin)

As a PRA analyst with a non-OpenPRA model, I want to understand the domain better and be ready to move to the next stage of nuclear licensing.

Build - Simple schema analyzer that identifies key SAPHIRE components
Ability to answer 5-10 predefined questions about schema conversion
- Understand about relationships in the schema
- Get more examples or context on a techincal element such as a basic event example
- Understand more about the metrics in example files that adhere to the non OpenPRA schema model

Must expose a sendRequest() function to communicate with other agents

2) Agent 2 - Schema Validation (Noah)

As a PRA analyst, I want a clear summary of validation issues in my model, so I can understand what needs to be fixed. 3-5 validation rules focusing on naming conventions and references
- Explanation of each issue with example fixes
- Ability to export the validation report
- Summary statistics of model completeness
Examples
Detection of inconsistent naming conventions for the same components
Detection of event trees with physically implausible success paths (like DHR after failed SCRAM)
https://www.google.com/url?q=https://docs.google.com/spreadsheets/d/1LoMjJOOmrOjQAZlhDLOyP94MHxZV0xxDzs2LTuO4ooM/edit?gid%3D764428722%23gid%3D764428722&sa=D&source=docs&ust=1742672846100968&usg=AOvVaw1wpNvTPhqQI77_RK2_N5Ov 

Must expose a validateComponent() function for other agents

3) Agent 3 - Schema Visualization (Bobber)
   
"Show me the event tree for loss of forced cooling"
   - Agent renders SVG diagram of the event tree with proper branching
   
"Highlight high-risk paths in this fault tree"
   - Agent color-codes paths based on risk significance

## Expected Demo Outputs
- SVG diagrams of event trees with proper formatting and labels
- Fault tree visualizations with component relationships
- Ability to modify visualizations through conversation (Maybe)

Must expose a visualizeComponent() function




Demo Flow:
User interacts with Agent_1 UI for schema assistance
Agent_1 sends a message to central hub
Hub visualizes the message and routes it to data-validation agent
data-validation processes request and sends results back via hub
Hub visualizes this flow and includes links to open each agent's UI to see results