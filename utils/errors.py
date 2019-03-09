"""Utility function to throw errors."""

def abort(code, message=None):
    """Throw a http status error."""
    raise HttpError(code, message)


class HttpError(Exception):
    """Wrapper for http errors."""

    def __init__(self, code, message):
        if code < 100 or code >= 600:
            raise ValueError('Code ' + str(code) + ' is not a valid http status code.')
        self.code = code
        self.message = self.__generate_message(code, message)

    def __generate_message(self, code, message):
        if message is not None:
            return self.__surround_h1(str(code) + ': ' + message)
        
        if code == 404:
            return self.__surround_h1(str(code) + ': could not find page :(')
        # TODO more standard errors

        return self.__surround_h1(str(code) + ': Oops there was an error.')

    def __surround_h1(self, message):
        return '<h1>' + message + '</h1>'