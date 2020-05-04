"""Reverse routes."""

import parse
from webframe.core.app import App
from webframe.utils.errors import abort

def url(name, args={}, get={}, include_host=False):
    """Reverse the route in the routes file"""
    routes = App().routes()

    url = None

    for route_params in routes:
        if __match_route(name, route_params):
            url = __generate_url(route_params, args)

    if url is None:
        abort(500, 'Could not find route: ' + str(name))

    get_string = '&'.join([
        str(key) + '=' + str(val)
        for key, val in get.items()
    ])

    if get_string:
        url += '?' + get_string

    if include_host:
        host = App().settings().HOST
        port = App().settings().PORT
        if port != 80:
            host = f'{host}:{str(port)}'
        if App().settings().USING_SSL:
            host = f'https://{host}'
        else:
            host = f'http://{host}'
        url = host + url

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
    return App().settings().RESOURCE_URL + '/' + path
