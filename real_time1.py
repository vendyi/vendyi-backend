import asyncio
import json
import websockets

async def test():
    token = "1e9e9f4ead5ce59ae79b5214392696f6f48f2a96"
    async with websockets.connect(f"wss://vendyi-92322aa588dc.herokuapp.com/ws/chat/chat_11_12/?token={token}") as websocket:
        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received message: {data}")

asyncio.run(test())
