"""The WSGI entry/communication point for the app."""
from webob import Request, Response
from importlib import reload
from framework.core.routes.route import Router
from framework.utils import errors


class WSGIApp(object):
    """The app entry point from a wsgi call."""

    def __init__(self, app):
        self.app = app
        self.router = Router(self.app.routes.route.routes)

    def __call__(self, environ, start_response):
        """The app entry point."""
        request = Request(environ)
        response = Response()
        try:
            route = self.router.get_route(request.path)
            response.text = self.set_response(route)
            print(route.params())
        except errors.HttpError as e:
            response.status = e.code
            response.text = e.message
        #response.text = self.get_route(request.path)
        return response(environ, start_response)

    def set_response(self, Route):
        return Route.callable()