from rich import box
from rich.align import Align
from rich.panel import Panel
from textual.widget import Widget


class TextBox(Widget):
    def __init__(
        self, name: str, text: str, is_titled: bool, align: str, height: int = None
    ) -> None:
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
            height=self.height,
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
            height=None,
        )
