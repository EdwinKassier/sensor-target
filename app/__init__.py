"""Create a bluepirnt to hook into the main system api"""


import logging.config
from os import environ
from celery import Celery
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from .config import config as app_config
from strawberry.flask.views import GraphQLView

from .core.views import core as core_blueprint
from .core.schema import schema


celery = Celery(__name__)

#Called in the run function, this creates and links the main app logic to the exposed endpoint

def create_app():
    """Create the using the relevant blueprints"""

    # loading env vars from .env file
    load_dotenv()
    APPLICATION_ENV = get_environment()
    app = Flask(app_config[APPLICATION_ENV].APP_NAME)
    app.config.from_object(app_config[APPLICATION_ENV])

    #This step is critical for allowing testing while in a local environment
    CORS(app, resources={r"/*": {'origins': '*'}})

    celery.config_from_object(app.config, force=True)
    
    # We are registering the core folder as a blueprint, 
    # this allows us to more easily create other blueprints(ie endpoints) in future if needed, say api/company/support
    #This allows for easier extension in future
    from .core.views import core as core_blueprint
    app.register_blueprint(
        core_blueprint,
        url_prefix='/api/v1/project/core'
    )

    app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql_view", schema=schema),
)

    return app


def get_environment():
    """Check which environment the api is in"""

    return environ.get('APPLICATION_ENV') or 'development'
