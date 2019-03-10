"""Wrapper class for webob response to add functionality in future."""

import webob
from framework.utils.errors import HttpError


class Response(webob.Response):

    def __init__(self, request):
        webob.Response.__init__(self)
        self.request = request

    def redirect(self, location):
        """Redirect to specific location."""
        self.status = 302
        self.location = location
        self.request.session.store('dont_clear_flash', True)

        return 'Redirecting...'

    def redirect_back(self):
        """Redirect back to last location visited on this session."""
        try:
            location = self.request.session.get('last_route')
        except KeyError:
            location = ''
        
        return self.redirect(location)
        
    
    def force_redirect(self, location):
        raise HttpError(302, self.redirect(location))