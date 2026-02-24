import os
import fcntl
import struct
import asyncio
import websockets
from select import select

SERVER_URL = "ws://<serverip>:80"

TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000


def setup_tun_interface(tun_name, my_ip):
    """
    Set up the TUN device.
    """

#    os.system(f"ip tuntap del dev {tun_name} mode tun")
#    os.system(f"ip tuntap add dev {tun_name} mode tun")
#    os.system(f"ip addr add {my_ip}/24 dev {tun_name}")
#    os.system(f"ip link set {tun_name} up")

    tun_fd = os.open("/dev/net/tun", os.O_RDWR)
    ifr = struct.pack('16sH', tun_name.encode('utf-8'), IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun_fd, TUNSETIFF, ifr)
    return tun_fd


def read_from_tun(tun_fd):
    """
    Read a packet from the TUN device.
    """
    readable, _, _ = select([tun_fd], [], [], 0)
    if tun_fd in readable:
        return os.read(tun_fd, 1500)
    return None


def write_to_tun(tun_fd, data):
    """
    Write a packet to the TUN device.
    """
    os.write(tun_fd, data)


async def tx_packets(tun_fd, websocket):
    """
    Transmit packets from the TUN device to the server.
    """
    while True:
        packet = read_from_tun(tun_fd)
        if packet:
            dest_ip = ".".join(str(b) for b in packet[16:20])
            try:
                await websocket.send(f"tx:{dest_ip}:{packet.hex()}")
#                print(f"Sent packet to {dest_ip}")
            except Exception as e:
                print(f"Error sending packet: {e}")
        await asyncio.sleep(0)  # Avoid CPU spinning


async def rx_packets(tun_fd, websocket):
    """
    Receive packets from the server and write them to the TUN device.
    """
    while True:
        try:
            message = await websocket.recv()
            if message.startswith("rx:"):
                _, packet_hex = message.split(":", 1)
                if packet_hex:  # Ensure the packet_hex is not empty
                    packet = bytes.fromhex(packet_hex)
                    write_to_tun(tun_fd, packet)
#                    print(f"Received packet and wrote to TUN: {packet_hex}")
                else:
                    print("No packet received from server (empty `rx:`)")
        except websockets.ConnectionClosed:
            print("Connection closed, reconnecting...")
            break
        except Exception as e:
            print(f"Error receiving packet: {e}")


async def vpn_client(tun_fd, my_ip):
    """
    WebSocket client handling TX and RX in separate tasks.
    """
    while True:
        try:
            async with websockets.connect(SERVER_URL) as websocket:
                # Register the device
                await websocket.send(f"register:{my_ip}")
                print(f"Registered device {my_ip} with server")

                # Run TX and RX tasks concurrently
                tx_task = asyncio.create_task(tx_packets(tun_fd, websocket))
                rx_task = asyncio.create_task(rx_packets(tun_fd, websocket))

                await asyncio.gather(tx_task, rx_task)
        except Exception as e:
            print(f"Connection error: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)


def main():
    tun_name = "tun0"
    my_ip = "10.0.0.3"

    # Set up the TUN interface
    tun_fd = setup_tun_interface(tun_name, my_ip)

    # Run the WebSocket client
    asyncio.run(vpn_client(tun_fd, my_ip))


if __name__ == "__main__":
    main()
