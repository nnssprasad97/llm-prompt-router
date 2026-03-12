# LLM-Powered Prompt Router

An intelligent routing service that uses a "Classify, then Respond" pattern to direct user queries to specialized AI personas.

## Setup Instructions

1. **Clone the repository.**
2. **Set up Environment Variables:**
   - Copy `.env.example` to a new file named `.env`.
   - Add your OpenAI API key to `.env` (`OPENAI_API_KEY=sk-...`).
3. **Run with Docker:**
   Ensure Docker and Docker Compose are installed. Run the following command in the project root:
   ```bash
   docker-compose up --build
   ```

## Design Overview
* **Classification**: Uses a fast, cheap LLM call (gpt-3.5-turbo) to classify the user's intent into code, data, writing, career, or unclear utilizing JSON mode.
* **Routing**: Maps the classified intent to an expert system prompt in `prompts.json`.
* **Generation**: Makes a second LLM call (gpt-4-turbo-preview) to generate the actual response based on the expert persona. If the intent is unclear, it safely asks for clarification without a second API call.
* **Logging**: Outputs everything to a local `route_log.jsonl` file.
