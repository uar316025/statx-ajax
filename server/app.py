#!/usr/bin/env python3
"""Main entry point of application"""

from os.path import dirname
from flask import Flask

import api_v1

APPNAME = 'statx-ajax'


def create_app():
    """Create flask application"""
    app = Flask(APPNAME)
    app.config.from_pyfile(dirname(__file__) + '/app.cfg', silent=True)

    app.register_blueprint(api_v1.bp)

    return app


if __name__ == '__main__':
    create_app().run()
