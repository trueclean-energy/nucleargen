# multiagent.py - Orchestration logic
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import httpx
import time
from datetime import datetime

# Import mock agent functions for fallback/testing
from mock_agents import process_schema_question, validate_model, render_component

# Message routing and orchestration
class MessageBus:
    def __init__(self):
        self.active_connections = []
        self.message_log = []
        self.agent_states = {
            "agent1": {"last_active": None, "status": "unknown"},
            "agent2": {"last_active": None, "status": "unknown"},
            "agent3": {"last_active": None, "status": "unknown"}
        }
        self.agent_urls = {
            "agent1": "http://localhost:3000/api/message",
            "agent2": "http://localhost:5000/api/validate",
            "agent3": "http://localhost:8000/api/visualize"
        }
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        # Log message
        timestamp = message.get("timestamp") or datetime.now().isoformat()
        log_entry = {
            "id": len(self.message_log) + 1,
            "timestamp": timestamp,
            "type": message.get("type"),
            "content": message.get("content"),
            "source": message.get("source", "unknown"),
            "target": message.get("target", "all")
        }
        
        self.message_log.append(log_entry)
        
        # Update agent state if applicable
        if "source" in message and message["source"] in self.agent_states:
            self.agent_states[message["source"]]["last_active"] = timestamp
            self.agent_states[message["source"]]["status"] = "active"
        
        # Send to all WebSocket clients
        for connection in self.active_connections:
            await connection.send_json(message)
    
    async def send_to_agent(self, agent_id, message):
        """Send a message to an agent via HTTP"""
        if agent_id in self.agent_urls:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.agent_urls[agent_id],
                        json=message,
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        self.agent_states[agent_id]["status"] = "active"
                        self.agent_states[agent_id]["last_active"] = datetime.now().isoformat()
                        return True
                    else:
                        return False
            except Exception as e:
                print(f"Error sending to agent {agent_id}: {str(e)}")
                return False
        return False
    
    async def route_message(self, message: dict):
        """Route message to appropriate agent and broadcast response"""
        msg_type = message.get("type")
        content = message.get("content")
        source = message.get("source", "user")
        
        # Log the incoming message
        await self.broadcast(message)
        
        # Route based on message type
        if msg_type == "schema.question":
            # First try to send to Agent 1
            success = await self.send_to_agent("agent1", {
                "type": "schema.question",
                "content": content,
                "timestamp": message.get("timestamp", datetime.now().isoformat()),
                "source": "hub",
                "target": "agent1"
            })
            
            if not success:
                # Fallback to mock
                response = process_schema_question(content)
                await self.broadcast({
                    "type": "schema.response",
                    "content": response,
                    "timestamp": datetime.now().isoformat(),
                    "source": "agent1",
                    "target": "hub"
                })
            
        elif msg_type == "validation.request":
            # Try to send to Agent 2
            success = await self.send_to_agent("agent2", {
                "type": "validation.request",
                "content": content,
                "timestamp": message.get("timestamp", datetime.now().isoformat()),
                "source": "hub",
                "target": "agent2"
            })
            
            if not success:
                # Fallback to mock
                results = validate_model(content)
                await self.broadcast({
                    "type": "validation.response",
                    "content": results,
                    "timestamp": datetime.now().isoformat(),
                    "source": "agent2", 
                    "target": "hub"
                })
            
        elif msg_type == "visualization.request":
            # Try to send to Agent 3
            success = await self.send_to_agent("agent3", {
                "type": "visualization.request",
                "content": content,
                "timestamp": message.get("timestamp", datetime.now().isoformat()),
                "source": "hub",
                "target": "agent3"
            })
            
            if not success:
                # Fallback to mock
                svg = render_component(content)
                await self.broadcast({
                    "type": "visualization.response", 
                    "content": svg,
                    "timestamp": datetime.now().isoformat(),
                    "source": "agent3",
                    "target": "hub"
                })
        
        # Handle responses from agents
        elif msg_type in ["schema.response", "validation.response", "visualization.response"]:
            # Forward the response to all clients
            await self.broadcast(message)