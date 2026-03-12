import pytest
import os
import json
from router import classify_intent, route_and_respond, check_manual_override

# --- Manual Override Tests ---
def test_manual_override_valid():
    override = check_manual_override("@code Help me with this function")
    assert override is not None
    assert override["intent"] == "code"
    assert override["confidence"] == 1.0
    assert override["cleaned_message"] == "Help me with this function"

def test_manual_override_invalid_persona():
    override = check_manual_override("@invalidpersona Help me")
    assert override is None

def test_manual_override_no_tag():
    override = check_manual_override("Help me with this function")
    assert override is None

# --- Routing Tests ---
def test_unclear_routing():
    response = route_and_respond("Can you write a poem?", {"intent": "unclear", "confidence": 0.0})
    assert "Are you asking for help with coding, data analysis, writing, or career advice?" in response

# --- Classification Tests (Mocking API) ---
class MockResponse:
    def __init__(self, text):
        self.text = text

class MockModel:
    def __init__(self, mock_response_text):
        self.mock_response_text = mock_response_text
        
    def generate_content(self, prompt):
        return MockResponse(self.mock_response_text)

def test_classify_intent_malformed_json(monkeypatch):
    """Test what happens if the LLM returns invalid JSON string"""
    import google.generativeai as genai
    
    def mock_generative_model(*args, **kwargs):
        return MockModel("```json\n{malformed: 'json'}```")
        
    monkeypatch.setattr(genai, "GenerativeModel", mock_generative_model)
    
    result = classify_intent("This is a test message that will get malformed json back")
    assert result["intent"] == "unclear"
    assert result["confidence"] == 0.0

def test_classify_intent_missing_keys(monkeypatch):
    """Test what happens if the LLM returns valid JSON but missing keys"""
    import google.generativeai as genai
    
    def mock_generative_model(*args, **kwargs):
        return MockModel('{"wrong_key": "data"}')
        
    monkeypatch.setattr(genai, "GenerativeModel", mock_generative_model)
    
    result = classify_intent("This message will get missing keys back")
    assert result["intent"] == "unclear"
    assert result["confidence"] == 0.0

# --- Exception Handling Tests ---
def test_classify_intent_api_error(monkeypatch):
    """Test handling of Google API Errors"""
    import google.generativeai as genai
    
    class MockAPIError(Exception):
        pass
    # We simulate a class name check like in router.py
    MockAPIError.__module__ = "google.api_core.exceptions"

    def mock_generative_model(*args, **kwargs):
        raise MockAPIError("API Access Blocked")
        
    monkeypatch.setattr(genai, "GenerativeModel", mock_generative_model)
    
    result = classify_intent("Trigger API error")
    assert result["intent"] == "unclear"
    assert result["confidence"] == 0.0
