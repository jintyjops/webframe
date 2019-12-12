"""Wrapper class for webob request to add functionality in future."""

import webob
from framework.core.http.session import Session


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

    