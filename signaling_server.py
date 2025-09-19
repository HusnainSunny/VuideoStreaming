import os
import asyncio
import websockets
import json

# Use the port provided by the environment variable or default to 8765.
port = int(os.environ.get("PORT", 8765))

rooms = {}

async def signaling_handler(websocket, path=None):
    try:
        async for message in websocket:
            data = json.loads(message)
            room = data.get("room")
            if not room:
                print("Message missing 'room':", data)
                continue

            # Add the connection to the room.
            if room not in rooms:
                rooms[room] = set()
            rooms[room].add(websocket)
            print(f"Message from {websocket.remote_address} in room '{room}':", data)

            # Broadcast the message to all other clients in the same room.
            for client in list(rooms[room]):
                if client != websocket:
                    try:
                        await client.send(message)
                    except websockets.exceptions.ConnectionClosed:
                        print("Attempted to send to a closed connection.")
    except websockets.exceptions.ConnectionClosed:
        print(f"Connection closed: {websocket.remote_address}")
    finally:
        # Remove the connection from all rooms.
        for r in list(rooms.keys()):
            if websocket in rooms[r]:
                rooms[r].remove(websocket)
                if not rooms[r]:
                    del rooms[r]

async def process_request(path, request_headers):
    # This callback handles HTTP requests before the WebSocket handshake.
    # If the path is "/healthz", return a simple HTTP 200 OK response.
    if path == "/healthz":
        return (200, [("Content-Type", "text/plain")], b"OK")
    # Otherwise, proceed with the normal WebSocket handshake.
    return None

async def main():
    server = await websockets.serve(
        signaling_handler,
        "0.0.0.0",
        port,
        process_request=process_request  # Enables HTTP requests to /healthz.
    )
    print(f"Signaling server started on ws://0.0.0.0:{port}")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
