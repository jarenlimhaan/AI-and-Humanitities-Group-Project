import os
import io
import aiohttp
import asyncio
from google.cloud import speech
from google.cloud.speech_v1 import types

from utils.config import ACCOUNT_SID, AUTH_TOKEN

class SpeechProcessor:
    @staticmethod
    async def download_audio(audio_url: str) -> bytes:
        """Download an audio file from a URL"""
        auth = aiohttp.BasicAuth(login=ACCOUNT_SID, password=AUTH_TOKEN)
        async with aiohttp.ClientSession() as session:
            async with session.get(audio_url, auth=auth) as response:
                return await response.read()

    @staticmethod
    async def transcribe_audio(audio_bytes: bytes) -> str:
        """Transcribe audio using Google Cloud Speech-to-Text API"""
        # Set up the Google Cloud Speech client
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./services/key.json"
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

    @classmethod
    async def process_audio_from_url(cls, audio_url: str) -> str:
        """Download and transcribe an audio file from a URL"""
        audio_bytes = await cls.download_audio(audio_url)
        return await cls.transcribe_audio(audio_bytes)
