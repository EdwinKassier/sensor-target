import asyncio

import strawberry
import json
from flask import Blueprint, current_app,request
from werkzeug.local import LocalProxy
from authentication import check_auth
import traceback
from .utils import data_collector, graph_creator
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
            collector = data_collector.DataCollector(symbol, investment)
            creator = graph_creator.GraphCreator(symbol)
            result = json.dumps(collector.driver_logic())
            graph_data = creator.driver_logic()
            return ProcessRequestResult(message=result, graph_data=graph_data)
        except Exception as exc:
            print(exc)
            return ProcessRequestResult(message="Symbol doesn't exist", graph_data=[])




schema = strawberry.Schema(query=Query)