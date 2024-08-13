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
        self.authenticated_users: Dict[int, str] = {}  # 使用 WebSocket 的 id 作为键

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
    

    async def authenticate(self, websocket: WebSocket, user_id: str):
        self.active_connections[user_id] = websocket
        self.authenticated_users[id(websocket)] = user_id  # 使用 WebSocket 对象的 id

    async def authenticate(self, websocket: WebSocket, user_id: str):
        self.active_connections[user_id] = websocket
        self.authenticated_users[websocket] = user_id

    def disconnect(self, websocket: WebSocket):
        user_id = self.authenticated_users.get(id(websocket))
        if user_id:
            self.active_connections.pop(user_id, None)
            self.authenticated_users.pop(id(websocket), None)

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
                if message.get('token') == '123456':  # 您的身份验证逻辑
                    user_id = f"user_{len(manager.active_connections) + 1}"
                    await manager.authenticate(websocket, user_id)
                    await websocket.send_text(f"Your user ID is: {user_id}")
                else:
                    await websocket.send_text("Authentication failed. Please try again.")
            elif id(websocket) in manager.authenticated_users:  # 使用 WebSocket 的 id 检查身份验证
                user_id = manager.authenticated_users[id(websocket)]
                await manager.broadcast(f"Message from {user_id}: {message.get('message', '')}")
            else:
                await websocket.send_text("Please authenticate first.")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        user_id = manager.authenticated_users.get(id(websocket))
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)