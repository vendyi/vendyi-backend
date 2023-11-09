import asyncio
import json
import websockets

async def test():
    token = "01e6ffed3b74832b6481eff0268f7f1e9806633a"
    async with websockets.connect(f"ws://localhost:8000/ws/chat/chat_1_2/?token={token}") as websocket:
        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received message: {data}")

asyncio.run(test())
