import requests
import multiprocessing

from flask import Flask
from flask_testing import LiveServerTestCase
import pytest

from insight import __version__, create_app

# Workaround for a multiprocessing bug on MacOS:
# https://github.com/pytest-dev/pytest-flask/issues/104
multiprocessing.set_start_method("fork")


def test_version():
    assert __version__ == "0.1.0"


class MyTest(LiveServerTestCase):
    def create_app(self):
        app = create_app()
        app.config["LIVESERVER_PORT"] = 8943
        app.config["LIVESERVER_TIMEOUT"] = 10
        return app

    def test_server_is_up_and_running(self):
        response = requests.get(self.get_server_url())
        self.assertEqual(response.status_code, 200)