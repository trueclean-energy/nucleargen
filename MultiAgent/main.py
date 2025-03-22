# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json

from multiagent import MessageBus

app = FastAPI()
message_bus = MessageBus()

# Add CORS middleware to allow requests from the agent UIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you'd specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the absolute path to the static directory
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Serve static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve index.html as root
@app.get("/")
async def get():
    return FileResponse(os.path.join(static_dir, "index.html"))

# REST API endpoint for sending messages
@app.post("/api/message")
async def send_message(request: Request):
    data = await request.json()
    await message_bus.route_message(data)
    return JSONResponse({"status": "success", "message": "Message routed successfully"})

# REST API endpoint to get message history
@app.get("/api/messages")
async def get_messages():
    return JSONResponse({"messages": message_bus.message_log})

# REST API endpoint to get agent status
@app.get("/api/agents")
async def get_agents():
    agents = [
        {
            "id": "agent1",
            "name": "Schema Assistant",
            "type": "json-schema",
            "status": "active",
            "url": "http://localhost:3000"
        },
        {
            "id": "agent2",
            "name": "Data Validator",
            "type": "validation",
            "status": "active",
            "url": "http://localhost:5000"
        },
        {
            "id": "agent3",
            "name": "Visualization",
            "type": "visualization",
            "status": "active",
            "url": "#"
        }
    ]
    return JSONResponse({"agents": agents})

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