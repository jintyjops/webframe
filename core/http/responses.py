"""Wrapper class for webob response to add functionality in future."""

import webob
from webob.static import FileApp
import json
from webframe.utils.errors import HttpError


class Response(webob.Response):

    def __init__(self, request):
        webob.Response.__init__(self)
        self.request = request
        self.template_args = {}

    def redirect(self, location):
        """Redirect to specific location."""
        self.status = 302
        self.location = location
        # so the flash data doesn't get wasted on the redirect
        self.request.session.store('dont_clear_flash', True)

        return 'Redirecting...'

    def redirect_back(self):
        """Redirect back to last location visited."""
        return self.redirect(self.request.referer)
        
    
    def force_redirect(self, location):
        """Immediatly quit and redirect to specific location."""
        raise HttpError(302, self.redirect(location))

    def force_redirect_back(self):
        """Immediatly quit and redirect to previous location."""
        raise HttpError(302, self.redirect_back())

    def set_content_type(self, content_type):
        self.content_type = content_type

    def json(self, jsonData):
        """Generates json as body of request."""
        self.set_content_type('application/json')
        return json.dumps(jsonData)

    def download(self, filename, downloadname, download=True):
        """
        Returns a download stream.
        filename is location of file.
        downloadname is name to download with.
        download (default True): specify whether to download the file or display 
            it inline (aka: content disposition: attachement or inline)
        """
        disposition = 'attachment'
        if not download:
            disposition = 'inline'

        return FileApp(filename, headerlist=[
            ['Content-Disposition', f'{disposition}; filename="{downloadname}"']
        ])

    def read_json(self):
        """Return json data written to this response."""
        return json.loads(self.text)