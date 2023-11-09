import asyncio
import json
import websockets

async def test():
    token = "6f991c1a86623a25ba70b5bb42f821513ad52e53"
    async with websockets.connect(f"wss://vendyi-92322aa588dc.herokuapp.com/ws/chat/chat_1_2/?token={token}") as websocket:
        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received message: {data}")

asyncio.run(test())
