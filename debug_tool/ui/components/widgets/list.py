from commons.logger import get_logger
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Label, ListItem, ListView

logger = get_logger(__name__)


class LabelItem(ListItem):
    def __init__(self, label: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.label = label

    def compose(self) -> ComposeResult:
        yield Label(self.label)


class ListItems(ListView):
    items = reactive([])

    def __init__(self, **kwargs):
        super().__init__(id="left_panel_list_view", **kwargs)
