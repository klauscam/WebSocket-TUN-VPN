import asyncio
import websockets

# A dictionary to map device IPs to their WebSocket connections
clients = {}


async def handler(websocket):
    """
    WebSocket server to handle immediate forwarding of packets.
    """
    device_ip = None

    try:
        async for message in websocket:
            #print(message)
            if message.startswith("register:"):
                # Register a client
                device_ip = message.split(":", 1)[1]
                clients[device_ip] = websocket
                print(f"Device registered: {device_ip}")
                await websocket.send(f"registered:{device_ip}")

            elif message.startswith("tx:"):
                # Forward the packet to the destination
                _, dest_ip, packet_hex = message.split(":", 2)
                if dest_ip in clients:
                    try:
                        await clients[dest_ip].send(f"rx:{packet_hex}")
                    #    print(f"Packet from {device_ip} sent to {dest_ip}")
                    except Exception as e:
                        print(f"Error forwarding packet to {dest_ip}: {e}")
                else:
                    print(f"Destination {dest_ip} not connected. Dropping packet.")

    except websockets.ConnectionClosed:
        print(f"Device {device_ip} disconnected.")
        if device_ip in clients:
            del clients[device_ip]


# Start the WebSocket server
#start_server = websockets.serve(handler, "0.0.0.0", 5000
async def main():
    # Start the WebSocket server
    start_server = websockets.serve(handler, "0.0.0.0", 80, ping_interval=10, ping_timeout=5)
    async with start_server:
        print("WebSocket server started on ws://0.0.0.0:80")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
