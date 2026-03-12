# LLM-Powered Prompt Router

An intelligent routing service that uses a "Classify, then Respond" pattern to direct user queries to specialized AI personas.

## Setup Instructions

1. **Clone the repository.**
2. **Set up Environment Variables:**
   - Copy `.env.example` to a new file named `.env`.
   - Add your Gemini API key to `.env` (`GEMINI_API_KEY=AIzaSy...`).
3. **Run the Script:**
   Install the requirements and run the router script:
   ```bash
   pip install -r requirements.txt
   python router.py
   ```

## Design Overview
* **Classification**: Uses a fast, cheap LLM call (gemini-2.5-flash) to classify the user's intent into code, data, writing, career, or unclear utilizing JSON mode.
* **Routing**: Maps the classified intent to an expert system prompt in `prompts.json`.
* **Generation**: Makes a second LLM call (gemini-2.5-flash) to generate the actual response based on the expert persona. If the intent is unclear, it safely asks for clarification without a second API call.
* **Logging**: Outputs everything to a local `route_log.jsonl` file.
