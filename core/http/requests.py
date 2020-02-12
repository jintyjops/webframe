"""Wrapper class for webob request to add functionality in future."""

import webob
from webframe.core.http.session import Session
from io import BytesIO
import json


MOCK_ENVIRON = {
    'ACTUAL_SERVER_PROTOCOL': 'HTTP/1.1',
    'PATH_INFO': '/',
    'QUERY_STRING': '',
    'REMOTE_ADDR': '::1',
    'REMOTE_PORT': '123456',
    'REQUEST_METHOD': 'GET',
    'REQUEST_URI': '/',
    'SCRIPT_NAME': '',
    'SERVER_NAME': 'localhost',
    'SERVER_PROTOCOL': 'HTTP/1.1',
    'wsgi.multiprocess': False,
    'wsgi.multithread': True,
    'wsgi.run_once': False,
    'wsgi.url_scheme': 'http',
    'wsgi.version': (1, 0),
    'SERVER_PORT': '80',
    'HTTP_HOST': 'localhost:80',
    'HTTP_CONNECTION': 'keep-alive',
    'HTTP_SEC_FETCH_DEST': 'script',
    'HTTP_ACCEPT': '*/*',
    'HTTP_SEC_FETCH_SITE': 'same-origin',
    'HTTP_SEC_FETCH_MODE': 'no-cors',
    'HTTP_REFERER': 'http://localhost:80/',
    'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br',
    'HTTP_ACCEPT_LANGUAGE': 'en-GB,en-US;q=0.9,en;q=0.8',
    'HTTP_COOKIE': ''
}


class Request(webob.Request):

    def __init__(self, environ):
        webob.Request.__init__(self, environ)
        self.route = None
        self.session = None
        self.model = None

    def set_route(self, route):
        """
        Set the route generated from the routing process.
        Expecting Type: Route
        """
        # Warning: this is ovewriting webob.Request.urlargs
        self.urlargs = route.params
        self.route = route

    def url_param(self, name):
        return self.urlargs[name]

    def input(self, name):
        """Get input, attempts to get value from GET then POST."""
        return self.params[name]

    def allInput(self):
        """Get all input from POST, GET, and json."""
        params = self.params
        if self.content_type == 'application/json' and self.json is not None:
            params = {**params, **self.json}
        return params
        
    def post(self, name):
        """Get POST data."""
        try:
            return self.POST[name]
        except KeyError:
            return None
    
    def get(self, name):
        """Get GET data."""
        try:
            return self.GET[name]
        except KeyError:
            return None
    
    def get_json(self, name):
        """Get json data."""
        try:
            return self.json[name]
        except KeyError:
            return None

    @staticmethod
    def mock(get=None, body=None, environ = {}):
        environ = {**MOCK_ENVIRON, **environ}
        if get is not None:
            environ['QUERY_STRING'] = '&'.join([
                str(k) + '=' + str(get[k]) for k in get
            ])
        if body is not None:
            environ['wsgi.input'] = body
            environ['CONTENT_LENGTH'] = body.length
            environ['REQUEST_METHOD'] = 'POST'
            environ['CONTENT_TYPE'] = body.content_type
        return Request(environ)

class Body(BytesIO):
    """
    A body which can be passed to a request as wsgi.input.
    This is useful for mocking.
    """

    def __init__(self):
        super().__init__()
        self.length = None
        self.content_type = 'application/x-www-form-urlencoded'
    
    def urlencoded(self, data):
        data = '&'.join([f'{k}={data[k]}' for k in data])
        self.write(bytes(data.encode('utf-8')))

    def multipart(self, data):
        raise NotImplementedError('Multipart form data not implemented yet.')

    def json(self, data):
        self.content_type = 'application/json'
        data = bytes(json.dumps(data).encode('utf-8'))
        self.write(data)

    def write(self, data):
        super().write(data)

        self.seek(0)
        self.length = len(data)