import socket
from multiprocessing import Queue

from fastapi_xray.commons.logger import get_logger

logger = get_logger()


class Receiver:
    def __init__(self, host: str, port: int, shared_queue: Queue):
        self.host = host
        self.port = port
        self.sock = None
        self.shared_queue = shared_queue

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info(f"Started debug server on {self.host}:{self.port}")
        # Bind the socket to a specific address and port
        self.sock.bind((self.host, self.port))

        while True:
            try:
                # Listen for incoming connections
                self.sock.listen()

                # Wait for a client to connect
                conn, addr = self.sock.accept()
                with conn:
                    # Receive data from the client
                    data = b""
                    while True:
                        chunk = conn.recv(1024)
                        if chunk:
                            data += chunk
                        else:
                            break
                    # Process the data received from the client
                    decoded_data = data.decode("utf-8")
                    logger.info("Received data from client")
                    self.shared_queue.put(decoded_data)
                    logger.info("Data sent to the shared queue.")

            except Exception as e:
                self.stop()
                logger.error(
                    "An error occurred while handling the connection",
                )
                logger.exception(e)

    def stop(self):
        self.sock.close()
