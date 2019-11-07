"""Reverse routes."""

import parse
from framework.core import app
from framework.utils.errors import abort

def url(name, args={}):
    """Reverse the route in the routes file"""
    routes = app.userapp.routes.route.routes

    url = None

    for route_params in routes:
        if __match_route(name, route_params):
           url = __generate_url(route_params, args)
        

    if url is None:
        abort(500, 'Could not find route...')

    return url

def __match_route(name, route_params):
    """Match the name to the route params. Return True if match."""
    try:
        return name == route_params['name']
    except KeyError:
        return False

def __generate_url(route_params, args):
    return route_params['path'].format(**args)

def resource(path):
    """Prepend the resource location onto the given path."""
    return app.userapp.settings.RESOURCE_DIR + '/' + path
