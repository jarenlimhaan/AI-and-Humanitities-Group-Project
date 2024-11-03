import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting

class GeminiClient:

    def __init__(self):
        self.generation_config = {"max_output_tokens": 8192, "temperature": 1, "top_p": 0.95,}
        self.vertexai = vertexai.init(project="dbs-chatbot-438904", location="us-central1")
        self.model = GenerativeModel(
            "gemini-1.5-flash-002",
        )
        self.safety_settings = [
                SafetySetting(
                    category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=SafetySetting.HarmBlockThreshold.OFF
                ),
                SafetySetting(
                    category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=SafetySetting.HarmBlockThreshold.OFF
                ),
                SafetySetting(
                    category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    threshold=SafetySetting.HarmBlockThreshold.OFF
                ),
                SafetySetting(
                    category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    threshold=SafetySetting.HarmBlockThreshold.OFF
                ),
            ]

