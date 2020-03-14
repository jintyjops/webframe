# -*- coding: utf-8 -*-
"""The WSGI entry/communication point for the app."""

import sys
import traceback
from importlib import reload
from webframe.core.http.requests import Request
from webframe.core.http.responses import Response
from webframe.core.route import Router, ResourceRoute
from webframe.utils.errors import abort
from webframe.utils import errors, db
from webframe.core import app
from threading import Semaphore


def app_setup(userapp):
    """Set up global variables."""
    app.userapp = userapp
    app.router = Router(app.userapp.routes.route.routes)
    if app.db is not None:
        app.db.close()
    app.db = db.make_session(app.userapp.settings.ENGINE)
    if WSGIApp.conn_pool is None:
        WSGIApp.conn_pool = Semaphore(app.userapp.settings.MAX_CONNECTIONS)

class WSGIApp(object):
    """The app entry point from a wsgi call."""

    conn_pool = None

    def __init__(self, userapp):
        app_setup(userapp)

    def  __call__(self, environ, start_response):
        """The app entry point."""
        WSGIApp.conn_pool.acquire()
        try:
            request = Request(environ)
            response = self.generate(request, Response(request))
        finally:
            WSGIApp.conn_pool.release()
            app.db.close()
        return response(environ, start_response)

    def generate(self, request, response):
        """Takes request and response objects and returns response."""
        try:
            route = app.router.get_route(request)

            if isinstance(route, ResourceRoute):
                response.text = self.get_resource_response(route)
                response.set_content_type(str(request.accept))
            else:
                request.set_route(route)
                try:
                    response.text = self.get_response(route, request, response)
                except errors.DebugError as e:
                    if app.userapp.settings.DEBUG:
                        response.status = 500
                        response.text = e.message
                    else:
                        raise errors.HttpError(500, '')
        except errors.HttpError as e:
            if e.response:
                response.location = e.response.location
            response.status = e.code
            response.text = e.message

        return response

    def get_response(self, Route, request, response):
        return Route.callable(request, response)

    def get_resource_response(self, route):
        """Serve a resource."""
        try:
            path = app.userapp.settings.RESOURCE_DIR + '/' + route.path
            with open(path, 'r', encoding='utf8') as resource:
                return resource.read()
        except IOError:
            abort(404)