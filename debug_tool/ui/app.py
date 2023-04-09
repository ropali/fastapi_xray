import json
import os
from multiprocessing import Queue

from commons.logger import get_logger
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Footer, Label, ListItem
from ui.components.panels import LeftPanel, RightPanel
from ui.components.widgets import TextBox

logger = get_logger(__name__)


class DebugApp(App):
    """FastAPI debug app."""

    selected_request = reactive({})

    def __init__(self, queue: Queue, **kwargs):
        super().__init__(**kwargs)
        self.queue = queue

    CSS_PATH = "main.css"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("r", "refresh", "Refresh"),
        ("c", "clear_all", "Clear All"),
    ]

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Container(
            TextBox("FastAPI Debug", "FastAPI Inspector", False, "center"),
            id="app_title",
        )
        yield LeftPanel(items=[])
        yield RightPanel(self.selected_request)

        yield Footer()

    def on_mount(self) -> None:
        self.set_interval(
            interval=os.environ.get("REFRESH_INTERVAL", 2), callback=self.action_refresh
        )

    async def action_refresh(self):
        self.poll()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    async def action_clear_all(self):
        """An action to clear all requests."""
        await self.query_one("#left_panel_list_view").clear()

    @work(exclusive=True)
    async def poll(self):
        import queue

        logger.info("Started polling queue")
        widget = self.query_one("#left_panel_list_view")
        try:

            result = self.queue.get_nowait()

            if not result:
                return

            result = json.loads(result)
            logger.info(
                f"Received data from queue for request ID: {result.get('request_id')}"
            )
            await widget.append(
                ListItem(Label(str(result.get("request_id")), classes="request_item"))
            )

        except queue.Empty:
            # handle case where the queue is empty
            logger.warning("Queue is empty")
        except json.JSONDecodeError:
            # handle case where the received data is not valid JSON
            logger.error("Received data is not valid JSON")
        except Exception as e:
            # handle any other exceptions
            logger.error(f"Error while polling queue: {e}")


def render_ui(shared_queue: Queue):
    app = DebugApp(watch_css=True, queue=shared_queue)
    app.run()
