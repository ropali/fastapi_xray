from rich.console import RenderableType
from textual.widgets import Static


class WrapperWidget(Static):
    """Wrapper widget around Static widget to override render method."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def render(self) -> RenderableType:
        return self.renderable
