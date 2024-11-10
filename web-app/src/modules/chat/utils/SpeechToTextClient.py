import os
import glob
from google.cloud import speech_v1
from pydub import AudioSegment

class SpeechProcessor:
    @staticmethod
    def transcribe_audio() -> str:
        """Transcribe the latest uploaded audio file using Google Cloud Speech-to-Text API"""
        try:
            # List all audio files in the directory and get the latest file
            files = glob.glob(os.path.join('src/static/audio/', '*'))
            if not files:
                return 'No audio files uploaded yet.'

            latest_file = max(files, key=os.path.getmtime)
            print(f"Processing latest audio file: {latest_file}")

            # Read the latest audio file as bytes
            with open(latest_file, 'rb') as audio_file:
                audio_bytes = audio_file.read()

            # Set up the Google Cloud Speech client
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "src/modules/chat/utils/key.json"
            client = speech_v1.SpeechClient()

            # Configure the audio and request settings
            audio = speech_v1.RecognitionAudio(content=audio_bytes)
            config = speech_v1.RecognitionConfig(
                encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
                enable_automatic_punctuation=True,
                audio_channel_count=1,
            )

            # Perform transcription
            print("Sending request to Google Speech-to-Text...")
            response = client.recognize(config=config, audio=audio)
            print(f"Got response: {response}")

            # Extract transcript from response
            if response.results:
                transcript = " ".join(
                    result.alternatives[0].transcript 
                    for result in response.results
                )
                print(f"Transcribed text: {transcript}")
                return transcript
                
            return "I'm sorry, but I couldn't transcribe any audio."

        except Exception as e:
            print(f"Transcription error: {str(e)}")
            return f"Error transcribing audio: {str(e)}"