import json
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class Request(BaseModel):
    base_url: str
    query_params: Dict[str, Any]
    path_params: Dict[str, Any]
    path: str
    status_code: int
    method: str
    cookies: Dict[str, str]
    headers: Dict[str, str]
    body: Union[Dict[str, Any], Any]


class ResponseError(BaseModel):
    message: Union[str, List[Dict[str, Any]]]

    @property
    def lexer_type(self):
        _lexer = "json"

        if isinstance(self.message, str):
            try:
                json.loads(self.message)
                _lexer = "json"
            except json.decoder.JSONDecodeError:
                _lexer = "txt"
        return _lexer


class Response(BaseModel):
    headers: Dict[str, str]
    error: Optional[ResponseError]


class SQlQuery(BaseModel):
    statement: str
    execution_time: str


class APIRequest(BaseModel):
    """An API call information"""

    request_id: str
    request: Request
    response: Response
    sql: List[SQlQuery]
    elapsed_time: str
