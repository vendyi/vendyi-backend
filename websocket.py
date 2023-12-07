import asyncio
import json
import websockets

async def test():
    token = "590de61fa1e622faa0af8ed8510ca287c6e8ef6a"
    async with websockets.connect(f"wss://vendyi-backend.onrender.com/ws/chat/chat_1_8/?token={token}") as websocket:
        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received message: {data}")

asyncio.run(test())
