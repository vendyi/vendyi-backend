import asyncio
import json
import websockets

async def test():
    token = "a765d41713edb64df7ef10dc7441bdf1d05559f1"
    async with websockets.connect(f"wss://vendyi-92322aa588dc.herokuapp.com/ws/chat/chat_3_11/?token={token}") as websocket:
        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received message: {data}")

asyncio.run(test())
