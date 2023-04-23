from commons.logger import get_logger
from rich import box
from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from textual.widget import Widget
from textual.widgets import Static

logger = get_logger(__name__)


class TextBox(Widget):
    def __init__(
        self,
        name: str,
        text: str,
        is_titled: bool,
        align: str,
        height: int = None,
        id: str = None,
    ) -> None:
        super().__init__(name=name, id=id)
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
            height=self.height,
        )


class InfoBox(Static):
    def __init__(self, border_title: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.border_title = border_title

    def render(self) -> RenderableType:
        return Panel(
            Align.left(self.renderable, vertical="top"),
            title=self.border_title,
            border_style="white",
            box=box.ROUNDED,
        )
