import json
import os
from multiprocessing import Queue

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Footer, ListView

from fastapi_xray.commons.logger import get_logger
from fastapi_xray.schemas import APIRequest
from fastapi_xray.ui.components.panels import LeftPanel, RightPanel
from fastapi_xray.ui.components.widgets.list import LabelItem
from fastapi_xray.ui.components.widgets.text import TextBox

logger = get_logger()


class MainApp(App):
    """FastAPI debug app."""

    selected_request = reactive(None)

    def __init__(self, queue: Queue, **kwargs):
        super().__init__(**kwargs)
        self.queue = queue
        self.requests = {}

    CSS_PATH = "main.css"
    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("c", "clear_all", "Clear All"),
    ]

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Container(
            TextBox("", "[b]✘ FastAPI X-Ray ✘[/]", False, "center"),
            id="app_title",
        )
        yield LeftPanel()
        yield RightPanel()

        yield Footer()

    def on_mount(self) -> None:
        self.set_interval(
            interval=os.environ.get("REFRESH_INTERVAL", 1), callback=self.action_refresh
        )

    async def action_refresh(self):
        self.poll()

    async def action_clear_all(self):
        """An action to clear all requests."""
        await self.query_one("#left_panel_list_view").clear()
        self.query_one(RightPanel).selected_request = None
        self.requests = {}

    def on_list_view_selected(self, event: ListView.Selected):
        request = self.requests.get(event.item.value)
        self.query_one(RightPanel).selected_request = request
        logger.info(
            f"Selected request: <{request.request_id}> {request.request.method} {request.request.path}"
        )

    async def add_new_request(self, new_request: APIRequest):
        widget = self.query_one("#left_panel_list_view")
        request = new_request.request
        logger.info(
            f"New request added: <{new_request.request_id}> {request.method} {request.path}"
        )
        widget.prepend(
            LabelItem(
                label=f"{len(self.requests) + 1}. [b][{request.method}][/] {request.path}",
                value=str(new_request.request_id),
                classes="request_item",
            )
        )

        self.requests[new_request.request_id] = new_request

    @work(exclusive=True)
    async def poll(self):
        import queue

        try:
            result = self.queue.get_nowait()
            if not result:
                return

            result = json.loads(result)
            api_request = APIRequest(**result)
            await self.add_new_request(api_request)

        except queue.Empty:
            # handle case where the queue is empty
            pass
        except json.JSONDecodeError:
            # handle case where the received data is not valid JSON
            logger.error("Received data is not valid JSON")
        except Exception as e:
            # handle any other exceptions
            logger.error(f"Error while polling queue: {e}")


def render_ui(shared_queue: Queue):
    app = MainApp(watch_css=True, queue=shared_queue)
    app.run()
