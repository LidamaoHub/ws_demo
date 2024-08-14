from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from pydantic import BaseModel
import logging
import asyncio
from typing import Dict, Set, Optional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.authenticated_users: Set[str] = set()

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"New connection established for user {user_id}")

    def authenticate(self, user_id: str):
        self.authenticated_users.add(user_id)
        logger.info(f"User {user_id} authenticated")

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        self.authenticated_users.discard(user_id)
        logger.info(f"User {user_id} disconnected")

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {str(e)}")
                self.disconnect(user_id)

    async def broadcast(self, message: str):
        disconnected = []
        for user_id, connection in self.active_connections.items():
            if user_id in self.authenticated_users:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {str(e)}")
                    disconnected.append(user_id)
        
        for user_id in disconnected:
            self.disconnect(user_id)

manager = ConnectionManager()

class Message(BaseModel):
    message: str
    userid: Optional[str] = None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    user_id = None
    try:
        user_id = f"user_{len(manager.active_connections) + 1}"
        await manager.connect(websocket, user_id)
        
        try:
            data = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
            message = json.loads(data)
            logger.debug(f"Received message: {message}")
            
            if message.get('type') != 'auth' or message.get('token') != '123456':
                logger.warning(f"Authentication failed for user {user_id}")
                await websocket.send_text("Authentication failed")
                await websocket.close(code=4000)
                return

            manager.authenticate(user_id)
            await websocket.send_text(f"Your user ID is: {user_id}")

            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                logger.debug(f"Received message from {user_id}: {message}")
                await manager.broadcast(f"Message from {user_id}: {message.get('message', '')}")
        except asyncio.TimeoutError:
            logger.warning(f"Authentication timeout for user {user_id}")
            await websocket.close(code=4000)
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from user {user_id}")
            await websocket.close(code=4000)
        except Exception as e:
            logger.error(f"Unexpected error for user {user_id}: {str(e)}")
            await websocket.close(code=4000)
    except Exception as e:
        logger.error(f"Error in websocket_endpoint: {str(e)}")
    finally:
        if user_id:
            manager.disconnect(user_id)
            await manager.broadcast(f"User {user_id} left the chat")

@app.post("/message")
async def send_message(message: Message):
    if message.userid:
        await manager.send_personal_message(message.message, message.userid)
    else:
        await manager.broadcast(f"REST API Message: {message.message}")
    return {"status": "Message sent"}

@app.get("/user_count")
async def get_user_count():
    return {
        "total_connections": len(manager.active_connections),
        "authenticated_users": len(manager.authenticated_users)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)