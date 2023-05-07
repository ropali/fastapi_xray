import json
import socket
import time
import uuid
from typing import Callable, Dict

from fastapi import FastAPI, Request, Response

from debug_tool.commons.logger import get_logger

logger = get_logger(__name__)

HOST = "0.0.0.0"  # The server's hostname or IP address
OUT_PORT = 8989  # The port used by the server to send data


def start_inspector(app: FastAPI, sqlalchemy_engine: "Engine" = None) -> None:  # noqa
    app.state.queries = []

    def set_query_start_timer(
        conn, cursor, statement, parameters, context, executemany
    ):
        conn.info["query_start"] = time.perf_counter()

    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        formatted_query = statement.replace("?", "{}").format(*parameters)
        elapsed_time = (time.perf_counter() - conn.info["query_start"]) * 1000
        sql_data = {
            "statement": formatted_query,
            "execution_time": f"{elapsed_time:.4f}",
        }
        app.state.queries.append(sql_data)

    if sqlalchemy_engine:
        from sqlalchemy import event

        event.listen(sqlalchemy_engine, "before_cursor_execute", set_query_start_timer)
        event.listen(sqlalchemy_engine, "after_cursor_execute", after_cursor_execute)

    @app.middleware("http")
    async def inspector_wrapper(request: Request, call_next: Callable) -> Response:
        request.state.queries = app.state.queries
        return await inspector(request, call_next)


def build_debug_info(request: Request, response: Response) -> Dict:
    debug_info = {
        "request_id": str(uuid.uuid4()),
    }

    request_body = {
        "base_url": str(request.base_url),
        "query_params": dict(request.query_params),
        "path_params": dict(request.path_params),
        "path": str(request.url.path),
        "status_code": response.status_code,
        "method": request.method,
        "cookies": dict(request.cookies),
        "headers": dict(request.headers),
    }

    response_body = {
        "headers": dict(response.headers) if hasattr(response, "headers") else None,
    }

    if response.status_code >= 400:
        response_body["error"] = True
        response_body["error_message"] = "Error Occurred"

    sql_queries = request.state.queries

    debug_info["request"] = request_body
    debug_info["response"] = response_body
    debug_info["sql"] = sql_queries

    return debug_info


async def inspector(request: Request, call_next: Callable) -> Response:
    elapsed_time = "N/A"

    try:
        start_time = time.perf_counter()
        response = await call_next(request)
        end_time = time.perf_counter()
        elapsed_time = (end_time - start_time) * 1000
        elapsed_time = f"{elapsed_time:.4f}"
    except Exception as e:
        response = Response(status_code=500, content=str(e))

    debug_info = build_debug_info(request, response)

    debug_info["elapsed_time"] = elapsed_time

    try:
        out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        out_sock.connect((HOST, OUT_PORT))
        out_sock.sendall(json.dumps(debug_info).encode("utf-8"))
        logger.info("Sent data to receiver")
    except Exception as e:
        logger.error(f"Exception: {e}")
    finally:
        request.state.queries.clear()

    return response
