import asyncio

import strawberry
import json
from flask import Blueprint, current_app,request
from werkzeug.local import LocalProxy
from authentication import check_auth
import traceback
import typing

@strawberry.type
class ProcessRequestResult:
    message: str
    graph_data: str

# Define a GraphQL schema
@strawberry.type
class Query:
    @strawberry.field
    def process_request(self, symbol: str, investment: int) -> ProcessRequestResult:
        try:
            return ProcessRequestResult(message=None, graph_data=None)
        except Exception as exc:
            print(exc)
            return ProcessRequestResult(message="Symbol doesn't exist", graph_data=[])




schema = strawberry.Schema(query=Query)