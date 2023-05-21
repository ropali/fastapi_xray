import multiprocessing
from multiprocessing import Process

import typer
from commons.logger import get_logger
from server import start_server
from ui.app import render_ui

app = typer.Typer()

logger = get_logger()


@app.command()
def run(host: str = "0.0.0.0", port: int = 8989, disable_log: bool = True):
    """Runs the UI server and X-Ray server."""

    logger.disabled = disable_log  # only for internal debugging
    shared_queue = multiprocessing.Queue()

    p1 = Process(target=start_server, args=(shared_queue, host, port))
    p1.daemon = True
    p1.start()

    render_ui(shared_queue)


if __name__ == "__main__":
    app()
