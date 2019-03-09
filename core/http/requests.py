"""Wrapper class for webob request to add functionality in future."""

import webob


class Request(webob.Request):

    def __init__(self, environ):
        webob.Request.__init__(self, environ)

    def set_route(self, route):
        """
        Set the route generated from the routing process.
        Expecting Type: Route
        """
        self.urlargs = route.params()

    def url_param(self, name):
        return self.urlargs[name]