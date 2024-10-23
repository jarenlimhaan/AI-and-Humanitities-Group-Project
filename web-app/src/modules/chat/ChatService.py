import os 
from .utils.Analyzer import ScreenshotAnalyzer
import glob
analyzer = ScreenshotAnalyzer()

class ChatService:

    @staticmethod
    def read_image():
        files = glob.glob(os.path.join('src/static/upload/', '*'))  # List all files
        if not files:
            return 'No files uploaded yet.', 404

        # Find the latest file based on modification time
        latest_file = max(files, key=os.path.getmtime)
        result = analyzer.analyze_screenshot(latest_file)
        return result
        
    