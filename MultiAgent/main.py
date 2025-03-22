# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from multiagent import MessageBus

app = FastAPI()
message_bus = MessageBus()

# Get the absolute path to the static directory
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Serve static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve index.html as root
@app.get("/")
async def get():
    return FileResponse(os.path.join(static_dir, "index.html"))

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await message_bus.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await message_bus.route_message(data)
    except WebSocketDisconnect:
        message_bus.disconnect(websocket)