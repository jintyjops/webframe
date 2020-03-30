# -*- coding: utf-8 -*-
"""The WSGI entry/communication point for the app."""

import os
import sys
import traceback
import logging
from importlib import reload
from webob.static import FileApp
from webframe.core.http.requests import Request
from webframe.core.http.responses import Response
from webframe.core.route import Router, ResourceRoute
from webframe.utils import storage
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
        logging.info('New request incoming...')
        try:
            request = Request(environ)
            logging.info(
                'New \'%s\' request for \'%s\' from \'%s\'',
                request.method,
                request.path,
                request.client_addr
            )
            response = self.generate(request, Response(request))
            if response.__class__ == FileApp:
                return response(environ, start_response)
        except Exception as e:
            logging.exception(e)
            traceback.print_stack()
            # Do some wsgi hackery
            body = ''
            status = f'{str(500)}'
            headers = [('Content-type', 'text/plain')]
            try:
                body = app.userapp.settings.ERROR_HANDLERS[500](traceback.format_exc())
                headers = [('Content-type', 'text/html')]
            except Exception as e:
                print('yeet2')
                logging.error('Error while trying to get 500 error page.')
                logging.exception(e)
                body = 'Internal server error.'
            start_response(status, headers)
            return [body.encode('utf-8')]
        finally:
            WSGIApp.conn_pool.release()
            app.db.close()
        return response(environ, start_response)

    def generate(self, request, response):
        """Takes request and response objects and returns response."""
        try:
            route = app.router.get_route(request)

            if isinstance(route, ResourceRoute):
                logging.info('Route is resource route.')
                return self.get_resource_response(response, route)
            else:
                logging.info('Fetching response...')
                request.set_route(route)
                try:
                    response.text = self.get_response(route, request, response)
                    logging.info('Response fetched...')
                except errors.DebugError as e:
                    if app.userapp.settings.DEBUG:
                        response.status = 500
                        response.text = e.message
                    else:
                        raise errors.HttpError(500, '')
        except errors.HttpError as e:
            if e.code == 500:
                logging.exception(e)
            if e.response:
                response.location = e.response.location
            response.status = e.code
            try:
                response.text = app.userapp.settings.ERROR_HANDLERS[int(e.code)](e.message)
            except (KeyError, ValueError):
                response.text = e.message

        logging.info('Status: %s', response.status)

        return response

    def get_response(self, Route, request, response):
        return Route.callable(request, response)

    def get_resource_response(self, response, route):
        """Serve a resource."""
        try:
            path = app.userapp.settings.RESOURCE_DIR + '/' + route.path
            if not os.path.exists(path) or not os.path.isfile(path):
                raise IOError
            return FileApp(path)
        except IOError:
            logging.warning('IOError while trying to access resource.')
            abort(404)