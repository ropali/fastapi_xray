import json
from abc import ABC, abstractmethod

from rich.align import Align
from rich.layout import Layout
from rich.panel import Panel
from rich.syntax import Syntax

from fastapi_xray.schemas import APIRequest
from fastapi_xray.ui.components.widgets.panels import SyntaxPanel


class PanelFactory(ABC):
    @abstractmethod
    def create_panel(self, data: APIRequest):
        raise NotImplementedError()

    @abstractmethod
    def parse_data(self, data: APIRequest):
        raise NotImplementedError()

    @property
    def id(self) -> str:
        return f"panel-{self.__class__.__name__}"


class HeadersPanelFactory(PanelFactory):
    def parse_data(self, selected_request: APIRequest):
        if not selected_request:
            return "{}"
        return json.dumps(selected_request.request.headers, indent=2)

    def create_panel(self, selected_request: APIRequest):
        return SyntaxPanel(
            code=self.parse_data(selected_request), lexer="json", title="Headers"
        )


class ResponseHeadersPanelFactory(HeadersPanelFactory):
    def parse_data(self, selected_request: APIRequest):
        if not selected_request:
            return "{}"
        return json.dumps(selected_request.response.headers, indent=2)


class RequestDetailsPanelFactory(PanelFactory):
    def parse_data(self, selected_request: APIRequest):
        request = selected_request.request

        layout = Layout()
        layout.split_row(
            Layout(name="left", ratio=9),
            Layout(name="right", ratio=1),
        )

        layout["left"].update(
            f"[b]{request.status_code}[/]\t[b]{request.method}[/]\t"
            f"[b]{request.path}[/]"
        )
        layout["right"].update(
            Align.right(f"[b] ⏱️ {selected_request.elapsed_time} ms[/]")
        )

        return layout

    def create_panel(self, selected_request: APIRequest):
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
    def parse_data(self, selected_request: APIRequest):
        if not selected_request or selected_request.request.body is None:
            return "{}"
        return json.dumps(selected_request.request.body, indent=2)

    def create_panel(self, selected_request: APIRequest):
        return SyntaxPanel(
            code=self.parse_data(selected_request), lexer="json", title="Body"
        )


class QueryParamsPanelFactory(PanelFactory):
    def parse_data(self, selected_request: APIRequest):
        if not selected_request:
            return "{}"
        return json.dumps(selected_request.request.query_params, indent=2)

    def create_panel(self, selected_request: APIRequest):
        return SyntaxPanel(
            code=self.parse_data(selected_request), lexer="json", title="Query Params"
        )


class CookiesPanelFactory(PanelFactory):
    def parse_data(self, selected_request: APIRequest):
        if not selected_request:
            return "{}"
        return json.dumps(selected_request.request.cookies, indent=2)

    def create_panel(self, selected_request: APIRequest):
        return SyntaxPanel(
            code=self.parse_data(selected_request), lexer="json", title="Cookies"
        )


class ResponseErrorPanelFactory(PanelFactory):
    _lexer_type = "txt"

    def parse_data(self, selected_request: APIRequest):
        if not selected_request or selected_request.response.error is None:
            return ""

        response = selected_request.response
        error_msg = response.error.message
        self._lexer_type = response.error.lexer_type

        if isinstance(error_msg, dict) or isinstance(error_msg, list):
            return json.dumps(error_msg, indent=2)

        return error_msg

    def create_panel(self, selected_request: APIRequest):
        return SyntaxPanel(
            code=self.parse_data(selected_request),
            lexer=self._lexer_type,
            title="Error",
        )


class SQLPanelFactory(PanelFactory):
    def parse_data(self, selected_request: APIRequest):
        if not selected_request or len(selected_request.sql) == 0:
            return "-- No SQL Queries Found! --"

        sql_queries = selected_request.sql

        statements = f"-- Total {len(sql_queries)} SQL queries ran \n\n"
        for idx, sql in enumerate(sql_queries, 1):
            statements += f"-- [{idx}] Took {sql.execution_time} ms\n"
            statements += f"{sql.statement}"

            if idx < len(sql_queries):
                statements += "\n\n"

        return statements

    def create_panel(self, selected_request):
        return Syntax(self.parse_data(selected_request), "sql", padding=2)
