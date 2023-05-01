import json
from typing import Dict

from commons.logger import get_logger
from rich.align import Align
from rich.console import RenderableType
from rich.layout import Layout
from rich.panel import Panel
from rich.syntax import Syntax
from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import TabbedContent, TabPane
from ui.components.widgets import WrapperWidget
from ui.components.widgets.list import ListItems

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

    def render_basic_details(self) -> str | RenderableType:
        if not self.selected_request:
            return "Nothing to display."

        layout = Layout()
        layout.split_row(
            Layout(name="left", ratio=9),
            Layout(name="right", ratio=1),
        )

        request = self.selected_request["request"]

        layout["left"].update(
            f"[b]{request.get('status_code')}[/]\t[b]{request.get('method')}[/]\t"
            f"[b]{request.get('path')}[/]"
        )
        layout["right"].update(
            Align.right(f"[b] ⏱️ {self.selected_request.get('time')} ms[/]")
        )

        return Panel(
            layout,
            height=3,
            border_style="white",
        )

    def render_headers(self) -> RenderableType | str:
        if not self.selected_request:
            return "Nothing to display."

        headers = self.selected_request["request"].get("headers")

        return Panel(
            Syntax(json.dumps(headers, indent=2), "json", padding=2, word_wrap=True),
            title="Headers",
            title_align="left",
            border_style="white",
        )

    def render_response(self) -> RenderableType | str:
        if not self.selected_request:
            return "Nothing to display."

        data = self.selected_request["response"]

        return Panel(
            Syntax(json.dumps(data, indent=2), "json", padding=2, word_wrap=True),
            title="Response",
            title_align="left",
            border_style="white",
        )

    def render_query_params(self) -> RenderableType | str:
        if not self.selected_request:
            return "Nothing to display."

        query_params = self.selected_request["request"].get("query_params")

        return Panel(
            Syntax(
                json.dumps(query_params, indent=2), "json", padding=2, word_wrap=True
            ),
            title="Query Params",
            title_align="left",
            border_style="white",
        )

    def render_cookies(self) -> RenderableType | str:
        if not self.selected_request:
            return "Nothing to display."

        cookies = self.selected_request["request"].get("cookies")

        return Panel(
            Syntax(json.dumps(cookies, indent=2), "json", padding=2, word_wrap=True),
            title="Cookies",
            title_align="left",
            border_style="white",
        )

    def render_sql_data(self) -> RenderableType | str:
        if not self.selected_request or not self.selected_request.get("sql_queries"):
            return "Nothing to display."
        sql_queries = self.selected_request.get("sql_queries")

        statements = ""
        for idx, sql in enumerate(sql_queries):
            statements += f"-- Took {sql['execution_time']} ms\n"
            statements += f"{sql['statement']}"

            if idx < len(sql_queries) - 1:
                statements += "\n\n"

        return Syntax(statements, "sql", padding=2)

    def compose(self) -> ComposeResult:

        with Container(id="right_panel"):
            with TabbedContent():
                with TabPane("Request"):
                    yield WrapperWidget(
                        self.render_basic_details(), id="basics_infobox"
                    )
                    yield WrapperWidget(
                        self.render_query_params(), id="query_params_infobox"
                    )
                    yield WrapperWidget(self.render_headers(), id="headers_infobox")
                    yield WrapperWidget(self.render_cookies(), id="cookies_infobox")
                with TabPane("Response"):
                    yield WrapperWidget(self.render_response(), id="response_infobox")
                with TabPane("SQL"):
                    yield WrapperWidget(
                        self.render_sql_data(), id="sql_queries_infobox"
                    )

    def watch_selected_request(self, selected_request: Dict) -> None:
        # https://github.com/Textualize/textual/discussions/1683
        self.query_one("#basics_infobox").update(self.render_basic_details())
        self.query_one("#headers_infobox").update(self.render_headers())
        self.query_one("#query_params_infobox").update(self.render_query_params())
        self.query_one("#cookies_infobox").update(self.render_cookies())

        self.query_one("#response_infobox").update(self.render_response())
        if "sql_queries" in selected_request:
            self.query_one("#sql_queries_infobox").update(self.render_sql_data())
