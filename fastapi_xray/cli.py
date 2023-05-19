import multiprocessing
from multiprocessing import Process

import typer
from server import start_server
from ui.app import render_ui

app = typer.Typer()


@app.command()
def run(host: str = "0.0.0.0", port: int = 8989):
    shared_queue = multiprocessing.Queue()

    p1 = Process(target=start_server, args=(shared_queue, host, port))
    p1.daemon = True
    p1.start()

    render_ui(shared_queue)


if __name__ == "__main__":
    app()
