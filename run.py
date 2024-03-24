"""This is the core of the api,
creating a central point for blueprinted frameworks to flow through"""

import json
import os
from app import create_app


app = create_app()


@app.route('/status', methods=['GET'])
def status():
    """Indicate the status of the api"""
    return (json.dumps({"message":  'DudeWheresMyLambo API Status : Running!'}),
            200, {"ContentType": "application/json"})


@app.route('/', methods=['GET'])
def home():
    """Welcome the user on a request to home"""
    return (json.dumps({"message": 'Welcome to the DudeWheresMyLambo API'}),
            200, {"ContentType": "application/json"})


if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 8080)), host='0.0.0.0', debug=True)
