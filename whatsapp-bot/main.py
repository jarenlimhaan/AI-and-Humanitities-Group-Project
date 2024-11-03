# Standard Library Imports 
from fastapi import FastAPI,Form
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Optional
from functools import partial
import time

# Services 
from services.VertexAi import VertexAi
from services.TwilioClient import TwilioClient
from services.GeminiClient import GeminiClient
from services.ImageAnalyzer import ImageProcessor

# Utils 
from utils.func import create_response, create_interactive_response

# Env 
from utils.config import PROJECT_ID, LOCATION_ID, \
    AGENT_ID, ACCOUNT_SID, AUTH_TOKEN, WHATSAPP_NUMBER\
    ,CONTENT_TEMPLATE_SID

'''
Init 
'''
app = FastAPI()
previous_message = []

## Clients 
vertex_ai = VertexAi(PROJECT_ID, LOCATION_ID, AGENT_ID)
gemini_client = GeminiClient()
image_analyzer = ImageProcessor()
client = TwilioClient(ACCOUNT_SID, AUTH_TOKEN, WHATSAPP_NUMBER).client

## CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

## Helper functions 
## TODO: Move this to a separate file
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
    MediaUrl0: Optional[str] = Form(default=None),
    ButtonText: Optional[str] = Form(default=None),
    SelectedButtonId: Optional[str] = Form(default=None),
    InteractiveButtonReplyId: Optional[str] = Form(default=None)
):
    """Handle incoming WhatsApp messages with combined text and image processing"""
    try:
        global previous_message

        # Initialize combined input with user's text message
        user_msg = Body.strip()

        '''
        Handle Interactive Buttons
        '''
        if any([ButtonText, SelectedButtonId, InteractiveButtonReplyId]):
            original_message = "Help me translate this message to only hindi and only the raw hindi message: " + ' '.join(previous_message)  
            responses = gemini_client.model.generate_content(
                [original_message],
                generation_config=gemini_client.generation_config,
                safety_settings=gemini_client.safety_settings,
                stream=True,
            )
            for msg in responses:
                send_message = msg.text
                if send_message:
                    client.messages.create(
                        to=From,
                        from_=f'whatsapp:{WHATSAPP_NUMBER}',
                        body=send_message
                    )
            return {"status": "success"}
        elif NumMedia > 0: 
            print("Image Detected: ", MediaUrl0)
            
            # Download and analyze the image
            image = await ImageProcessor.download_image(MediaUrl0)
            image_analysis = await ImageProcessor.analyze_image(image)

            combined_input = ""
            
            # Combine image analysis with user's text message
            combined_input += f"{image_analysis}"
            combined_input += f"and i wanna ask {user_msg}"
            combined_input = combined_input.replace("\n", " ")
            
            try:
                loop = asyncio.get_running_loop()
                bot_response = await loop.run_in_executor(
                    None,
                    partial(get_vertex_response_with_retry, combined_input, max_retries=3)
                )

                print(combined_input, bot_response)

                previous_message = [response for response in bot_response]  

                for msg in bot_response:
                    create_response(client, From, WHATSAPP_NUMBER, msg)
                create_interactive_response(client, From, WHATSAPP_NUMBER, CONTENT_TEMPLATE_SID)

                return {"status": "success"}
            
            except asyncio.TimeoutError:
                raise TimeoutError("Bot response timeout")
        else:
            print("Text Detected: ", user_msg)
            try:
                loop = asyncio.get_running_loop()
                bot_response = await loop.run_in_executor(
                    None,
                    partial(get_vertex_response_with_retry, user_msg, max_retries=3)
                )

                previous_message = [response for response in bot_response]

                for msg in bot_response:
                    create_response(client, From, WHATSAPP_NUMBER, msg)
                create_interactive_response(client, From, WHATSAPP_NUMBER, CONTENT_TEMPLATE_SID)

                return {"status": "success"}

            except asyncio.TimeoutError:
                raise TimeoutError("Bot response timeout")
            
    except Exception as e:
        print(f"Error occurred while processing the message: {str(e)}")
        error_msg = (
            "I apologize, but I'm having trouble processing your message. "
            "Please try again later."
        )
        create_response(client, From, WHATSAPP_NUMBER, error_msg)
        return {"status": "error", "message": str(e)}