import os
import io
import glob
from PIL import Image
from google.cloud import vision
from google.cloud.vision_v1 import types

class ImageProcessor:
    @staticmethod
    def analyze_image(upload_dir: str = "src/static/upload", credentials_path: str = "src/modules/chat/utils/key.json") -> str:
        """
        Get the latest image from upload directory and analyze it using Google Cloud Vision API
        """
        # Get the latest image
        files = glob.glob(os.path.join(upload_dir, '*'))
        if not files:
            return "No images found in upload directory"
            
        image_path = max(files, key=os.path.getmtime)
        
        # Set up the Google Cloud Vision client
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        client = vision.ImageAnnotatorClient()

        # Load and convert the image to bytes
        with Image.open(image_path) as image:
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="PNG")
            image_bytes = image_bytes.getvalue()

        # Create an Image object for the Vision API
        vision_image = types.Image(content=image_bytes)

        # Perform image analysis
        response = client.annotate_image({"image": vision_image})

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