import socket
import time
import threading
import subprocess

# Apply packet loss using tc
def apply_packet_loss():
    try:
        # Introduce 20% packet loss on the loopback interface
        subprocess.run(["sudo", "tc", "qdisc", "add", "dev", "lo", "root", "netem", "loss", "20%"], check=True)
        print("Applied packet loss of 20% on loopback interface")
    except subprocess.CalledProcessError:
        print("Failed to apply tc rules. Ensure you have sudo privileges.")

# Remove packet loss rule
def remove_packet_loss():
    try:
        subprocess.run(["sudo", "tc", "qdisc", "del", "dev", "lo", "root"], check=True)
        print("Removed packet loss on loopback interface")
    except subprocess.CalledProcessError:
        print("Failed to remove tc rules. Ensure you have sudo privileges.")

# Server function
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 9999))
    server.listen(1)
    print("Server is listening on 127.0.0.1:9999")
    conn, addr = server.accept()
    print(f"Connection accepted from {addr}")

    # Set a small receive buffer to create backpressure
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)

    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"Server received: {data.decode()}")
    conn.close()
    server.close()

# Client function
def start_client():
    time.sleep(1)  # Ensure the server is up
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 9999))
    for i in range(5):
        client.sendall(f"Message {i}".encode())
        time.sleep(0.1)  # Simulate normal communication

    # Induce retransmissions by halting ACKs
    print("Client intentionally stopping read operations to induce retransmissions...")
    client.shutdown(socket.SHUT_RD)
    time.sleep(2)  # Keep the connection alive to simulate packet loss
    client.close()

# Main function
def main():
    # Apply packet loss
    apply_packet_loss()

    # Start server and client threads
    server_thread = threading.Thread(target=start_server)
    client_thread = threading.Thread(target=start_client)

    server_thread.start()
    client_thread.start()

    server_thread.join()
    client_thread.join()

    # Clean up packet loss
    remove_packet_loss()

if __name__ == "__main__":
    main()

