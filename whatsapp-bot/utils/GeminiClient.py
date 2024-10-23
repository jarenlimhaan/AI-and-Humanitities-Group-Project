import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting

class GeminiClient:

    def __init__(self):
        self.generation_config = generation_config = {"max_output_tokens": 8192, "temperature": 1, "top_p": 0.95,}
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

    def fetch_response(self, msg):
        vertexai.init(project="dbs-chatbot-438904", location="us-central1")
        model = GenerativeModel(
            "gemini-1.5-flash-002",
        )
        responses = model.generate_content(
            [msg],
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
            stream=True,
        )

        for response in responses:
            print(response.text, end="")

        return responses[0].text

