"""Wrapper class for webob response to add functionality in future."""

import webob


class Response(webob.Response):

    def __init__(self):
        webob.Response.__init__(self)
