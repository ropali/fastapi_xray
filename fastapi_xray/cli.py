import multiprocessing
from multiprocessing import Process

import typer
from typer import Argument

from fastapi_xray.commons.logger import get_logger
from fastapi_xray.server import start_server
from fastapi_xray.ui.app import render_ui

app = typer.Typer()

logger = get_logger()


@app.command()
def run(
    host: str = Argument(  # noqa :B008
        "0.0.0.0",
        help="Host where server will listen for incoming data for UI",
    ),
    port: int = Argument(  # noqa :B008
        8989, help="Port where server will listen for incoming data for UI"
    ),
    disable_log: bool = Argument(  # noqa :B008
        True, help="Generate logs for debugging."
    ),
):
    """Runs the UI server and X-Ray server."""

    logger.disabled = disable_log  # only for internal debugging
    shared_queue = multiprocessing.Queue()

    p1 = Process(target=start_server, args=(shared_queue, host, port))
    p1.daemon = True
    p1.start()

    render_ui(shared_queue)


if __name__ == "__main__":
    app()
