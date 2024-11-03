import os
import io
import aiohttp
import asyncio
from PIL import Image
from google.cloud import vision
from google.cloud.vision_v1 import types

from utils.config import ACCOUNT_SID, AUTH_TOKEN

class ImageProcessor:
    @staticmethod
    async def download_image(image_url: str) -> Image.Image:
        """Download an image from a URL"""
        auth = aiohttp.BasicAuth(login=ACCOUNT_SID, password=AUTH_TOKEN)
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url, auth=auth) as response:
                image_bytes = await response.read()
                return Image.open(io.BytesIO(image_bytes))

    @staticmethod
    async def analyze_image(image: Image.Image) -> str:
        """Analyze an image using Google Cloud Vision API"""
        # Set up the Google Cloud Vision client
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "services/key.json"
        client = vision.ImageAnnotatorClient()

        # Convert the PIL Image to a bytes object
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes = image_bytes.getvalue()

        # Create an Image object for the Vision API
        vision_image = types.Image(content=image_bytes)

        # Perform image analysis
        response = await asyncio.get_event_loop().run_in_executor(
            None, client.annotate_image, {"image": vision_image}
        )

        # Extract relevant information from the response
        text_annotations = response.text_annotations
        if text_annotations:
            text = text_annotations[0].description
            return text
        else:
            labels = response.label_annotations
            if labels:
                labels_text = ", ".join([label.description for label in labels])
                return f"Given the current context: {labels_text}"
        return "I'm sorry, but I couldn't extract any useful information from the image."