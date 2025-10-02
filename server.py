import socket,time

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 8500        # Port to listen on (non-privileged ports are > 1023)
Run = True

def stop():
	Run=False


def start():
    """Starts a simple TCP echo server on localhost:8500."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Listening on {HOST}:{PORT}")

        while (Run == True):
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while (Run == True):
                    data = conn.recv(1024)  # Receive up to 1024 bytes
                    if not data:
                        break  # No more data from client
                    print(f"Received from {addr}: {data.decode()}")
                    #conn.sendall(data)  # Echo back the received data
            time.sleep(3)

if __name__ == "__main__":
    start()