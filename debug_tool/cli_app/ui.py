import uuid
from time import monotonic
from typing import Dict, List

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Header, Footer, Static, ListView, ListItem, Label


class LeftPanel(Widget):
    items = reactive([])

    def __init__(self, items: List[Dict], **kwargs):
        super().__init__(**kwargs)
        self.items = [ListItem(Label(item.get("title"), classes="request_item")) for item in items]

    def compose(self) -> ComposeResult:

        yield Static(
            "All Request",
            expand=True,
            id="left_panel_header"
        )

        yield ListView(
            *self.items,
            initial_index=None,
            id="left_panel_list_view"
        )


class RightPanel(Widget):
    """A stopwatch widget."""

    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("4")),
            ListItem(Label("5")),
            ListItem(Label("6")),
            initial_index=None,
        )


class DebugApp(App):
    """FastAPI debug app."""

    def __init__(self, data: List[Dict], **kwargs):
        super().__init__(**kwargs)

        self.data = data

    CSS_PATH = "main.css"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "add_item", "Add new item"),
    ]

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Container(LeftPanel(items=self.data, id="my_list"), id="left_panel")
        yield Container(RightPanel(), id="right_panel")
        yield Footer()

    def action_add_item(self):
        self.query_one("#left_panel_list_view").append(ListItem(Label(str(uuid.uuid4()), classes="request_item")))

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


def render_ui(data):
    app = DebugApp(watch_css=True, data=data)
    app.run()
