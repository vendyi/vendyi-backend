import asyncio
import json
import websockets

async def test():
    token = "33303ea111906f76068f949a192d9939e51f6da4"
    async with websockets.connect(f"ws://localhost:8000/ws/chat/chat_1_2/?token={token}") as websocket:
        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received message: {data}")

asyncio.run(test())
