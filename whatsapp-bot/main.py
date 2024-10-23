# Standard Library Imports 
from dotenv import load_dotenv
import os
from fastapi import FastAPI, Response, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.messaging_response import MessagingResponse

# Utils 
from utils.VertexAi import VertexAi
from utils.TwilioClient import TwilioClient

load_dotenv()

'''
Env variables
'''
## Vertex AI - Model
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION_ID = os.getenv("LOCATION_ID")
AGENT_ID = os.getenv("AGENT_ID")

## Twilio - WhatsApp
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")

'''
Init 
'''
vertex_ai = VertexAi(PROJECT_ID, LOCATION_ID, AGENT_ID)
client = TwilioClient(ACCOUNT_SID, AUTH_TOKEN, WHATSAPP_NUMBER).client
app = FastAPI()

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

'''
Main Endpoints
'''
@app.post("/whatsapp")
async def handle_whatsapp(
    From: str = Form(...),
    Body: str = Form(...),
    NumMedia: int = Form(default=0),
    MediaContentType0: str = Form(default=None),
    MediaUrl0: str = Form(default=None)
):
    """Handle incoming WhatsApp messages"""
    try:

        response = MessagingResponse()

        # Extract the user message (handle media if needed)
        if NumMedia > 0:
            user_msg = f"{Body} (Media received: {MediaContentType0})"
        else:
            user_msg = Body

        # Log the received message
        print(f"Received message from {From}: {user_msg}")

        # Forward the message to Vertex AI and get the response
        bot_response = vertex_ai.get_vertex_response(user_msg)

        # Log the bot's response
        print(f"Bot response: {bot_response}")

        for sentence in bot_response:
            message = response.message()
            message.body(sentence + "\n")

        return Response(content=str(response), media_type="application/xml")

    except Exception as e:
        print(f"Error in webhook: {str(e)}")

        # Handle errors gracefully
        error_response = MessagingResponse()
        error_response.message(
            "I apologize, but I'm having trouble processing your message. Please try again later."
        )
        return Response(content=str(error_response), media_type="application/xml")