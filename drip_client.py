###
### drip_client.py
###

import socket
import time

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000

def run_drip_client():
    print("Starting drip client...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    
    # Consume the welcome message
    buffer = b""
    while b"\n" not in buffer:
        buffer += sock.recv(1024)
    print("Connected. Server greeting received.")

    # The command we want to send, including the newline
    command = b"ADD 1 2\n"
    
    print("Dripping command one byte at a time:")
    for byte in command:
        # Send a single byte
        sock.sendall(bytes([byte]))
        print(f"Sent: {repr(bytes([byte]))}")
        time.sleep(0.3)
        
    print("Command completely sent. Waiting for response...")
    
    # Read the response
    response = sock.recv(1024)
    print(f"Server replied: {response.decode('ascii').strip()}")
    
    sock.close()

if __name__ == "__main__":
    run_drip_client()