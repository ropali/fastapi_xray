import json
import socket
import time
import uuid
from typing import Callable

from commons.logger import get_logger
from fastapi import Request, Response

logger = get_logger(__name__)

HOST = "0.0.0.0"  # The server's hostname or IP address
OUT_PORT = 8989  # The port used by the server to send data


async def inspector(request: Request, call_next: Callable) -> Response:
    logger.info("Collecting debug info.....")
    # Collect debug information before handling the request
    start_time = time.perf_counter()
    response = await call_next(request)
    end_time = time.perf_counter()
    # Collect debug information after handling the request

    debug_info = {
        "request_id": str(uuid.uuid4()),
        "time": start_time - end_time,
        "base_url": str(request.base_url),
        "query_params": dict(request.query_params),
        "path_params": dict(request.path_params),
        "path": str(request.url.path),
        "status_code": response.status_code,
        "method": request.method,
        "cookies": dict(request.cookies),
        "headers": dict(request.headers),
    }
    # Add, session, auth & user details as well "json_body": await response.json(),

    # Send the response data to the server
    try:
        # Create a socket object for sending data
        out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        out_sock.connect((HOST, OUT_PORT))
        out_sock.sendall(json.dumps(debug_info).encode("utf-8"))
        logger.info("sent data to receiver")
    except Exception as e:
        logger.error(f"Exception: {e}")
        logger.exception(e)

    return response
