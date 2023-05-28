from rich.console import RenderableType
from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import TabbedContent, TabPane

from fastapi_xray.schemas import APIRequest
from fastapi_xray.ui.components.panel_factory import (
    CookiesPanelFactory,
    HeadersPanelFactory,
    PanelFactory,
    QueryParamsPanelFactory,
    RequestBodyPanelFactory,
    RequestDetailsPanelFactory,
    ResponseErrorPanelFactory,
    ResponseHeadersPanelFactory,
    SQLPanelFactory,
)
from fastapi_xray.ui.components.widgets import WrapperWidget
from fastapi_xray.ui.components.widgets.list import ListItems


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
    selected_request: Reactive[RenderableType] = Reactive(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # initialize the factories
        self.tabs = {
            "request": [
                RequestDetailsPanelFactory(),
                RequestBodyPanelFactory(),
                QueryParamsPanelFactory(),
                HeadersPanelFactory(),
                CookiesPanelFactory(),
            ],
            "response": [
                ResponseHeadersPanelFactory(),
                ResponseErrorPanelFactory(),
            ],
            "sql": [
                SQLPanelFactory(),
            ],
        }

    def create_panel(self, data: APIRequest, factory: PanelFactory) -> RenderableType:
        return factory.create_panel(data)

    def watch_selected_request(self, selected_request: APIRequest) -> None:
        for _, factories in self.tabs.items():
            for factory in factories:
                self.query_one(f"#{factory.id}").update(
                    self.create_panel(selected_request, factory)
                )

    def compose(self) -> ComposeResult:
        with Container(id="right_panel"):
            with TabbedContent():
                for tab_name, factories in self.tabs.items():
                    with TabPane(tab_name.upper()):
                        for factory in factories:
                            yield WrapperWidget(
                                self.create_panel(self.selected_request, factory),
                                id=f"{factory.id}",
                            )
