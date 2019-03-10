"""Wrapper class for webob response to add functionality in future."""

import webob
from framework.utils.errors import HttpError


class Response(webob.Response):

    def __init__(self):
        webob.Response.__init__(self)

    def redirect(self, location):
        """Redirect to specific location."""
        self.status = 302
        self.location = location

        return 'Redirecting...'

    def redirect_back(self):
        """Redirect back to last location visited on this session."""
        # TODO: get from session.
    
    def force_redirect(self, location):
        raise HttpError(302, self.redirect(location))