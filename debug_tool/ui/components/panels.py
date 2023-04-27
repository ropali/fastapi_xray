from typing import Dict

from commons.logger import get_logger
from rich.console import RenderableType
from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import Reactive
from textual.widget import Widget
from ui.components.widgets.list import ListItems
from ui.components.widgets.text import InfoBox

logger = get_logger(__name__)


class LeftPanel(Widget):
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Container(id="left_panel"):
            yield ListItems()


class RightPanel(Widget):
    selected_request: Reactive[RenderableType] = Reactive({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_basic_details(self) -> str:
        if not self.selected_request:
            return "Nothing to display."

        return (
            f"\nHTTP Method: {self.selected_request.get('method')} \n\n"
            f"Path: {self.selected_request.get('path')}\n\n"
            f"Path Params: {self.selected_request.get('path_params')}\n\n"
            f"Query Params: {self.selected_request.get('query_params')}\n\n"
            f"Execution Time: {self.selected_request.get('time')} ms\n\n"
            f"Base URL: {self.selected_request.get('base_url')}\n\n"
            f"Response Code: {self.selected_request.get('status_code')}"
        )

    def get_headers(self) -> str:
        if not self.selected_request:
            return "Nothing to display."

        headers = self.selected_request.get("headers")

        if not headers:
            return ""

        text = "\n"

        last_key = list(headers.keys())[-1]

        for k, v in headers.items():
            text += f"{k.capitalize()}: {v}"

            if last_key == k:
                text += "\n"
            else:
                text += "\n\n"

        return text

    def compose(self) -> ComposeResult:
        yield Container(
            InfoBox("BASICS", self.get_basic_details(), id="basics_infobox"),
            InfoBox("HEADERS", self.get_headers(), id="headers_infobox"),
            id="right_panel",
        )

    def watch_selected_request(self, selected_request: Dict) -> None:
        # https://github.com/Textualize/textual/discussions/1683
        self.query_one("#basics_infobox").update(self.get_basic_details())
        self.query_one("#headers_infobox").update(self.get_headers())
