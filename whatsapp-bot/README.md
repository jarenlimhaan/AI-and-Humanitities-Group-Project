## Running the Whatsapp-bot

1. Open Terminal
```bash
poetry install 
```

2. In the same terminal 
```bash
poetry run uvicorn main:app --port 8000 --reload
```

3. Open another Terminal
```bash 
ngrok http http://localhost:8000
```
-> make sure to change in twilio too