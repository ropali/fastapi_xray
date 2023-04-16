from typing import Dict

from commons.logger import get_logger
from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
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
    data = reactive(None)

    def __init__(self, data: Dict = None, **kwargs):
        super().__init__(**kwargs)
        self.data = data

    def get_basic_details(self) -> str:

        if not self.data:
            return "Nothing to display."

        return (
            f"\nHTTP Method: {self.data.get('method')} \n\n"
            f"Path: {self.data.get('path')}\n\n"
            f"Execution Time: {self.data.get('time')} ms\n\n"
            f"URL: {self.data.get('url')}\n\n"
            f"Response Code: {self.data.get('status_code')}"
        )

    def get_headers(self) -> str:
        if not self.data:
            return "Nothing to display."

        headers = self.data.get("headers")

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
        logger.info(f"Data: {self.data}")
        yield Container(
            InfoBox("Basics", self.get_basic_details(), align="left"),
            InfoBox("Headers", self.get_headers(), align="left"),
            id="right_panel",
        )
