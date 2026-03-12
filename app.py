from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import router # Imports your existing router.py logic

app = FastAPI(title="LLM Prompt Router API")

# Define the request body schema
class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Check for manual override
        override = router.check_manual_override(request.message)
        
        if override:
            intent_data = {"intent": override["intent"], "confidence": override["confidence"]}
            message_to_process = override["cleaned_message"]
        else:
            # 2. Standard Classification
            intent_data = router.classify_intent(request.message)
            message_to_process = request.message
            
        # 3. Route and Respond
        final_response = router.route_and_respond(message_to_process, intent_data)
        
        # 4. Log the interaction
        router.log_interaction(
            intent=intent_data["intent"],
            confidence=intent_data["confidence"],
            user_message=request.message,
            final_response=final_response
        )
        
        # Return the rich response to the frontend
        return {
            "intent": intent_data["intent"],
            "confidence": intent_data["confidence"],
            "response": final_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve the simple HTML UI
@app.get("/", response_class=HTMLResponse)
async def get_ui():
    with open("index.html", "r") as f:
        return f.read()
