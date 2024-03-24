"""This is the main view area of the api, creating the request endpoints"""

import json
from flask import Blueprint, current_app,request
from werkzeug.local import LocalProxy
from authentication import check_auth
import traceback
import grpc
from .proto_files import api_pb2_grpc as pb2_grpc
from .proto_files import api_pb2 as pb2
from .utils import data_collector, graph_creator


core = Blueprint('core', __name__)
logger = LocalProxy(lambda: current_app.logger)


@core.before_request
def before_request_func():
    """Ensure logger name is set"""
    current_app.logger.name = 'core'

#Preparing for prod release cloud run, test
@core.route('/process_request', methods=['GET'])
def main_request():
    """Process a request around the main logic of the api"""

    logger.info('app test route hit')
    try:
        symbol = str(request.args.get('symbol').strip())
        investment = int(request.args.get('investment'))

        collector = data_collector.DataCollector(symbol, investment)
        creator = graph_creator.GraphCreator(symbol)
        result = collector.driver_logic()
        graph_data = creator.driver_logic() 
        return(json.dumps({"message": result,"graph_data":graph_data}), 
        200, {"ContentType": "application/json"})
    except Exception as exc:
        return(json.dumps({"message": 'Server Failure'}),
        500, {"ContentType": "application/json"})
    
@core.route('/process_request_grpc', methods=['GET'])
def main_request_grpc():
    """Process a request around the main logic of the api"""

    logger.info('app test route hit')
    try:
        symbol = str(request.args.get('symbol').strip())
        investment = int(request.args.get('investment'))

        logger.info(f'app test route hit args {symbol}:{investment}')

        # Define the endpoint URL
        endpoint = "master-dwml-backend-python-grpc-lqfbwlkw2a-uc.a.run.app"

        # Create a channel to the gRPC server
        # For cloud run it is imperative you pass along ssl credentials
        channel = grpc.secure_channel(endpoint, grpc.ssl_channel_credentials())

        stub = pb2_grpc.APIStub(channel)
        logger.info(f'app test route stub {stub}')
        response = stub.processRequest(pb2.apiRequest(symbol=symbol, investment=investment))
        logger.info(f'app test route hit response {response}')
        print(response)
        
        return json.dumps({"message": response.message, "graph_data": response.graph_data}), 200, {"ContentType": "application/json"}
    except grpc.RpcError as exc:
        # Handle gRPC errors
        status_code = exc.code()
        details = exc.details()
        return json.dumps({"error": f"gRPC Error ({status_code}): {details}"}), 500, {"ContentType": "application/json"}
    except Exception as exc:
        # Handle other exceptions
        return json.dumps({"error": str(exc)}), 500, {"ContentType": "application/json"}


@core.route('/restricted', methods=['GET'])
@check_auth
def restricted():
    """A separate request to test the auth flow"""

    return json.dumps({"message": 'Successful Auth'}), 200, {"ContentType": "application/json"}
