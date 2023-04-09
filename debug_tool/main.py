import multiprocessing
import os
from multiprocessing import Process, Queue

from commons.logger import get_logger
from server.receiver import Receiver
from ui.app import render_ui

logger = get_logger(__name__)

HOST = "0.0.0.0"  # The server's hostname or IP address
PORT = 8989  # The port used by the server


def start_server(shared_queue: Queue):
    receiver = Receiver(HOST, PORT, shared_queue)
    try:
        logger.info("server started")
        receiver.start()
    except Exception as e:
        receiver.stop()
        logger.error(f"Server crashed: {e}")
        # Restart the program if it crashes
        logger.info("Restarting server")
        os.execv(__file__, os.sys.argv)


def start_app():
    shared_queue = multiprocessing.Queue()

    p1 = Process(target=start_server, args=(shared_queue,))
    p1.daemon = True
    p1.start()

    render_ui(shared_queue)


if __name__ == "__main__":
    start_app()
