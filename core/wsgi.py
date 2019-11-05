"""The WSGI entry/communication point for the app."""

import sys
from importlib import reload
from framework.core.http.requests import Request
from framework.core.http.responses import Response
from framework.core.route import Router
from framework.utils import errors, db
from framework.core import app


class WSGIApp(object):
    """The app entry point from a wsgi call."""

    def __init__(self, userapp):
        # Set up global variables
        app.userapp = userapp
        app.router = Router(app.userapp.routes.route.routes)
        app.db = db.make_session(userapp.settings.ENGINE);

    def __call__(self, environ, start_response):
        """The app entry point."""
        request = Request(environ)
        response = Response(request)
        try:
            route = app.router.get_route(request)
            request.set_route(route)
            try:
                response.text = self.get_response(route, request, response)
            except errors.DebugError as e:
                if app.userapp.settings.DEBUG:
                    # TODO Include stack trace.
                    response.status = 500
                    response.text = e.message
                else:
                    raise errors.HttpError(500, '')
        except errors.HttpError as e:
            response.status = e.code
            response.text = e.message
                
        #response.text = self.get_route(request.path)
        return response(environ, start_response)

    def get_response(self, Route, request, response):
        return Route.callable(request, response)