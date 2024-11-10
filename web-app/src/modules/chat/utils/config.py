from dotenv import load_dotenv
import os

# Get the current working directory
current_directory = os.getcwd()
print(current_directory)

# Specify the path to your .env file
dotenv_path = 'src/modules/chat/utils/.env'  # Replace with the actual path to your .env file
load_dotenv(dotenv_path)

'''
Env variables
'''
## Vertex AI - Model
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION_ID = os.getenv("LOCATION_ID")
AGENT_ID = os.getenv("AGENT_ID")

## Twilio - WhatsApp
ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")
CONTENT_TEMPLATE_SID = os.getenv("CONTENT_TEMPLATE_SID")

