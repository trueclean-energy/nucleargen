# Requirement
   
"Show me the event tree for loss of forced cooling"
   - Agent renders SVG diagram of the event tree with proper branching
   - For schema, refer to [../Resources/SAPHIRE/event_trees.json](../Resources/SAPHIRE/event_trees.json) and [../Resources/SAPHIRE/saphire_schema20march.json](../Resources/SAPHIRE/saphire_schema20march.json)
   - For sample image, refer to [../Resources/SAPHIRE/Event_Tree1.png](../Resources/SAPHIRE/Event_Tree1.png)
   
"Highlight high-risk paths in this fault tree"
   - Agent color-codes paths based on risk significance
   - Refer to [../Resources/SAPHIRE/basic_events.json](../Resources/SAPHIRE/basic_events.json) and [../Resources/SAPHIRE/saphire_schema20march.json](../Resources/SAPHIRE/saphire_schema20march.json)
   - For sample images, refer to [../Resources/SAPHIRE/Fault_Tree1.png](../Resources/SAPHIRE/Fault_Tree1.png) and [../Resources/SAPHIRE/Fault_Tree2.png](../Resources/SAPHIRE/Fault_Tree2.png)

# Data structure
[../Resources/SAPHIRE/basic_events.json](../Resources/SAPHIRE/basic_events.json) and [../Resources/SAPHIRE/event_trees.json](../Resources/SAPHIRE/event_trees.json) are subsets of [../Resources/SAPHIRE/saphire_schema20march.json](../Resources/SAPHIRE/saphire_schema20march.json)

# High level design
Use Gemini 2 Flash model.

## Event tree prompt



