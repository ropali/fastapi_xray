from rich.console import RenderableType
from rich.panel import Panel
from rich.syntax import Syntax
from textual.widgets import Static


class SyntaxPanel(Static):
    """A custom panel that renders a Syntax widget."""

    def __init__(self, code: str, lexer: str, title: str, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.lexer = lexer
        self.code = code

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.__init__(*args, **kwargs)
        return obj.render()

    def render(self) -> RenderableType:
        return Panel(
            Syntax(self.code, self.lexer, padding=2, word_wrap=True),
            title=self.title,
            title_align="left",
            border_style="white",
        )
