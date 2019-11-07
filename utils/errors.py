"""Utility function to throw errors."""

from framework.core import app

def abort(code, message=None):
    """Throw a http status error."""
    raise HttpError(code, message)


def debug(to_print):
    """Debugging utility to print to the page."""
    raise DebugError(to_print.__repr__())


class HttpError(Exception):
    """Wrapper for http errors."""

    def __init__(self, code, message=None):
        if code < 100 or code >= 600:
            raise ValueError('Code ' + str(code) + ' is not a valid http status code.')
        self.code = code
        self.message = self._generate_message(code, message)

    def _generate_message(self, code, message):
        if message is not None and app.userapp.settings.DEBUG:
            return self._surround_h1(str(code) + ': ' + message)
        
        if code == 404:
            return self._surround_h1(str(code) + ': could not find page :(')
        
        if 500 <= code < 600:
            return self._surround_h1(str(code) + ': Server error')

        return self._surround_h1(str(code) + ': Oops there was an error.')

    def _surround_h1(self, message):
        return '<h1>' + message + '</h1>'


class DebugError(HttpError):

    def __init__(self, message):
        self.message = message