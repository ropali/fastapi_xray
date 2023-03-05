import uuid
from time import monotonic

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Header, Footer, Static, ListView, ListItem, Label


class LeftPanel(Widget):
    """A widget to display elapsed time."""

    items = reactive([])

    def generate_items(self):
        for i in range(10):
            self.items.append(ListItem(Label(str(uuid.uuid4()), classes="request_item")))

    def compose(self) -> ComposeResult:
        self.generate_items()

        yield Static(
            "All Request",
            expand=True,
            id="left_panel_header"
        )

        yield ListView(
            *self.items,
            initial_index=None,
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
    """A Textual app to manage stopwatches."""

    CSS_PATH = "main.css"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Container(LeftPanel(), id="left_panel")
        yield Container(RightPanel(), id="right_panel")


def action_toggle_dark(self) -> None:
    """An action to toggle dark mode."""
    self.dark = not self.dark


def render_ui():
    app = DebugApp(watch_css=True)
    app.run()
