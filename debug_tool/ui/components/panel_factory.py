import json
from abc import ABC, abstractmethod
from typing import Dict

from commons.logger import get_logger
from rich.align import Align
from rich.layout import Layout
from rich.panel import Panel
from rich.syntax import Syntax
from ui.components.widgets.panels import SyntaxPanel

logger = get_logger(__name__)


class PanelFactory(ABC):
    @abstractmethod
    def create_panel(self, data):
        raise NotImplementedError()

    @abstractmethod
    def parse_data(self, data):
        raise NotImplementedError()

    @property
    def id(self) -> str:
        return f"panel-{self.__class__.__name__}"


class HeadersPanelFactory(PanelFactory):
    def parse_data(self, selected_request: Dict):
        if not selected_request:
            return "{}"
        return json.dumps(
            selected_request.get("request", {}).get("headers", {}), indent=2
        )

    def create_panel(self, selected_request):
        return SyntaxPanel(
            code=self.parse_data(selected_request), lexer="json", title="Headers"
        ).render()


class ResponseHeadersPanelFactory(HeadersPanelFactory):
    def parse_data(self, selected_request: Dict):
        if not selected_request:
            return "{}"
        return json.dumps(
            selected_request.get("response", {}).get("headers", {}), indent=2
        )


class RequestDetailsPanelFactory(PanelFactory):
    def parse_data(self, selected_request: Dict):
        request = selected_request.get("request")

        layout = Layout()
        layout.split_row(
            Layout(name="left", ratio=9),
            Layout(name="right", ratio=1),
        )

        layout["left"].update(
            f"[b]{request.get('status_code')}[/]\t[b]{request.get('method')}[/]\t"
            f"[b]{request.get('path')}[/]"
        )
        layout["right"].update(
            Align.right(f"[b] ⏱️ {selected_request.get('elapsed_time')} ms[/]")
        )

        return layout

    def create_panel(self, selected_request: Dict):
        if not selected_request:
            return Panel(
                Align.center("[b]No request selected![/]"),
                height=3,
                border_style="white",
            )

        return Panel(
            self.parse_data(selected_request),
            height=3,
            border_style="white",
        )


class RequestBodyPanelFactory(PanelFactory):
    def parse_data(self, selected_request: Dict):
        if (
            not selected_request
            or selected_request.get("request", {}).get("body") is None
        ):
            return "{}"
        return json.dumps(selected_request.get("request", {}).get("body", {}), indent=2)

    def create_panel(self, selected_request: Dict):
        return SyntaxPanel(
            code=self.parse_data(selected_request), lexer="json", title="Body"
        ).render()


class QueryParamsPanelFactory(PanelFactory):
    def parse_data(self, selected_request: Dict):
        if not selected_request:
            return "{}"
        return json.dumps(
            selected_request.get("request", {}).get("query_params", {}), indent=2
        )

    def create_panel(self, selected_request: Dict):
        return SyntaxPanel(
            code=self.parse_data(selected_request), lexer="json", title="Query Params"
        ).render()


class CookiesPanelFactory(PanelFactory):
    def parse_data(self, selected_request: Dict):
        if not selected_request:
            return "{}"
        return json.dumps(
            selected_request.get("request", {}).get("cookies", {}), indent=2
        )

    def create_panel(self, selected_request: Dict):
        return SyntaxPanel(
            code=self.parse_data(selected_request), lexer="json", title="Cookies"
        ).render()


class ResponseErrorPanelFactory(PanelFactory):
    def parse_data(self, selected_request: Dict):
        if not selected_request:
            return ""
        response = selected_request.get("response", {})
        if response.get("error"):
            return response.get("error_message")

        return "No error occurred!"

    def create_panel(self, selected_request: Dict):
        return SyntaxPanel(
            code=self.parse_data(selected_request), lexer="txt", title="Error Trace"
        ).render()


class SQLPanelFactory(PanelFactory):
    def parse_data(self, selected_request: Dict):
        if not selected_request or len(selected_request.get("sql", [])) == 0:
            return "-- No SQL Queries Found! --"

        sql_queries = selected_request.get("sql", [])

        statements = f"-- Total {len(sql_queries)} SQL queries ran \n\n"
        for idx, sql in enumerate(sql_queries, 1):
            statements += f"-- [{idx}] Took {sql['execution_time']} ms\n"
            statements += f"{sql['statement']}"

            if idx < len(sql_queries):
                statements += "\n\n"

        return statements

    def create_panel(self, selected_request):
        return Syntax(self.parse_data(selected_request), "sql", padding=2)
