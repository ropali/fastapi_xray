from multiprocessing import Queue

from fastapi_xray.commons.logger import get_logger
from fastapi_xray.server.receiver import Receiver

logger = get_logger()


def start_server(shared_queue: Queue, host: str, port: int):
    rec = Receiver(host, port, shared_queue)
    try:
        logger.info("server started")
        rec.start()
    except Exception as e:
        rec.stop()
        logger.error(f"Server crashed: {e}")
