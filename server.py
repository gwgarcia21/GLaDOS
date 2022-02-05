import websockets
import asyncio
import glados

PORT = 7890

print("Server listening on port: " + str(PORT))

connected = set()

async def echo(websocket, path):
    print("A client just connected.")
    connected.add(websocket)
    glados.main()
    try:
        async for message in websocket:
            print("Received from client: " + message)
            await websocket.send("Response: " + message)
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected.")
    finally:
        connected.remove(websocket)

start_server = websockets.serve(echo, "localhost", PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()