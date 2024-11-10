import os
import glob
from google.cloud import speech
from google.cloud.speech_v1 import types

class SpeechProcessor:

    @staticmethod
    async def transcribe_audio() -> str:
        """Transcribe the latest uploaded audio file using Google Cloud Speech-to-Text API"""

        # List all audio files in the directory and get the latest file
        files = glob.glob(os.path.join('src/static/audio/', '*'))
        if not files:
            return 'No audio files uploaded yet.', 404

        latest_file = max(files, key=os.path.getmtime)

        # Read the latest audio file as bytes
        with open(latest_file, 'rb') as audio_file:
            audio_bytes = audio_file.read()

        # Set up the Google Cloud Speech client
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "src/modules/chat/utils/key.json"
        client = speech.SpeechClient()

        # Configure the audio and request settings
        audio = types.RecognitionAudio(content=audio_bytes)
        config = types.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=16000,  # Adjust this according to your audio file's settings
            language_code="en-SG",
        )

        # Perform transcription
        response = client.recognize(config=config, audio=audio)

        # Extract transcript from response
        if response.results:
            transcript = " ".join(result.alternatives[0].transcript for result in response.results)
            return transcript
        return "I'm sorry, but I couldn't transcribe any audio."
