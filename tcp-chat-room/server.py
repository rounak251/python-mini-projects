import socket
import threading

# Configuration
HOST = '0.0.0.0'      # Listen on all interfaces
PORT = 5555            # Real-time chat port
clients = []           # List of active client sockets

def broadcast(message, sender_socket=None):
    """Send message to ALL connected clients except the sender"""
    for client in clients[:]:  # Copy list to avoid modification during iteration
        if client != sender_socket:
            try:
                client.send(message)
            except:
                # Client disconnected unexpectedly
                clients.remove(client)

def handle_client(client_socket, addr):
    """Handle messages from one client in its own thread (real-time)"""
    print(f"[+] New client connected: {addr}")
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break  # Client disconnected cleanly
            # Prefix with sender address for clarity
            formatted = f"[{addr[0]}:{addr[1]}] {message.decode('utf-8')}\n".encode()
            broadcast(formatted, client_socket)
        except:
            break
    
    # Cleanup on disconnect
    if client_socket in clients:
        clients.remove(client_socket)
    client_socket.close()
    print(f"[-] Client disconnected: {addr}")

# ==================== MAIN SERVER ====================
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(100)  # Can accept up to 100 pending connections

print(f"🚀 Real-Time TCP Server started on {HOST}:{PORT}")
print("Waiting for multiple clients to connect...\n")

while True:
    client_socket, addr = server.accept()
    clients.append(client_socket)
    
    # Each client gets its own thread → true concurrency & real-time handling
    thread = threading.Thread(target=handle_client, args=(client_socket, addr))
    thread.daemon = True
    thread.start()