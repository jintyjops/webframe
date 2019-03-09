"""The WSGI entry/communication point for the app."""
from framework.core.http.requests import Request
from framework.core.http.responses import Response
from importlib import reload
from framework.core.routes.route import Router
from framework.utils import errors
from framework.core import app
import sys


class WSGIApp(object):
    """The app entry point from a wsgi call."""

    def __init__(self, userapp):
        # Set up global variables
        app.userapp = userapp
        app.router = Router(app.userapp.routes.route.routes)

    def __call__(self, environ, start_response):
        """The app entry point."""
        request = Request(environ)
        response = Response()
        try:
            route = app.router.get_route(request.path)
            request.set_route(route)
            response.text = self.set_response(route, request, response)
        except errors.HttpError as e:
            response.status = e.code
            response.text = e.message
        #response.text = self.get_route(request.path)
        return response(environ, start_response)

    def set_response(self, Route, request, response):
        return Route.callable(request, response)