import uuid
import re
from google.cloud.dialogflowcx_v3 import AgentsClient, SessionsClient
from google.cloud.dialogflowcx_v3.types import TextInput, QueryInput, DetectIntentRequest

class VertexAi:

    def __init__(self, project_id: str, location_id: str, agent_id: str):
        self.project_id = project_id
        self.location_id = location_id
        self.agent_id = agent_id
        self.language_code = "en-us"
        self.agent = f"projects/{project_id}/locations/{location_id}/agents/{agent_id}"
        self.session_id = str(uuid.uuid4())  # Generate session ID once for reuse

    def split_message(self, text: str, max_length: int = 1600) -> list[str]:
        """Split a message by sentences or newline characters into smaller chunks."""
        # First, try to split by newline (\n) if present
        parts = text.split("-")

        # If any part exceeds max_length, split it further by punctuation (.!?)
        messages = []
        for part in parts:
            if len(part) > max_length:
                sentences = re.split(r'([.!?])', part)  # Keep punctuation as separate items
                chunk = ""
                for i in range(0, len(sentences) - 1, 2):  # Combine sentence + punctuation
                    sentence = sentences[i] + sentences[i + 1]
                    if len(chunk) + len(sentence) <= max_length:
                        chunk += sentence
                    else:
                        messages.append(chunk.strip())
                        chunk = sentence  # Start a new chunk
                if chunk:
                    messages.append(chunk.strip())
            else:
                messages.append(part.strip())

        return messages

    def get_vertex_response(self, user_msg: str) -> list[str]:
        """Send a message to Dialogflow CX and return the response as a list of messages."""
        session_path = f"{self.agent}/sessions/{self.session_id}"

        # Handle client options for regional endpoints
        client_options = None
        agent_components = AgentsClient.parse_agent_path(self.agent)
        location_id = agent_components["location"]
        if location_id != "global":
            api_endpoint = f"{location_id}-dialogflow.googleapis.com:443"
            client_options = {"api_endpoint": api_endpoint}

        # Create a session client
        session_client = SessionsClient(client_options=client_options)

        # Create the input and detect intent request
        text_input = TextInput(text=user_msg)
        query_input = QueryInput(text=text_input, language_code=self.language_code)
        request = DetectIntentRequest(session=session_path, query_input=query_input)

        # Get the response from Dialogflow
        response = session_client.detect_intent(request=request)

        # Extract and flatten the response messages
        full_message = " ".join(
            " ".join(msg.text.text) for msg in response.query_result.response_messages if msg.text.text
        )

        # Split the response into smaller chunks if needed
        return self.split_message(full_message)