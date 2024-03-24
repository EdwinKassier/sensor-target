"""This is the main view area of the api, creating the request endpoints"""

import json
from flask import Blueprint, current_app,request
from werkzeug.local import LocalProxy
from authentication import check_auth
import traceback
import grpc
from app.core.utils import data_collector


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

    logger.info('app route hit')
    try:
        collector = data_collector.DataCollector()
        result = collector.driver_logic()
        return(json.dumps({"message": 'Data available', "graph_data":result}), 
        200, {"ContentType": "application/json"})
    except Exception as exc:
        return(json.dumps({"message": 'Server Failure', "reason":str(exc)}),
        500, {"ContentType": "application/json"})

@core.route('/restricted', methods=['GET'])
@check_auth
def restricted():
    """A separate request to test the auth flow"""

    return json.dumps({"message": 'Successful Auth'}), 200, {"ContentType": "application/json"}
