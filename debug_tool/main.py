import datetime
import json
import socket
import os
from cli_app.ui import render_ui

HOST = '0.0.0.0'  # The server's hostname or IP address
PORT = 8989  # The port used by the server

request_data = []


def start_server():
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Started debug server on {HOST}:{PORT}")
        # Bind the socket to a specific address and port
        s.bind((HOST, PORT))

        while True:
            try:
                # Listen for incoming connections
                s.listen()

                # Wait for a client to connect
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)

                    # Receive data from the client
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        # Process the data received from the client
                        print(
                            f"-------------------------Received[{datetime.datetime.now()}]---------------------------------")
                        print(json.loads(data.decode('utf-8')))
                        request_data.append(json.loads(data.decode('utf-8')))
                        print(f"-------------------------Received[{datetime.datetime.now()}]---------------------------------")
            except Exception as e:
                print("An error occurred:", e)
                # Restart the program if it crashes
                os.execv(__file__, os.sys.argv)


if __name__ == '__main__':
    render_ui(request_data)
    # start_server()

