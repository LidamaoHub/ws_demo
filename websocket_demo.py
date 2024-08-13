import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional
import json
from pydantic import BaseModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.authenticated_users: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    async def authenticate(self, websocket: WebSocket, user_id: str):
        self.active_connections[user_id] = websocket
        self.authenticated_users[websocket] = user_id

    def disconnect(self, websocket: WebSocket):
        user_id = self.authenticated_users.get(websocket)
        if user_id:
            self.active_connections.pop(user_id, None)
            self.authenticated_users.pop(websocket, None)

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

class Message(BaseModel):
    message: str
    userid: Optional[str] = None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_text("Invalid message format. Please send JSON.")
                continue

            if message.get('type') == 'auth':
                if message.get('token') == '123456':  # Your authentication logic here
                    user_id = f"user_{len(manager.active_connections) + 1}"
                    await manager.authenticate(websocket, user_id)
                    await websocket.send_text(f"Your user ID is: {user_id}")
                else:
                    await websocket.send_text("Authentication failed. Please try again.")
            elif websocket in manager.authenticated_users:
                user_id = manager.authenticated_users[websocket]
                await manager.broadcast(f"Message from {user_id}: {message.get('message', '')}")
            else:
                await websocket.send_text("Please authenticate first.")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        user_id = manager.authenticated_users.get(websocket)
        if user_id:
            await manager.broadcast(f"User {user_id} left the chat")

@app.post("/message")
async def send_message(message: Message):
    if message.userid:
        await manager.send_personal_message(message.message, message.userid)
    else:
        await manager.broadcast(message.message)
    return {"status": "Message sent"}

@app.get("/user_count")
async def get_user_count():
    return {"user_count": len(manager.active_connections)}

@app.get("/hardware_status")
async def get_hardware_status():
    with open('/sys/fs/cgroup/memory/memory.usage_in_bytes', 'r') as f:
        memory_usage = int(f.read().strip()) / (1024 * 1024)  # Convert to MB
    
    with open('/sys/fs/cgroup/cpu/cpuacct.usage', 'r') as f:
        cpu_usage = int(f.read().strip())
    
    # Calculate CPU usage percentage (this is an approximation)
    cpu_delta = cpu_usage - get_hardware_status.last_cpu_usage if hasattr(get_hardware_status, 'last_cpu_usage') else 0
    get_hardware_status.last_cpu_usage = cpu_usage
    cpu_percent = cpu_delta / 1000000000 * 100  # Convert to percentage

    return {"memory_usage_mb": round(memory_usage, 2), "cpu_percent": round(cpu_percent, 2)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)