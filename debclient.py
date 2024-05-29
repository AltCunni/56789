import socket
import sys

# Configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 12345


def test_server_connection(host, port):
    try:
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the server
        server_address = (host, port)
        print(f"Connecting to {host} on port {port}")
        sock.connect(server_address)

        # Send data
        message = 'test'
        print(f"Sending: {message}")
        sock.sendall(message.encode())

        # Look for the response
        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print(f"Received: {data.decode()}")

        return True
    except Exception as e:
        print(f"Warning: The server at {host}:{port} is not working correctly.")
        print(f"Error: {e}")
        return False
    finally:

        sock.close()


# Test the server
if not test_server_connection(SERVER_HOST, SERVER_PORT):
    sys.exit(1)