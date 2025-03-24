import base64
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types

# Load environment variables
load_dotenv()

def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    files = [
        # Make the file available in local system working directory
        client.files.upload(file="../Resources/SAPHIRE/event_trees.json"),
    ]
    model = "gemini-2.0-pro-exp-02-05"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(
                    file_uri=files[0].uri,
                    mime_type=files[0].mime_type,
                ),
                types.Part.from_text(text="""Mermaid code for this json file"""),
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=64,
        max_output_tokens=8192,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""You are a code generator that translates JSON data representing event trees into Mermaid flowchart code. Your goal is to create a visually accurate and syntactically correct Mermaid diagram that represents the event tree structure and information contained in the JSON.

**Input:**

The input will be a JSON file with the following structure (this is a *generalized* structure based on your example; specifics may vary slightly):

```json
{
  \"job_id\": \"...\",
  \"files\": { ... },
  \"metadata\": { ... },
  \"saphire_data\": {
    \"fault_trees\": [],
    \"event_trees\": [
      {
        \"id\": \"EVENT_TREE_ID\",
        \"name\": \"Event Tree Name\",
        \"top_events\": [
          { \"id\": \"TOP_EVENT_ID\", \"description\": \"Top Event Description\" },
          ...
        ],
        \"sequences\": [
          {
            \"id\": \"SEQUENCE_ID\",
            \"end_state\": \"END_STATE_VALUE\",
            \"end_state_name\": \"END_STATE_NAME\", //optional
            \"path\": []  // You will *not* be provided with the explicit path; you must infer it.
          },
          ...
        ],
        \"node_descriptions\": {
          \"NODE_ID\": \"Node Description\",
          ...
        },
        \"node_substitutions\": {
          \"NODE_ID\": {
            \"original\": \"ORIGINAL_TEXT\",
            \"substitute\": \"SUBSTITUTE_TEXT\"
          },
          ...
        }
      },
      ...  // More event trees might be present
    ],
    \"basic_events\": [], //Not needed
    \"end_states\": [
      {
        \"id\": \"END_STATE_ID\",
        \"name\": \"End State Name\",
        \"description\": \"End State Description\"
      },
      ...
    ],
     \"sequences\": [], //Not needed
    \"project\": { ... } //Not needed
  }
}

```

**Key Data Elements and Their Meanings:**

*   **`event_trees`**:  An array of event tree objects. Each object describes a single event tree.
*   **`id`**:  A unique identifier for the event tree (e.g., \"ATWS\").
*   **`name`**:  The name of the event tree (e.g., \"ATWS\").
*   **`top_events`**:  An array of objects, each representing a header/top event in the event tree diagram (the blue boxes across the top in your original image).
*   **`sequences`**:  An array of objects, each representing a *final outcome* or end state of the event tree.  *Crucially, you will NOT be given the explicit `path` for each sequence.  You must infer the branching logic from the `node_substitutions` and other clues.*  The `\"id\"` is typically the label on the right side of the diagram (e.g., \"RS-AA\"). `\"end_state\"` and `\"end_state_name\"` give more information of the end state.
*   **`node_descriptions`**:  A dictionary that maps node IDs (integers as strings, e.g., \"11\") to their corresponding descriptions.  These descriptions are crucial for building the diagram.
*   **`node_substitutions`**:  A dictionary that handles branching logic.  It indicates how decision nodes in the event tree are connected.  For example:
    ```json
    \"node_substitutions\": {
      \"11\": {
        \"original\": \"NO-OF-MODULES\",
        \"substitute\": \"ATWS-NO-MODULES-124-1\"
      }
    }
    ```
    This means that at node \"11\", if the condition represented by \"NO-OF-MODULES\" is true/false (you'll need to determine this), the flow goes to the logic represented by \"ATWS-NO-MODULES-124-1\".  *This is how you'll build the branching structure*.  There might not always be an obvious \"Yes/No\" relationship; you'll need to infer the branching based on the sequence of substitutions.
*    **`end_states`**: List of possible end states of event tree, with name and description.

**Output:**

The output should be a single, valid Mermaid code block representing the event tree(s).  The code should follow these rules:

1.  **`graph TD`**:  Start with `graph TD` to indicate a top-down flowchart.
2.  **Subgraphs:** Enclose each event tree within a `subgraph EVENT_TREE_ID`.  Use the `id` from the JSON.
3.  **Node Definitions:**
    *   Define each node *once*, with a unique ID.  Use descriptive IDs (e.g., `A`, `B`, `Q11`, etc.).  Don't repeat node definitions.
    *   Define the node ID *first*, then its label on a *separate* line.
        ```mermaid
        NODE_ID;
        NODE_ID[\"Node Label <br> (Optional Extra Info)\"]
        ```
    *   Use `[...]` for rectangular nodes (most nodes).
    *   Use `{...}` for diamond nodes (decision points, typically associated with `top_events`).
    *   Enclose *all* node labels in *double quotes* to handle special characters correctly.  Use `<br>` for line breaks within labels.
4.  **Connections:**
    *   Use `-->` for connections.
    *   Label decision branches with `-- Yes -->` and `-- No -->` where appropriate.  If the \"Yes/No\" relationship isn't clear, you may omit these labels, or infer them from the `top_events` and `node_substitutions`.
5.  **Node Substitutions:** Process the `node_substitutions` carefully to determine the branching logic. This is the most critical and complex part. Create normal connections between original and substituted nodes.
6.  **Top Events:**  Represent the `top_events` as a series of connected decision nodes (diamonds) at the top of the diagram.
7. **End States:** Show end state with their names inside node description.

**Example (Partial - for ATWS, illustrating the core concepts):**

```mermaid
graph TD
    subgraph ATWS
        A[ANTICIPATED TRANSIENT <br> OCCURS] --> B{TRIP-CR};
        B -- Yes --> C[OK];
        B -- No --> D{TRIP-RSCE};
        D -- Yes --> E{OP-TRIP};
        D -- No --> Q19;
        Q19[\"1 MODULE <br> (ATWS-NO-MODULES-14)\"]

        E -- Yes --> F{HTS-FAILURE};
        E -- No --> Q11;
        Q11[\"1 MODULE <br> (ATWS-NO-MODULES-124-1)\"]

        ... (Rest of the event tree) ...
    end
```

**Constraints and Important Considerations:**

*   **No Hardcoding:** Do *not* hardcode any specific node IDs, labels, or connections based on prior knowledge.  Always derive the structure *solely* from the provided JSON.
*   **Error Handling:**  While you don't need to implement explicit error handling for invalid JSON, your code should be robust enough to handle variations in the input (e.g., missing `node_descriptions`, different numbers of `top_events`, etc.) without crashing.  If you encounter something unexpected, make a reasonable assumption and continue.
*   **Readability:** Generate clean, well-formatted Mermaid code that is easy to read and understand.  Use consistent indentation and spacing.
*   **Completeness:** Generate the *complete* Mermaid code for all event trees present in the JSON, each within its own subgraph.
*   **Inference:** You will need to *infer* the branching logic (the \"path\" of each sequence) by carefully examining the `node_substitutions` and the order of events. This is the core challenge. There is no direct \"path\" array in the input."""),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    # generate()
    # Just print response.json in case of API error.
    with open("response.json", "r") as f:
        print(f.read())
