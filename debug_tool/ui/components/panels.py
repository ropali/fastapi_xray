from typing import Dict, List

from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView
from ui.components.widgets import InfoBox


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
        self.items = [
            ListItem(
                Label(
                    f"[{item.get('method')}] {item.get('path')}", classes="request_item"
                )
            )
            for item in self.items
        ]

        yield Container(
            ListView(*self.items, initial_index=None, id="left_panel_list_view"),
            id="left_panel",
        )


class RightPanel(Widget):
    def __init__(self, data: Dict, **kwargs):
        self.data = data
        super().__init__(**kwargs)

    def get_basic_details(self) -> str:
        return (
            f"\nHTTP Method: {self.data.get('method')} \n\n"
            f"Path: {self.data.get('path')}\n\n"
            f"Execution Time: {self.data.get('time')} ms\n\n"
            f"URL: {self.data.get('url')}\n\n"
            f"Response Code: {self.data.get('status_code')}"
        )

    def get_headers(self) -> str:
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
        yield Container(
            InfoBox("Basics", self.get_basic_details(), align="left"),
            InfoBox("Headers", self.get_headers(), align="left"),
            id="right_panel",
        )
