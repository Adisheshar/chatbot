from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import requests
from twilio.twiml.voice_response import VoiceResponse

app = FastAPI()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class IVRRequest(BaseModel):
    digit: str
    call_sid: str

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/ivr")
async def handle_ivr_input(data: IVRRequest):
    if data.digit == "1":
        user_query = "What's the weather update for Bangalore?"
        language = "en-GB"
    elif data.digit == "2":
        user_query = "ಬೆಂಗಳೂರು ನಗರಕ್ಕೆ ಹವಾಮಾನವನ್ನು ಹೇಳಿ"
        language = "kn-IN"
    else:
        raise HTTPException(status_code=400, detail="Invalid input")

    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": user_query}]
    }

    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }

    groq_response = requests.post(GROQ_API_URL, json=payload, headers=headers)

    if groq_response.status_code != 200:
        raise HTTPException(status_code=groq_response.status_code, detail="Error from Groq API")

    chatbot_text = groq_response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    if not chatbot_text:
        chatbot_text = "Sorry, I couldn't get a proper response. Please try again."

    return Response(content=str(generate_twiml_response(chatbot_text, language)), media_type="application/xml")

def generate_twiml_response(chatbot_text, language):
    response = VoiceResponse()
    response.say(chatbot_text, voice='alice', language=language)
    return response
