# Standard Library Imports 
from fastapi import FastAPI, Response, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.messaging_response import MessagingResponse
import asyncio
from typing import Optional
from functools import partial
import time

# Utils 
from utils.VertexAi import VertexAi
from utils.TwilioClient import TwilioClient
from utils.GeminiClient import GeminiClient
from utils.ImageAnalyzer import ImageProcessor

# Env 
from utils.config import PROJECT_ID, LOCATION_ID, AGENT_ID, ACCOUNT_SID, AUTH_TOKEN, WHATSAPP_NUMBER


'''
Init 
'''
vertex_ai = VertexAi(PROJECT_ID, LOCATION_ID, AGENT_ID)
gemini_client = GeminiClient()
image_analyzer = ImageProcessor()
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

def get_vertex_response_with_retry(user_msg: str, max_retries: int = 3) -> list:
    """Get response from Vertex AI with retry logic"""
    for attempt in range(max_retries):
        try:
            response = vertex_ai.get_vertex_response(user_msg)
            if response:
                return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait 1 second between retries
            else:
                raise
    raise Exception("Failed to get response after all retries")

'''
Main Endpoints
'''
@app.post("/whatsapp")
async def handle_whatsapp(
    From: str = Form(...),
    Body: str = Form(...),
    NumMedia: int = Form(default=0),
    MediaContentType0: Optional[str] = Form(default=None),
    MediaUrl0: Optional[str] = Form(default=None)
):
    """Handle incoming WhatsApp messages with combined text and image processing"""
    try:
        user_msg = Body.strip()
        print(f"Received message from {From}: {user_msg}")
        
        # Initialize combined_input with user's text message
        combined_input = f"User message: {user_msg}\n" if user_msg else ""

        
        
        if NumMedia > 0:
            print("image analysis")
          
            # Download and analyze the image
            image = await ImageProcessor.download_image(MediaUrl0)
            image_analysis = await ImageProcessor.analyze_image(image)
            
            # Combine image analysis with user's text message
            combined_input += f"Image content: {image_analysis}"
            print(f"Combined input: {combined_input}")
            
            # Get the Vertex AI response based on combined input
            loop = asyncio.get_running_loop()
            try:
                bot_response = await loop.run_in_executor(
                    None,
                    partial(get_vertex_response_with_retry, combined_input, max_retries=3)
                )
                
                # Send messages directly using Twilio client
                for msg in bot_response:
                    message = client.messages.create(
                        to=From,
                        from_=f'whatsapp:{WHATSAPP_NUMBER}',
                        body=msg
                    )
                    print(f"Message sent (SID: {message.sid}): {msg[:100]}...")
                
                return {"status": "success"}
            
            except asyncio.TimeoutError:
                raise TimeoutError("Bot response timeout")
          
        else:
            print("text analysis")
            # Handle text-only messages
            loop = asyncio.get_running_loop()
            try:
                bot_response = await loop.run_in_executor(
                    None,
                    partial(get_vertex_response_with_retry, user_msg, max_retries=3)
                )
                
                # Send messages directly using Twilio client
                for msg in bot_response:
                    message = client.messages.create(
                        to=From,
                        from_=f'whatsapp:{WHATSAPP_NUMBER}',
                        body=msg
                    )
                    print(f"Message sent (SID: {message.sid}): {msg[:100]}...")

                return {"status": "success"}

            except asyncio.TimeoutError:
                raise TimeoutError("Bot response timeout")

    except Exception as e:
        print(f"Error occurred while processing the message: {str(e)}")
        error_msg = (
            "I apologize, but I'm having trouble processing your message. "
            "Please try again later."
        )
        message = client.messages.create(
            to=From,
            from_=f'whatsapp:{WHATSAPP_NUMBER}',
            body=error_msg
        )
        return {"status": "error", "message": str(e)}

# Optional: Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}