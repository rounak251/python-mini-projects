import socket
import threading
import sys

# Configuration (must match server)
HOST = '127.0.0.1'  # Change to server's IP if running on different machine
PORT = 5555

def receive_messages(client_socket):
    """Thread that continuously listens for broadcast messages"""
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            print(message.decode('utf-8'), end='')
        except:
            break

# ==================== MAIN CLIENT ====================
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((HOST, PORT))
    print("✅ Connected to Real-Time Server! Type messages below.\n")
except:
    print("❌ Could not connect to server. Make sure server.py is running.")
    sys.exit(1)

# Start background thread for receiving messages (real-time)
receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
receive_thread.daemon = True
receive_thread.start()

# Main loop for sending messages
try:
    while True:
        message = input("")
        if message.lower() in ['exit', 'quit']:
            break
        if message.strip():  # Only send non-empty messages
            client_socket.send(message.encode('utf-8'))
except KeyboardInterrupt:
    print("\n👋 Disconnecting...")
except:
    pass
finally:
    client_socket.close()
    print("Client closed.")