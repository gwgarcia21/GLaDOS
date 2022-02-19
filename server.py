import websockets
import asyncio
import interpreter
from threading import Thread

PORT = 7890

print("Server listening on port: " + str(PORT))

connected = set()

async def echo(websocket, path):
    print("A client just connected.")
    connected.add(websocket)
    try:
        async for message in websocket:
            #interpreter.main(message)
            Thread(target=interpreter.main(message)).start()
            print("Received from client: " + message)
            await websocket.send("Response: " + message)
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected." + str(e))
    finally:
        connected.remove(websocket)
    #print(len(connected))

start_server = websockets.serve(echo, "localhost", PORT)
#start_server = websockets.serve(echo, "192.168.5.116", PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()