# Standard Library Imports 
from fastapi import FastAPI,Form
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Optional
from functools import partial
import time
import logging

# Services 
from services.VertexAi import VertexAi
from services.TwilioClient import TwilioClient
from services.GeminiClient import GeminiClient
from services.ImageAnalyzer import ImageProcessor
from services.SpeechToTextClient import SpeechProcessor

# Utils 
from utils.func import create_response

# Env 
from utils.config import PROJECT_ID, LOCATION_ID, \
    AGENT_ID, ACCOUNT_SID, AUTH_TOKEN, WHATSAPP_NUMBER\

'''
Init 
'''
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

## Configure the logging system
logging.basicConfig(
    level=logging.CRITICAL,                   
    format='%(levelname)s: %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',           
)

## Clients 
vertex_ai = VertexAi(PROJECT_ID, LOCATION_ID, AGENT_ID)
gemini_client = GeminiClient()
image_analyzer = ImageProcessor()
speech_processor = SpeechProcessor()
client = TwilioClient(ACCOUNT_SID, AUTH_TOKEN, WHATSAPP_NUMBER).client

## Constants 
curr_language = "English"

'''
Helper functions 
'''
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

def get_gemini_response(query: str) -> list[str]:
    """Get response from Gemini with retry logic"""
    response = gemini_client.model.generate_content(
        [query],
        generation_config=gemini_client.generation_config,
        safety_settings=gemini_client.safety_settings,
        stream=True,
    )
    response_text = [msg.text.strip() for msg in response if msg.text]

    # Combine the first two elements and keep the rest as they are
    if len(response_text) >= 2:
        response_text = [response_text[0] + ' ' + response_text[1]] + response_text[2:]
    return response_text

def reformat_final_message(lang: str, bot_responses: list[str], user_msg: str, image_analysis = None) -> list[str]:
    bot_response = ''.join(bot_responses)
    if "sorry" in bot_response.lower() or "rephrasing" in bot_response.lower():
        if image_analysis != None:
            logging.critical("State 1: Vertex AI can't respond to image analysis with/without user msg")
            query = f"Help me a more  friendly personality and please add some emojis when answering, do not be aggresive when answering this in the context of POSB digibank services and do not give me options and in {lang} and only in {lang} and also condense the answer to be a bit shorter and give me in point forms, the text: {image_analysis}"
        else:
            logging.critical("State 2: Vertex AI can't understand respond to the user message")
            query = f"Help me adopt more a  friendly personality and please add some emojis when answering, do not be aggresive when answering this in the context of POSB digibank services and do not give me options when answering this in {lang} and only in {lang} and also condense the answer to be a bit shorter and give me in point forms, the text: {user_msg}"
    else:
        if "english" not in lang.lower():
            logging.critical("State 3: Vertex AI gave a response but user asked in another language")
            query = f"Help me translate this message in {lang} and only in {lang} and making sure in the context of POSB digibank services and Help me to condense this answer to be abit shorter and give a more friendly  personality and please add some emojis when answering, do not be aggresive when answering this and give me in point forms, the text: {bot_response}"
        else:
            logging.critical("State 4: Vertex AI gave a response")
            query = f"Help me to condense this answer to abit shorter and making sure in the context of POSB digibank services, the text: {bot_response} and just give a more friendly  personality and please add some emojis when answering, do not be aggresive and give me in point forms when answering this"
    return get_gemini_response(query)

'''
Main Endpoints
'''
@app.post("/whatsapp")
async def handle_whatsapp(
    From: str = Form(...),
    Body: str = Form(...),
    NumMedia: int = Form(default=0),
    MediaUrl0: Optional[str] = Form(default=None),
    MediaContentType0: Optional[str] = Form(default=None),
):
    """Handle incoming WhatsApp messages with combined text, image, and audio processing."""
    global previous_bot_message, curr_language
    user_msg = Body.strip()

    ## Check if the user message's language and if is not english i need to reformat 
    ## back to english to pass to vertex ai as it only understands english
    if user_msg != '':
        query = f"Give me in one word and one word only, what is this language and do not categorise the message, I just want the language: {user_msg}"  
        responses = get_gemini_response(query)
        curr_language = responses[0]
        if "english" not in curr_language.lower():
            query  = f"Help me translate this message back to english and only give me the message back in english: {user_msg}"  
            responses = get_gemini_response(query)
            user_msg = ' '.join(responses)
    logging.critical(f"Lang Detected: {curr_language}")

    image_analysis = None

    try:
        ## If video or audio is detected
        if NumMedia > 0:
            if MediaContentType0 and MediaContentType0.startswith("audio/"):
                logging.critical(f"Audio Detected: {MediaUrl0}")
                
                # Download and transcribe the audio
                audio_bytes = await SpeechProcessor.download_audio(audio_url=MediaUrl0)
                transcription = await SpeechProcessor.transcribe_audio(audio_bytes)

                combined_input = f"{transcription} and I want to ask {user_msg}" if user_msg else transcription
                combined_input = combined_input.replace("\n", " ")
                
            elif MediaContentType0 and MediaContentType0.startswith("image/"):
                logging.critical(f"Image Detected: {MediaUrl0}")
                
                # Download and analyze the image
                image = await ImageProcessor.download_image(MediaUrl0)
                image_analysis = await ImageProcessor.analyze_image(image)
                combined_input = f"{image_analysis}  and I want to ask {user_msg}" if user_msg else image_analysis
                combined_input = combined_input.replace("\n", " ")

  

            loop = asyncio.get_running_loop()
            bot_response = await loop.run_in_executor(
                None,
                partial(get_vertex_response_with_retry, combined_input, max_retries=3)
            )  

        else:
            logging.critical(f"Text Detected: {user_msg}")
            loop = asyncio.get_running_loop()
            bot_response = await loop.run_in_executor(
                None,
                partial(get_vertex_response_with_retry, user_msg, max_retries=3)
            )

        # Send the final response
        formatted_response = reformat_final_message(curr_language, bot_response, user_msg, image_analysis)
        msg = '\n'.join(formatted_response)
        print(formatted_response)
        create_response(client, From, WHATSAPP_NUMBER, msg)
        return {"status": "success"}

    except asyncio.TimeoutError:
        create_response(client, From, WHATSAPP_NUMBER, "The response is taking too long. Please try again later.")
        return {"status": "error", "message": "Bot response timeout"}

    except Exception as e:
        logging.critical(f"Error occurred while processing the message: {str(e)}")
        error_msg = (
            "I apologize, but I'm having trouble processing your message. "
            "Please try again later."
        )
        create_response(client, From, WHATSAPP_NUMBER, error_msg)
        return {"status": "error", "message": str(e)}