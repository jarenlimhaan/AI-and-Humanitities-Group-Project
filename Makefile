.PHONY: run server ngrok

# Start the FastAPI server with Uvicorn in the frontend directory
server:
	cd whatsapp-bot && poetry run uvicorn main:app --port 8000 --reload

# Start ngrok to tunnel to localhost:8000
ngrok:
	ngrok http 8000

# Run both commands in parallel
run:
	# Run both server and ngrok concurrently
	make -j2 server ngrok
