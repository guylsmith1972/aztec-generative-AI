# Medieval Craftable Object Discovery System

This project is a Python-based system designed to automatically discover and define craftable objects within a simulated medieval European economy, primarily for game development or world-building purposes. It leverages Large Language Models (LLMs) like Oobabooga's text-generation-webui (with models like Falcon) or OpenAI's API to generate detailed descriptions, components, tools needed, variants, and related objects. The system iteratively expands its knowledge base by identifying undefined object references within already defined objects.

## Core Functionality

*   **AI-Driven Object Definition**: Uses LLMs to generate JSON data for craftable objects based on a name and description.
*   **Iterative Discovery**: Scans defined objects for references to other tools, components, or related items that are not yet defined, and queues them for discovery.
*   **Object Validation**: Validates generated object data against a JSON schema (`object_definition.json`) to ensure consistency and correctness.
*   **Medieval Contextualization**: AI prompts are designed to ensure generated objects are plausible within a medieval European setting.
*   **Data Persistence**: Stores the discovered economy (objects, banned items) in `economy.json`.
*   **Extensible AI Providers**: Supports Oobabooga (default), OpenAI, and includes stubs for Hugging Face API.

## System Architecture & Key Components

The system is composed of several Python scripts and data files:

*   **`main.py`**: The main entry point to run the discovery process. It initializes the economy and orchestrates the `researcher`.
*   **`economy.py`**: Manages the `economy.json` data file. Handles loading, saving, adding new objects, banning objects, and identifying undefined objects for further research.
*   **`craftable_object.py`**: Contains the core logic for interacting with the AI to generate, correct, and validate individual craftable object definitions.
    *   It uses functions like `is_object_acceptable` to filter out anachronistic items.
    *   `get_object_request_query` orchestrates the generation of a full object definition via AI.
    *   `extract_object_references` pulls out names of other objects mentioned in an object's definition, which fuels the discovery process.
*   **`researcher.py`**: Implements the object discovery loop. It takes the current economy, identifies undefined objects, and uses `craftable_object.py` to query the AI for their definitions.
*   **AI API Wrappers**:
    *   **`oobabooga_api.py`**: Interface for Oobabooga's text-generation-webui API (default).
    *   **`openai_api.py`**: Interface for OpenAI's API (e.g., GPT-3.5-turbo, GPT-4).
    *   **`huggingface_api.py`**: (Stub) Interface for Hugging Face Inference API.
    *   **`run_locally.py`**: (Alternative) A script to run a local Hugging Face model (e.g., Falcon) directly using `transformers`. Not directly integrated into `main.py` but provides an alternative local inference method.
*   **`prompt_templates.py`**: Loads and formats text prompts from files in the `prompt_templates/` directory to query the AI.
*   **`schema.py`**: Loads and uses JSON schemata (from the `schemata/` directory) to validate AI-generated object data.
*   **`utility.py`**: Contains utility functions, notably `extract_json` for robustly extracting JSON from AI text responses.

## Data Files

*   **`economy.json`**: The primary data file. Stores all discovered objects and a list of banned object names. This file is continuously updated by the system.
*   **`example_object.json`**: Provides an example of the expected JSON structure for a craftable object. Used by `researcher.py` to guide the AI in its generation process.
*   **`economy_old.json`**: Appears to be an older version of the economy data. The current system uses `economy.json`.
*   **`schemata/object_definition.json`**: The JSON schema that defines the structure and constraints for craftable object JSON data.
*   **`prompt_templates/*.txt`**: Text files containing templates for prompts sent to the LLM. These are crucial for guiding the AI's responses. Examples:
    *   `generate_craftable_object.txt`: Asks the AI to describe an object.
    *   `generate_object_parts.txt`: Asks for components of an assembled object.
    *   `generate_object_materials.txt`: Asks for raw materials for a directly crafted object.
    *   `generate_tools_needed.txt`: Asks for tools to assemble an object.
    *   `get_construction_method.txt`: Determines if an object is assembled or directly crafted.
    *   `confirm_construction_of_a.txt`: Confirms materials for a component part.

## Setup and Installation

1.  **Python Environment**:
    Ensure you have Python 3.8+ installed. It's recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Dependencies**:
    Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
    A `requirements.txt` file would typically look like this (you may need to create it or install packages individually):
    ```
    # requirements.txt
    requests
    jsonschema
    torch
    transformers
    openai
    # Add other specific versions if needed, e.g., sentencepiece for some tokenizers
    ```

3.  **AI Provider Setup**:

    *   **Oobabooga (Default)**:
        *   Download and run Oobabooga's text-generation-webui: [https://github.com/oobabooga/text-generation-webui](https://github.com/oobabooga/text-generation-webui)
        *   Ensure it's running with the API enabled, typically on `http://localhost:5000`. The script expects this default URI.
        *   Load a suitable instruction-tuned model (e.g., a Falcon-instruct model, TheBloke's GPTQ models are good options for local inference).

    *   **OpenAI**:
        *   If you want to use OpenAI, you'll need an API key.
        *   Set the `OPENAI_KEY` environment variable:
            ```bash
            export OPENAI_KEY="your_openai_api_key_here"
            # On Windows (Command Prompt): set OPENAI_KEY=your_openai_api_key_here
            # On Windows (PowerShell): $env:OPENAI_KEY="your_openai_api_key_here"
            ```
        *   You would then modify `main.py` to instantiate `OpenAIAPI` instead of `OobaboogaAPI`.

    *   **Hugging Face API / Local Transformers (`run_locally.py`)**:
        *   For `huggingface_api.py`, set the `HUGGINGFACE_API_KEY` environment variable.
        *   `run_locally.py` uses `transformers` directly and might require significant VRAM depending on the model (`tiiuae/falcon-7b-instruct` is specified). It downloads the model to `models/MODEL_NAME`.

## Running the Application

1.  **Ensure `economy.json` exists**: If it's your first run, you might want to start with an empty or minimal `economy.json` or use the provided one. An empty one should look like:
    ```json
    {
      "banned": [],
      "objects": {}
    }
    ```

2.  **Start your chosen AI provider**:
    *   For Oobabooga, ensure the web UI is running with the API.
    *   For OpenAI, ensure your API key is set.

3.  **Run `main.py`**:
    ```bash
    python main.py
    ```

    The script will:
    *   Load the existing economy from `economy.json`.
    *   Initialize a list of `required_objects` (e.g., "axe", "helmet").
    *   Call `researcher.discover_objects()`.
    *   The researcher will identify undefined objects (initially from `required_objects`, then from references within defined objects).
    *   For each undefined object, it will:
        *   Check if the object is "acceptable" (medieval context) using an AI query.
        *   If acceptable, query the AI to generate its full definition.
        *   Attempt to add the new object to the economy.
        *   The economy is saved to `economy.json` after each successful object discovery (or after a batch, check `main.py` logic).
        *   If rejected, the object name is added to the "banned" list in `economy.json`.
    *   The `main.py` script is set to run the discovery process for a fixed number of iterations (e.g., 4 times).

## How it Works: The Discovery Loop

1.  **Seed Objects**: The `required_objects` dictionary in `main.py` provides the initial seeds.
2.  **Get Undefined Objects**: `economy.get_undefined_objects()` looks at all defined objects in `economy.json`. It extracts all references from fields like "tools needed", "pieces needed" (if component type), "related objects", and "variants". It compiles a list of these referenced objects that are not yet defined in the `economy.json` and are not in the `banned` list.
3.  **Process Candidates**: `researcher.discover_objects()` iterates through these undefined candidate objects.
    *   **Acceptability Check**: `craftable_object.is_object_acceptable()` queries the AI to determine if the candidate object fits the medieval European theme.
    *   **Generation**: If acceptable, `craftable_object.get_object_request_query()` uses a series of prompt templates to ask the AI for:
        *   Basic object details (description, manufacturers, users, type, related, variants).
        *   Construction method (assembled from parts or crafted directly from raw materials).
        *   If assembled: parts needed (and their types: component, location, feature).
        *   If direct: raw materials needed.
        *   If a part is a component: its raw material.
        *   Tools needed for assembly.
    *   **Validation & Addition**: The generated JSON is validated against `schemata/object_definition.json`. If valid and the name matches, it's added to the `economy`.
    *   **Banning**: If an object is deemed unacceptable by the AI, its name is added to the `economy['banned']` list to prevent future processing.
4.  **Iteration**: The `main` script runs this discovery loop multiple times. Each iteration can define new objects, which in turn might introduce more undefined references, leading to further discoveries in subsequent iterations.

## Customization

*   **AI Model**:
    *   In `oobabooga_api.py`, you can adjust generation parameters (temperature, top_p, etc.) for your specific model.
    *   To switch to OpenAI, change `OobaboogaAPI` to `OpenAIAPI` in `main.py`.
*   **Initial Objects**: Modify the `required_objects` dictionary in `main.py` to change the starting set of items to define.
*   **Prompt Templates**: Edit the `.txt` files in `prompt_templates/` to refine how the AI is queried. This is a key area for improving the quality and structure of generated data.
*   **Schema**: Modify `schemata/object_definition.json` if you need to change the structure or validation rules for objects.

## Troubleshooting

*   **Oobabooga API Not Responding**: Ensure Oobabooga's text-generation-webui is running, the API is enabled (usually via command-line flags like `--api`), and the correct model is loaded. Check the `URI` in `oobabooga_api.py`.
*   **OpenAI API Errors**: Check your `OPENAI_KEY` environment variable and ensure you have sufficient credits/quota.
*   **JSONDecodeError**: The AI might produce output that isn't valid JSON or contains extra text. `utility.extract_json` tries to handle this, but complex or malformed AI responses can still cause issues. Improving prompts or AI model choice can help.
*   **Slow Generation**: Local LLMs can be slow. OpenAI API calls can also take time. Be patient.
*   **Poor Quality Generations**:
    *   Experiment with different LLMs. Some are better at structured JSON output or following instructions than others.
    *   Refine the prompt templates in `prompt_templates/`. Clearer instructions and better examples lead to better AI output.
    *   Adjust AI generation parameters (temperature, top_p, etc.). Lower temperature usually means more deterministic, less creative output.

This system provides a powerful framework for procedurally generating rich, interconnected game data. Happy world-building!
