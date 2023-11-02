import asyncio
import json
import websockets

async def test():
    token = "28ac666c27913a5da80bc913033441e4a881f30b"
    async with websockets.connect(f"ws://localhost:8000/ws/chat/chat_1_2/?token={token}") as websocket:
        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received message: {data}")

asyncio.run(test())
