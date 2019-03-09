"""Session handler for the framework."""
import os
from base64 import b64encode

class Session(object):

    # in memory session handler.
    # dict of form {token: {key: value, etc...}, etc...}
    session = {}

    def __init__(self, request):
        """Initialise session for this user."""
        self.request = request
        cookies = self.request.headers['Cookie']
        try:
            self.token = cookies['session']
        except KeyError:
            # 32 characters should be enough.
            self.token = self.__generate_session_token(32)
        
        self.__get_or_create()

    def __generate_session_token(self, length):
        # Just in case ;)
        while True:
            token = b64encode(os.urandom(length))
            try:
                Session.session[token]
                return token
            except KeyError:
                continue

    def __get_or_create(self):
        """Try to get or create then return a session with the current token."""
        return Session.session.setdefault(self.token, [])

    def get(self, key):
        """Get a value from the current session."""
        return Session.session[self.token][key]

    def store(self, key, value):
        """Store a value in the session."""
        Session.session[self.token][key] = value

    def set_response_session_token(self, response, path="/", max_age=3600):
        response.set_cookie('session', self.token)