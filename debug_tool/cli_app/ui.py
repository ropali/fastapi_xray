import uuid
from time import monotonic
from typing import Dict, List

from rich import box
from rich.align import Align
from rich.panel import Panel
from textual.app import App, ComposeResult
from textual.containers import Container, Grid
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Header, Footer, Static, ListView, ListItem, Label
from cli_app.logger import get_logger

logger = get_logger(__name__)


class TextBox(Widget):
    def __init__(self, name: str, text: str, is_titled: bool, align: str, height: int = None) -> None:
        super().__init__(name=name)
        self.text = text
        self.is_titled = is_titled
        self.align = align
        self.height = height

    def render(self) -> Panel:
        if self.align == "left":
            align = Align.left
        elif self.align == "center":
            align = Align.center
        else:
            align = Align.right
        return Panel(
            align(self.text, vertical="middle"),
            title=self.name if self.is_titled else None,
            border_style="white",
            box=box.ROUNDED,
            height=self.height
        )


class InfoBox(Widget):
    DEFAULT_CLASSES = "info-box"

    def __init__(self, name: str, text: str, align: str) -> None:
        super().__init__(name=name)
        self.text = text
        self.align = align

    def render(self) -> Panel:
        if self.align == "left":
            align = Align.left
        elif self.align == "center":
            align = Align.center
        else:
            align = Align.right
        return Panel(
            align(self.text, vertical="middle"),
            title=self.name,
            border_style="white",
            box=box.ROUNDED,
            safe_box=True,
            height=None
        )


class LeftPanel(Widget):
    items = reactive([])

    DEFAULT_CSS = """
        ListItem {
            color: $text;
            height: auto;
            background: #5f6062;
            overflow: hidden hidden;
        }
        ListItem > Widget :hover {
            background: #5f6062;
        }
        ListView > ListItem.--highlight {
            background: #7b7263 50%;
        }
        ListView:focus > ListItem.--highlight {
            background: #7b7263;
        }
        ListItem > Widget {
            height: auto;
        }
        """

    def __init__(self, items: List[Dict], **kwargs):
        super().__init__(**kwargs)
        self.items = items

    def compose(self) -> ComposeResult:
        logger.info(str(self.items))
        self.items = [ListItem(Label(f"[{item.get('method')}] {item.get('path')}", classes="request_item")) for item in
                      self.items]

        yield Container(
            ListView(
                *self.items,
                initial_index=None,
                id="left_panel_list_view"
            ),
            id="left_panel"
        )


class RightPanel(Widget):

    def __init__(self, data: Dict, **kwargs):
        self.data = data
        super().__init__(**kwargs)

    def construct_text(self) -> str:
        return f"HTTP Method: {self.data.get('method')} \n" \
               f"Path: {self.data.get('path')}\n" \
               f"Execution Time: {self.data.get('time')} ms\n" \
               f"URL: {self.data.get('url')}\n" \
            f"Response Code: {self.data.get('status_code')}\n"

    def compose(self) -> ComposeResult:
        yield Container(
            InfoBox("Basics", self.construct_text(), align="left"),
            InfoBox("Query Parameters", self.construct_text(), align="left"),
            InfoBox("Headers", self.construct_text(), align="left"),
            id="right_panel"
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
        yield Container(TextBox("FastAPI Debug", "FastAPI Inspector", False, "center"), id="app_title")
        yield LeftPanel(items=self.data)
        yield RightPanel(self.data[0])

        yield Footer()

    def action_add_item(self):
        self.query_one("#left_panel_list_view").append(ListItem(Label(str(uuid.uuid4()), classes="request_item")))

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


def render_ui(data):
    app = DebugApp(watch_css=True, data=data)
    app.run()
