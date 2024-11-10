## Import the required libraries
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import logging
import time

## Third-Party Imports
from .utils.VertexAi import VertexAi
from .utils.GeminiClient import GeminiClient
from .utils.ImageAnalyzer import ImageProcessor
from .utils.SpeechToTextClient import SpeechProcessor

## Env
from .utils.config import PROJECT_ID, LOCATION_ID, AGENT_ID

'''
Init
'''
# Initialize the chat blueprint
chat_blueprint = Blueprint('chat', __name__)

# Configure the logging system
logging.basicConfig(
    level=logging.CRITICAL,
    format='%(levelname)s: %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# Clients
vertex_ai = VertexAi(PROJECT_ID, LOCATION_ID, AGENT_ID)
gemini_client = GeminiClient()
image_analyzer = ImageProcessor()
speech_processor = SpeechProcessor()

# Constants
curr_language = "English"


'''
Helper functions
'''
def get_vertex_response_with_retry(user_msg: str, max_retries: int = 3) -> list:
    for attempt in range(max_retries):
        try:
            response = vertex_ai.get_vertex_response(user_msg)
            if response:
                return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                raise
    raise Exception("Failed to get response after all retries")

def get_gemini_response(query: str) -> list[str]:
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
            query = f"Help me a more  friendly personality and please add some emojis when answering, do not be aggresive when answering this in the context of POSB digibank services and do not give me options and in {lang} and only in {lang} and also condense the answer to be a bit shorter, the text: {image_analysis}"
        else:
            logging.critical("State 2: Vertex AI can't understand respond to the user message")
            query = f"Help me adopt more a  friendly personality and please add some emojis when answering, do not be aggresive when answering this in the context of POSB digibank services and do not give me options when answering this in {lang} and only in {lang} and also condense the answer to be a bit shorter , the text: {user_msg}"
    else:
        if "english" not in lang.lower():
            logging.critical("State 3: Vertex AI gave a response but user asked in another language")
            query = f"Help me translate this message in {lang} and only in {lang} and making sure in the context of POSB digibank services and Help me to condense this answer to be abit shorter and give a more friendly  personality and please add some emojis when answering, do not be aggresive when answering this, the text: {bot_response}"
        else:
            logging.critical("State 4: Vertex AI gave a response")
            query = f"Help me to condense this answer to abit shorter and making sure in the context of POSB digibank services, the text: {bot_response} and just give a more friendly  personality and please add some emojis when answering, do not be aggresive when answering this"
    return get_gemini_response(query)


'''
Main Endpoints
'''
@chat_blueprint.route('', methods=['GET'])
def chat():
    return render_template('chat.html', segment='chat')

@chat_blueprint.route('/upload', methods=['POST'])
def upload_file():

    file = request.files['file']

    # If a file is selected, save it to the desired location
    if file:
        # Ensure the filename is safe to use
        filename = secure_filename(file.filename)
        # Define the path where the file will be saved
        filepath = os.path.join('src/static/upload/', filename)

        # Save the file
        file.save(filepath)
        return "success"
    
@chat_blueprint.route('/upload-audio', methods=['POST'])
def upload_audio():

    file = request.files['audio']

    # If a file is selected, save it to the desired location
    if file:
        # Ensure the filename is safe to use
        filename = secure_filename(file.filename)
        # Define the path where the file will be saved
        filepath = os.path.join('src/static/audio/', filename)

        # Save the file
        file.save(filepath)
        return "success"



@chat_blueprint.route("/web_message", methods=["GET"])
def handle_web_message():
    """Handle incoming web-based messages with text, image, and audio processing."""
    global curr_language
    user_msg = request.args.get("message", "")
    img = request.args.get("img", "")
    audio = request.args.get("audio", "")
    
    print(user_msg, img, audio)

    if user_msg:
        query = f"Identify language in one word and one word only for this message: {user_msg}"
        responses = get_gemini_response(query)
        curr_language = responses[0]
        if "english" not in curr_language.lower():
            query = f"Translate to English: {user_msg}"
            responses = get_gemini_response(query)
            user_msg = ' '.join(responses)
    logging.critical(f"Lang Detected: {curr_language}")

    image_analysis = None
    # try:
    if audio:
        logging.critical(f"Audio Detected")
        transcription = SpeechProcessor.transcribe_audio()
        combined_input = f"{transcription} and {user_msg}" if user_msg else transcription
    elif img:
        logging.critical(f"Image Detected")
        image_analysis = ImageProcessor.analyze_image()
        combined_input = f"{image_analysis} and {user_msg}" if user_msg else image_analysis
    else:
        logging.critical(f"Text Detected: {user_msg}")
        combined_input = user_msg

    bot_response = get_vertex_response_with_retry(combined_input)
    formatted_response = reformat_final_message(curr_language, bot_response, user_msg, image_analysis)
    return jsonify({"status": "success", "message": '&nbsp;'.join(formatted_response)})

    # except Exception as e:
    #     logging.critical(f"Error occurred: {str(e)}")
    #     return jsonify({"status": "error", "message": "An error occurred while processing your message."})