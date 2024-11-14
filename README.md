# Overview
This project offers a **web application** and a **WhatsApp chatbot** to help migrant workers access and use **DBS DigiBank services** with ease. The aim is to bridge the digital literacy gap, empowering users to manage their finances securely and independently.

Project Structure:
- **Web Application**: Built with Flask, providing an educational platform where users can learn about digital banking.
- **WhatsApp Chatbot**: Built with FastAPI and powered by Twilio, the chatbot offers accessible, real-time assistance through WhatsApp.

Endpoints:
- Whatsapp-bot: http://wa.me/+14155238886?text=join%20spoken-likely 
   - Enter "join spoken-likely"
- Web-app: http://152.42.235.175:5000/

## Features
---

### Web Application (Flask)
- **Educational Modules**: Interactive guides and tutorials on topics like account management, fund transfers, and online payments.
- **Multi-Language Support**: Ensures content accessibility by supporting multiple languages.
- **Real-Time Assistance**: Provides immediate help and answers to common questions about digital banking services.

### WhatsApp Chatbot (FastAPI)
- **Real-Time Assistance**: Provides immediate help and answers to common questions about digital banking services.
- **Twilio Integration**: Integrated with Twilio’s WhatsApp API for seamless WhatsApp communication.
- **Language Options**: Supports multiple languages to accommodate diverse users.
- **Simple Commands**: Users can interact with the chatbot through straightforward commands and questions for ease of use.
- **Speech Recognition**: Users can use the whatsapp in-built microphone to ask the chatbot questions as well.
- **Image Recognition**

### Tech Stack
---
- **Frontend**: Jinja HTML (for the web app interface)
- **Backend**:
  - Flask (for the web application)
  - FastAPI (for the WhatsApp chatbot)
- **APIs**: Twilio (for WhatsApp integration with the chatbot), Google Cloud services 
- **Deployment**: Digital Ocean for consistent and scalable deployment

## Installation
---

### Prerequisites
- Python 3.11 or later
- Twilio account and API credentials for WhatsApp integration
- Google Cloud Service Account

### Setting Up Google Account 
1) Google Cloud Account: Ensure you have a Google Cloud account and access to the relevant services.
2) Google Cloud Project: Set up a project in the Google Cloud Console.
3) Billing Enabled: Make sure billing is enabled for your project if needed by your chosen services.

Set Up Google Cloud SDK (if not already installed)
- The Google Cloud SDK allows you to authenticate and manage Google Cloud resources from the command line.
- Install Google Cloud SDK:
   - https://cloud.google.com/sdk/docs/install
- Follow the instructions to install the SDK here.
- Initialize and Authenticate:
    - Open a terminal or command prompt and run:
    - gcloud init
This command will guide you through selecting your Google Cloud project and authenticating with your Google account.



### Setup Instructions

1. **Set up environment variables**:
   - Create a `.env` file in both the `web-app` and `whatsapp-bot` "util" directories for both of these directories with the required environment variables, such as database credentials, Twilio API keys, and other secrets.
   - Do include the service key json that is retrieved on the service account page over here:
   - https://console.cloud.google.com/apis/credentials

3. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

4. **Web Application (Flask) Setup**:
   - Navigate to the `web-app` directory, install dependencies:
   ```bash
   cd web-app
   poetry install
   poetry run python main.py
   ```

5. **WhatsApp Chatbot (FastAPI) Setup**:
   - Navigate to the `whatsapp-bot` directory and install dependencies:
   ```bash
   cd ../whatsapp-bot
   poetry install
   poetry run uvicorn main:app --reload
   ```

## Usage

- **Web App**: Users access educational content on digital banking via the web app and access to web-based ui chat.
- **WhatsApp Chatbot**: Users can send questions or commands to the chatbot for immediate assistance.

## Contributing
We welcome contributions! Please open an issue first to discuss changes. For major changes, please open a pull request.

## License
This project is licensed under the MIT License.

## Acknowledgments
- **DBS Bank** for resources on DigiBank services.
- **Twilio** for providing WhatsApp API for easy integration.