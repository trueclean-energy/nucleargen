# multiagent.py - Orchestration logic
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import asyncio
import json

# Import mock agent functions
from mock_agents import process_schema_question, validate_model, render_component

# Message routing and orchestration
class MessageBus:
    def __init__(self):
        self.active_connections = []
        self.message_log = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        # Log message
        self.message_log.append({
            "timestamp": message.get("timestamp"),
            "type": message.get("type"),
            "content": message.get("content")
        })
        
        # Send to all clients
        for connection in self.active_connections:
            await connection.send_json(message)
    
    async def route_message(self, message: dict):
        """Route message to appropriate agent and broadcast response"""
        msg_type = message.get("type")
        content = message.get("content")
        
        if msg_type == "schema.question":
            # Route to Agent 1
            response = process_schema_question(content)
            await self.broadcast({
                "type": "schema.response",
                "content": response,
                "timestamp": message.get("timestamp")
            })
            
        elif msg_type == "validation.request":
            # Route to Agent 2
            results = validate_model(content)
            await self.broadcast({
                "type": "validation.response",
                "content": results,
                "timestamp": message.get("timestamp")
            })
            
        elif msg_type == "visualization.request":
            # Route to Agent 3
            svg = render_component(content)
            await self.broadcast({
                "type": "visualization.response", 
                "content": svg,
                "timestamp": message.get("timestamp")
            })