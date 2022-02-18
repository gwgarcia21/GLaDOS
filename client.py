import websockets
import asyncio
import json

message = {
  "agent": "GLaDOS",
  "text": "Hello, indeed it works!",
  "type": "say"
}

async def listen():
    url = "ws://127.0.0.1:7890"

    async with websockets.connect(url) as ws:
        #await ws.send("Hello server!")
        obj = json.dumps(message)
        await ws.send(obj)
        while True:
            msg = await ws.recv()
            print(msg)

asyncio.get_event_loop().run_until_complete(listen())