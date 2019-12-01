"""Session handler for the framework."""
import os
from base64 import b64encode
import time

class Session(object):

    # 32 characters should be enough.
    TOKEN_LENGTH = 32
    # In seconds
    TOKEN_LIFE = 300

    # in memory session handler.
    # dict of form {token: {key: value, etc...}, etc...}
    session = {}

    # TODO handle expiry of tokens.

    def __init__(self, request):
        """Initialise session for this user."""
        self.request = request
        try:
            # Check for key error.
            self.request.headers['Cookie']
            cookies = self.request.cookies
        except KeyError:
            self.request.headers['Cookie'] = ''
            cookies = self.request.cookies
        try:
            self.token = cookies['session']
        except KeyError:
            self.token = self.__generate_new_session_token(Session.TOKEN_LENGTH)

        self.__create_if_not_exists()
        self.__clear_flash()

    def __generate_new_session_token(self, length):
        # Just in case ;)
        while True:
            token = b64encode(os.urandom(length))
            try:
                Session.session[token]
            except KeyError:
                break

        return str(token)

    def __create_if_not_exists(self):
        """Try to get or create then return a session with the current token."""
        try:
            Session.session[self.token]
        except KeyError:
            self.token = self.__generate_new_session_token(Session.TOKEN_LENGTH)
            Session.session[self.token] = {
                'expiry': time.time() + Session.TOKEN_LIFE,
                'flash': {}
            }

    def __clear_flash(self):
        try:
            if not self.get('dont_clear_flash'):
                raise KeyError()
        except KeyError:
            Session.session[self.token]['flash'] = {}

        self.delete('dont_clear_flash')

    def get(self, key):
        """Get a value from the current session."""
        return Session.session[self.token][key]

    def store(self, key, value):
        """Store a value in the session."""
        Session.session[self.token][key] = value

    def delete(self, key):
        """Delete a value from the session. Fails silently."""
        try:
            del Session.session[self.token][key]
        except KeyError:
            pass

    def flash(self, key, value):
        """Store a value for one request/response cycle."""
        Session.session[self.token]['flash'][key] = value

    def getFlash(self, key):
        """Get specific key from flash."""
        try:
            return self.flash_data()[key]
        except KeyError:
            return None

    def flash_data(self):
        """Get values only available for one request/response cycle."""
        return Session.session[self.token]['flash']

    def getNewCSRF(self):
        """Generates and stores a new CSRF token."""
        raise Exception('CSRF token generation not implemented!')

    def set_response_session_token(self, response, path="/", max_age=3600):
        response.set_cookie('session', self.token)

    def __repr__(self):
        return str(Session.session[self.token])