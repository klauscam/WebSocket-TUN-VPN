# WebSocket TUN VPN

A minimal Layer-3 VPN tunnel implemented in Python using:

-   Linux **TUN** interfaces
-   **WebSockets** for transport
-   `asyncio` for concurrency

This project creates a simple IP-over-WebSocket tunnel that allows
multiple clients to exchange raw IP packets through a central WebSocket
relay server.

------------------------------------------------------------------------

## ✨ Features

-   Layer-3 IP tunneling (TUN device)
-   Asynchronous packet forwarding
-   Simple client registration by IP
-   Direct packet routing between connected peers
-   Minimal dependencies
-   Easy to understand and extend

------------------------------------------------------------------------

## 🧠 How It Works

1.  Each client creates a Linux **TUN interface**.
2.  Outgoing IP packets are read from the TUN device.
3.  Packets are serialized (hex) and sent to the WebSocket server.
4.  The server forwards packets based on destination IP.
5.  The receiving client writes packets back into its TUN device.

```{=html}
Client A (10.0.0.2)
          │
          │  WebSocket
          ▼
        Server
          ▲
          │  WebSocket
          │
Client B (10.0.0.3)
```

The server acts purely as a packet forwarder. It does not inspect or
modify IP payloads.

------------------------------------------------------------------------

## 📦 Requirements

-   Linux (TUN/TAP support required)
-   Python 3.9+
-   Root privileges (required for TUN interface)
-   websockets library

Install dependency:

``` bash
pip install websockets
```

------------------------------------------------------------------------

## 🚀 Setup & Usage

### 1️⃣ Start the Server

``` bash
sudo python server.py
```

The server listens on:

    ```
    ws://0.0.0.0:80
    ```

You may change the port if needed.

------------------------------------------------------------------------

### 2️⃣ Configure Client

Edit in `client.py`:

``` {=python}
SERVER_URL = "ws://<server-ip>:80"
my_ip = "10.0.0.X"
```

Each client must have a **unique IP address** in the same subnet.

------------------------------------------------------------------------

### 3️⃣ Configure TUN Interface

You must configure the TUN interface manually (recommended).

Example:

``` bash
sudo ip tuntap add dev tun0 mode tun
sudo ip addr add 10.0.0.2/24 dev tun0
sudo ip link set tun0 up
```

Repeat on the other client with a different IP.

------------------------------------------------------------------------

### 4️⃣ Run the Client

``` bash
sudo python client.py
```

Once connected, clients can ping each other:

``` bash
ping 10.0.0.3
```

------------------------------------------------------------------------

## 🔐 Important Security Notice

⚠️ This project is a **proof-of-concept** and does **NOT** provide:

-   Encryption
-   Authentication
-   Authorization
-   Replay protection
-   Traffic obfuscation
-   DoS protection

Do **NOT** expose this server directly to the public internet.

For production usage, consider:

-   Running behind Nginx with TLS
-   Adding authentication tokens
-   Using WSS (TLS)
-   Adding encryption at packet level
-   Implementing client verification

------------------------------------------------------------------------

## 🏗 Architecture

### Client

-   Opens `/dev/net/tun`
-   Reads packets using `select`
-   Sends packets as:

```{=html}
<!-- -->
```
    tx:<destination_ip>:<hex_packet>

-   Receives packets as:

```{=html}
<!-- -->
```
    rx:<hex_packet>

------------------------------------------------------------------------

### Server

Maintains a dictionary:

``` python
clients = {
    "10.0.0.2": websocket,
    "10.0.0.3": websocket,
}
```

Forwards packets immediately to destination if connected.

Drops packets if destination is offline.

------------------------------------------------------------------------

## ⚙️ Known Limitations

-   No NAT traversal
-   No automatic routing configuration
-   No multi-hop routing
-   No MTU management
-   No fragmentation handling
-   No reconnection state sync
-   Single relay node architecture

------------------------------------------------------------------------

## 📚 Educational Purpose

This project is designed to demonstrate:

-   Linux TUN interface usage
-   Raw IP packet handling
-   Async IO networking
-   Building simple VPN architectures
-   WebSocket-based tunneling

------------------------------------------------------------------------

## ⚠️ Disclaimer

This software is provided for educational and research purposes only.\
The author is not responsible for misuse or damages caused by this
software.
