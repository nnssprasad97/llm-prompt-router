import os
import json
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize Gemini Client
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Load prompts
with open("prompts.json", "r") as f:
    PROMPTS = json.load(f)

LOG_FILE = "route_log.jsonl"

def classify_intent(message: str) -> dict:
    """Classifies the user's intent and returns a JSON object."""
    classifier_prompt = """
    Your task is to classify the user's intent. Based on the user message below, 
    choose one of the following labels: code, data, writing, career, math, unclear. 
    Respond with a single JSON object containing two keys: 
    'intent' (the label you chose) and 'confidence' (a float from 0.0 to 1.0). 
    Do not provide any other text or explanation.
    """
    
    try:
        # Prompt routing with fast model
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config={"response_mime_type": "application/json", "temperature": 0.0}
        )
        
        prompt = f"{classifier_prompt}\n\nUser Message: {message}"
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        result = json.loads(response.text)
        
        # Validate keys exist
        if "intent" not in result or "confidence" not in result:
            raise ValueError("Missing keys in JSON")
            
        # Optional: Implement a confidence threshold
        if result["confidence"] < 0.7:
            return {"intent": "unclear", "confidence": result["confidence"]}
            
        return result

    except json.JSONDecodeError as e:
        print(f"Classification JSON Error: {e}")
        return {"intent": "unclear", "confidence": 0.0}
    except ValueError as e:
        print(f"Classification Value Error (missing keys): {e}")
        return {"intent": "unclear", "confidence": 0.0}
    except genai.types.generation_types.StopCandidateException as e:
        print(f"Classification Generation Error: {e}")
        return {"intent": "unclear", "confidence": 0.0}
    except Exception as e:
        # Check for Google API specific errors without rigid type checking if possible, 
        # or catch common ones like API key issues.
        if "google.api_core.exceptions" in str(type(e)):
            print(f"Classification API Error: {e}")
            return {"intent": "unclear", "confidence": 0.0}
        # Re-raise unexpected structural/logic errors
        raise 

def route_and_respond(message: str, intent_data: dict) -> str:
    """Routes the request to the proper expert or asks for clarification."""
    intent = intent_data.get("intent", "unclear")
    
    # Handle 'unclear' intent without making a second LLM call (Core Requirement 4)
    if intent == "unclear" or intent not in PROMPTS:
        return "I'm not quite sure how to help with that. Are you asking for help with coding, data analysis, writing, or career advice?"

    # Second LLM Call for the actual generation
    system_prompt = PROMPTS[intent]
    
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        system_instruction=system_prompt,
        generation_config={"temperature": 0.7}
    )
    
    response = model.generate_content(message)
    
    return response.text

def log_interaction(intent: str, confidence: float, user_message: str, final_response: str):
    """Appends the interaction to a JSON Lines log file."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "intent": intent,
        "confidence": confidence,
        "user_message": user_message,
        "final_response": final_response
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def check_manual_override(message: str) -> dict:
    """
    Checks if the user has provided a manual intent override (e.g., '@code fix this').
    Returns a dictionary with the intent and the cleaned message, or None if no override.
    """
    valid_intents = list(PROMPTS.keys()) # ['code', 'data', 'writing', 'career', 'math']
    
    # Check if the message starts with an '@' tag
    if message.startswith("@"):
        parts = message.split(" ", 1)
        potential_intent = parts[0][1:].lower() # Extract the word after '@'
        
        if potential_intent in valid_intents:
            cleaned_message = parts[1] if len(parts) > 1 else ""
            return {
                "intent": potential_intent,
                "confidence": 1.0,
                "cleaned_message": cleaned_message
            }
    return None

def process_message(message: str) -> str:
    """Main orchestration function handling overrides, classification, and routing."""
    
    # 1. Check for Manual Override
    override = check_manual_override(message)
    
    if override:
        intent_data = {"intent": override["intent"], "confidence": override["confidence"]}
        message_to_process = override["cleaned_message"]
        print(f"[Router Logs] Manual Override Detected: {intent_data['intent']}")
    else:
        # 2. Standard Classification
        intent_data = classify_intent(message)
        message_to_process = message
        print(f"[Router Logs] Detected Intent: {intent_data['intent']} (Confidence: {intent_data['confidence']})")
    
    # 3. Route and Respond
    final_response = route_and_respond(message_to_process, intent_data)
    
    # 4. Log the interaction (always log the original raw message)
    log_interaction(
        intent=intent_data["intent"],
        confidence=intent_data["confidence"],
        user_message=message,
        final_response=final_response
    )
    
    return final_response

def interactive_cli():
    """Runs a continuous interactive loop for the user."""
    print("="*50)
    print("🤖 Welcome to the LLM Prompt Router!")
    print("Available personas: code, data, writing, career, math")
    print("Tip: Use '@[persona]' to force a route (e.g., '@code write a python loop')")
    print("Type 'exit' or 'quit' to stop.")
    print("="*50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
                
            response = process_message(user_input)
            print(f"\nAssistant:\n{response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[Error]: Something went wrong: {e}")

# --- Execution Block ---
if __name__ == "__main__":
    test_messages = [
        "how do i sort a list of objects in python?",
        "explain this sql query for me",
        "This paragraph sounds awkward, can you help me fix it?",
        "I'm preparing for a job interview, any tips?",
        "what's the average of these numbers: 12, 45, 23, 67, 34",
        "Help me make this better.",
        "I need to write a function that takes a user id and returns their profile, but also i need help with my resume.",
        "hey",
        "Can you write me a poem about clouds?", # Should trigger unclear
        "Rewrite this sentence to be more professional.",
        "I'm not sure what to do with my career.",
        "what is a pivot table",
        "fxi thsi bug pls: for i in range(10) print(i)",
        "How do I structure a cover letter?",
        "My boss says my writing is too verbose."
    ]

    # To run test messages uncomment the following loop:
    # for msg in test_messages:
    #    process_message(msg)
    
    # Start the interactive CLI
    interactive_cli()
