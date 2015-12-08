# -*- coding: utf-8 -*-
"""`dbapi_viewer.wsgi` module.

Initializes the service app instance.
"""

__license__ = 'GLPv3'
__date__ = '13-11-2015'
__author__ = 'Papavassiliou Vassilis'
__version__ = '0.0.1'
__all__ = ['dbviewer_service']


import bottle
from api import index_handler, main_handler

dbviewer_service = bottle.Bottle()


def cors_enable_hook():
    """Enable COR's requests in a bottle.py wsgi app.
    """
    bottle.response.headers['Access-Control-Allow-Origin'] = '*'
    bottle.response.headers['Access-Control-Allow-Headers'] = \
        'Authorization, Credentials, X-Requested-With, Content-Type'
    bottle.response.headers['Access-Control-Allow-Methods'] = \
        'GET, PUT, POST, OPTIONS, DELETE'


def strip_path_hook():
    """Ignore trailing slashes.
    """
    bottle.request.environ['PATH_INFO'] = \
        bottle.request.environ['PATH_INFO'].rstrip('/')


dbviewer_service.get('/')(index_handler)
dbviewer_service.get('/<schema>/<action>')(main_handler)
dbviewer_service.post('/<schema>/<action>')(main_handler)
dbviewer_service.hook('before_request')(strip_path_hook)
dbviewer_service.hook('after_request')(cors_enable_hook)
