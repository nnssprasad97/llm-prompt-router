# LLM-Powered Prompt Router

An intelligent routing service that uses a "Classify, then Respond" pattern to direct user queries to specialized AI personas. This project prevents monolithic prompt inefficiency by using a lightweight classifier to delegate tasks to 'expert' personas.

## Features
- **Intelligent Classification**: Detects user intent (code, data, writing, career, math) using Gemini 2.5 Flash.
- **Expert Personas**: Specialized system prompts for high-quality, task-specific responses.
- **Manual Overrides**: Force routing using `@persona` tags (e.g., `@code fix this bug`).
- **Robust Logging**: JSON Lines logging with timestamps, intents, confidence, and full responses.
- **Graceful Error Handling**: Fallbacks for malformed LLM responses or API issues.

## Setup Instructions

### 1. Prerequisite: Python 3.8+
Ensure you have Python installed.

### 2. Set up Environment Variables
1. Copy `.env.example` to a new file named `.env`.
2. Open `.env` and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

### 3. Install Dependencies
It is recommended to use a virtual environment:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## How to Run

### Run the Interactive CLI
Launch the interactive session to chat with the personas:
```bash
python router.py
```

### Run Unit Tests
Verify the system's logic and error handling:
```bash
pytest test_router.py
```

## Design Overview
* **Classification**: Uses `gemini-2.5-flash` with JSON mode for fast, cost-effective intent detection.
* **Routing**: Maps intent labels to system prompts defined in `prompts.json`.
* **Generation**: Generates the final response using the selected expert persona.
* **Observability**: All interactions are logged to `route_log.jsonl` for evaluation.
