import socket
from contextlib import contextmanager

class PortPool:
    def __init__(self, start_port, end_port):
        self.available_ports = set(range(start_port, end_port + 1))
        self.allocated_ports = set()

    def allocate(self):
        if not self.available_ports:
            raise Exception("No ports available.")
        port = self.available_ports.pop()
        self.allocated_ports.add(port)
        return port

    def release(self, port):
        if port in self.allocated_ports:
            self.allocated_ports.remove(port)
            self.available_ports.add(port)
        else:
            raise ValueError(f"Port {port} was not allocated.")

    def __enter__(self):
        return self.allocate()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release(self.allocated_ports.pop())

# Example usage
port_pool = PortPool(8000, 8100)

# Allocate a port
port = port_pool.allocate()
print(f"Allocated port: {port}")

# Release the port when done
port_pool.release(port)

# Using with statement for automatic allocation and release
with port_pool as port:
    print(f"Using port: {port}")