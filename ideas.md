I understand you need to develop at least two AI agents for a hackathon challenge that involves building multimodal AI agents capable of advanced reasoning and autonomous decision-making. With only 3 hours to code, we need to focus on agents that can be developed quickly while still making an impact. Based on your notes and the context provided, here are descriptions for three complementary agents:

## 1. PRA Schema Conversion Agent

**Description:** The Schema Conversion Agent analyzes and transforms various PRA model formats into the OpenPRA schema format. It intelligently maps fields from legacy or proprietary formats to the OpenPRA schema, ensuring logical consistency and proper naming conventions. When it encounters issues, it provides clear explanations of problems and suggests fixes. The agent leverages contextual understanding to handle ambiguous mappings and preserves the integrity of the original model's risk assessment capabilities.

**Key Capabilities:**
- Automatic detection of input schema format (SAPHIRE MARD, proprietary formats)
- Field-by-field mapping with confidence scores
- Real-time validation checking for logical consistency issues like the EBR-II examples
- Interactive clarification for ambiguous mappings via chat interface
- Generation of OpenPRA-compliant JSON output

**Demo Flow:** Upload a non-OpenPRA schema → Agent analyzes structure → Agent proposes mappings → User confirms/adjusts key mappings → Agent generates and validates the OpenPRA output.

## 2. PRA Visualization Agent

**Description:** The Visualization Agent transforms complex PRA data into insightful visual representations through a conversational interface. It specializes in creating FC curves, event trees, and fault trees based on the OpenPRA schema. The agent understands natural language requests about visualizing specific scenarios or components and can modify visualizations through conversation. It adapts the visualization style to highlight the most critical risk insights.

**Key Capabilities:**
- Natural language generation of SVG diagrams for event trees and fault trees
- Interactive FC curve creation with customizable risk targets
- Comparison views showing before/after modifications
- Visual highlighting of logical inconsistencies or high-risk areas
- Shareable exports in multiple formats (SVG, PNG)

**Demo Flow:** User requests "Show me an FC curve for sequence X" → Agent creates visualization → User asks to modify parameters → Agent updates in real-time → User requests to export or share the visualization.

## 3. PRA Validation Agent

**Description:** The Validation Agent performs intelligent quality checks on PRA models, identifying logical inconsistencies, naming convention issues, and reference integrity problems. It uses the EBR-II examples as a foundation for its validation rules. The agent categorizes issues by severity and provides specific recommendations for fixes. It understands the context of nuclear safety analysis and can adapt its validation criteria accordingly.

**Key Capabilities:**
- Automated detection of critical logical contradictions (e.g., decay heat removal after failed SCRAM)
- Naming convention consistency checker with auto-correction suggestions
- Data source validation for component failure rates
- Severity classification of identified issues (critical, major, minor)
- Interactive resolution workflow for fixing detected problems

**Demo Flow:** Upload OpenPRA schema → Agent performs comprehensive validation → Agent presents categorized issues → User selects an issue to address → Agent suggests specific fixes → User approves changes.

For the hackathon, I'd recommend focusing on the Schema Conversion Agent and Visualization Agent as your primary two agents, as they provide complementary capabilities that showcase both reasoning (schema mapping) and multimodal output (visualizations). They could be presented as working together - the Conversion Agent prepares the data, and the Visualization Agent helps users understand it through interactive graphics.


## 4. PRA Documentation Generator Agent

**Description:** The Documentation Generator Agent creates comprehensive, professional-grade technical reports directly from PRA models. It analyzes OpenPRA schema data to extract key findings, assumptions, and risk insights, then transforms them into clearly structured documents with executive summaries, detailed analysis sections, and visualization integration. The agent adapts its writing style to match technical documentation standards while making complex PRA concepts accessible to different stakeholders. It can generate targeted reports focusing on specific aspects of the model or produce complete documentation sets.

**Key Capabilities:**
- Automatic extraction of key model parameters, assumptions, and limitations
- Dynamic generation of executive summaries tailored to technical and non-technical audiences
- Integration of visualizations from the Visualization Agent with proper context and analysis
- Traceability matrices linking findings to underlying data sources
- Comparison reports highlighting changes between model versions
- Export options in multiple formats (PDF, Markdown, HTML)

**Demo Flow:** User selects OpenPRA model → User specifies report type and audience → Agent generates structured document outline → Agent populates sections with relevant content and visualizations → User requests specific modifications → Agent delivers final formatted report.

This Documentation Generator Agent complements the Schema Conversion and Visualization agents by providing the crucial narrative layer that explains what the model means, what insights it provides, and what actions should be considered. Together, these three agents create a powerful ecosystem for PRA model management - conversion, visualization, and communication - addressing the full lifecycle of PRA usage.