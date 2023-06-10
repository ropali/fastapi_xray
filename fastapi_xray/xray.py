import json
import os
import socket
import time
import uuid
from typing import Callable, Dict, Union

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from fastapi_xray.commons.logger import get_logger

logger = get_logger()

HOST = os.environ.get("XRAY_HOST", "0.0.0.0")  # The server's hostname or IP address
OUT_PORT = int(
    os.environ.get("XRAY_PORT", 8989)
)  # The port used by the server to receive data for display


def start_xray(
    app: FastAPI,
    sqlalchemy_engine: "Engine" = None,  # noqa :F821
    host: str = "0.0.0.0",
    port: int = 8989,
) -> None:
    """Starts X-Ray integration for FastAPI.

    Args:
        app (FastAPI): The FastAPI application instance.
        sqlalchemy_engine (Engine, optional): The SQLAlchemy engine instance. Defaults to None.
        host (str, optional): The UI host listener address where data will be sent. Defaults to "0.0.0.0".
        port (int, optional): The UI port listener address where data will be sent. Defaults to 8899.

    Returns:
        None

    This function sets up the necessary configurations and middleware to integrate X-Ray
    for FastAPI applications. It tracks and logs SQL queries along with their execution times.
    If the `sqlalchemy_engine` is provided, it sets up event listeners for tracking SQLAlchemy queries.

    Additionally, it includes exception handlers for capturing HTTP exceptions and request validation errors,
    ensuring they can be caught and handled by the middleware.
    """
    global HOST
    global OUT_PORT

    HOST = host
    OUT_PORT = port

    app.state.queries = []
    app.state.error = None

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
        # Maintain the queries state so that it can be accessed in the middleware
        app.state.queries.append(sql_data)

    if sqlalchemy_engine:
        from sqlalchemy import event

        event.listen(sqlalchemy_engine, "before_cursor_execute", set_query_start_timer)
        event.listen(sqlalchemy_engine, "after_cursor_execute", after_cursor_execute)

    @app.exception_handler(HTTPException)
    @app.exception_handler(RequestValidationError)
    async def __exception_handler(
        request: Request, exc: Union[HTTPException, RequestValidationError]
    ) -> None:
        """This is just workaround to capture HTTPException, RequestValidationError.
        These exceptions basically handled error which means FastAPI handles specially.
        it inside the http middleware, so re-raise error from so that
        it can be caught in the middleware
        """
        raise exc

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
        err = response.body.decode("utf-8") if hasattr(response, "body") else ""

        try:
            err = json.loads(err)
        except json.JSONDecodeError:
            pass

        response_body["error"] = {
            "message": err,
        }

    sql_queries = request.state.queries

    debug_info["request"] = request_body
    debug_info["response"] = response_body
    debug_info["sql"] = sql_queries

    return debug_info


async def set_body(request: Request, body: bytes):
    async def receive():
        return {"type": "http.request", "body": body}

    request._receive = receive


async def get_body(request: Request) -> bytes:
    body = await request.body()
    await set_body(request, body)
    return body


async def inspector(request: Request, call_next: Callable) -> Response:
    body = None
    body = await extract_body(body, request)

    start_time = time.perf_counter()
    try:
        response = await call_next(request)
    except HTTPException as htex:
        response = JSONResponse(status_code=htex.status_code, content=htex.detail)
    except RequestValidationError as re:
        response = JSONResponse(status_code=422, content=re.errors())
    except Exception as e:
        response = JSONResponse(status_code=500, content=str(e))
    finally:
        end_time = time.perf_counter()
        elapsed_time = (end_time - start_time) * 1000
        elapsed_time = f"{elapsed_time:.4f}"

    debug_info = build_debug_info(request, response)

    debug_info["elapsed_time"] = elapsed_time

    debug_info["request"]["body"] = body

    try:
        send_debug_info(debug_info)
    except Exception as e:
        logger.error(f"Exception: {e}")
    finally:
        request.state.queries.clear()

    return response


async def extract_body(body: bytes, request: Request) -> bytes:
    if request.headers.get("Content-Type") == "application/json":
        # This is workaround to get request body in the middleware
        # https://stackoverflow.com/a/74778485/6832201
        await set_body(request, await request.body())
        body = await request.json()
    elif request.headers.get("Content-Type") == "application/x-www-form-urlencoded":
        await set_body(request, await request.body())
        form_data = await form_to_json(request)
        return form_data
    return body

async def form_to_json(request: Request):
        form_data = await request.form()
        form_items = form_data.items()
        form_body = {}
        for item in form_items:
            form_body[item[0]] = item[1]
        return form_body


def send_debug_info(debug_info: Dict):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as out_sock:
        out_sock.connect((HOST, OUT_PORT))
        out_sock.sendall(json.dumps(debug_info).encode("utf-8"))
        logger.info("Sent data to receiver")
