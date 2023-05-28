from textual.app import ComposeResult
from textual.widget import AwaitMount
from textual.widgets import Label, ListItem, ListView

from fastapi_xray.commons.logger import get_logger

logger = get_logger()


class LabelItem(ListItem):
    DEFAULT_CSS = """
        ListItem {
            color: $text;
            height: auto;
            background: #68625d;
            overflow: hidden hidden;
        }
        ListItem > Widget :hover {
            background: $boost;
        }
        ListView > ListItem.--highlight {
            background: #7b7263 50%;
        }
        ListView:focus > ListItem.--highlight {
            background: #5f6062;
        }
        ListItem > Widget {
            height: auto;
        }
        """

    def __init__(self, label: str, value: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.label = label
        self.value = value

    def compose(self) -> ComposeResult:
        yield Label(self.label, classes="left_panel_label")


class ListItems(ListView):
    def __init__(self, **kwargs):
        super().__init__(id="left_panel_list_view", **kwargs)

    def prepend(self, item: ListItem) -> AwaitMount:
        """Prepend a new ListItem to the start of the ListView.

        Args:
            item: The ListItem to prepend.

        Returns:
            An awaitable that yields control to the event loop
                until the DOM has been updated with the new child item.
        """
        await_mount = self.mount(item, before=0)
        # self.index = 0
        return await_mount
