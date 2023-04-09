import multiprocessing
import os
import socket
from multiprocessing import Process, Queue

from commons.logger import get_logger
from cli_app.ui import render_ui
from server.receiver import Receiver

logger = get_logger(__name__)

HOST = '0.0.0.0'  # The server's hostname or IP address
PORT = 8989  # The port used by the server


def start_server(shared_queue: Queue):
    receiver = Receiver(HOST, PORT, shared_queue)
    try:
        logger.info(f"server started")
        receiver.start()
    except Exception as e:
        receiver.stop()
        # Restart the program if it crashes
        os.execv(__file__, os.sys.argv)


def start_app():
    sharedQueue = multiprocessing.Queue()

    p1 = Process(target=start_server, args=(sharedQueue,))
    p1.daemon = True
    p1.start()

    render_ui(sharedQueue)


if __name__ == '__main__':
    start_app()
