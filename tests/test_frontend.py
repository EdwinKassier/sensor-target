import unittest
import pytest

from flask import abort, url_for
from flask_testing import TestCase
from os import environ, path

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        with app.test_client() as client:
            yield client

        
def test_base_route_without_args(client):
    rv = client.get('/api/v1/core/unknown_request')

    print(rv.get_data())
    assert rv.status_code == 404

def test_base_route_with_args_valid_symbol(client):
    rv = client.get('/api/v1/core/process_request')

    print(rv.get_data())
    assert rv.status_code == 200

