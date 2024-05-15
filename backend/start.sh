#!/bin/sh
# Set ngrok authtoken
ngrok authtoken $NGROK_AUTHTOKEN

# Start uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start ngrok
ngrok http 8000
