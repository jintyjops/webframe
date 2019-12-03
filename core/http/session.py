"""Session handler for the framework."""
import os
from base64 import b64encode
import time
import secrets

class Session(object):

    # 32 characters should be enough.
    TOKEN_LENGTH = 32
    # In seconds
    TOKEN_LIFE = 300
    # In seconds (86400 seconds == one day)
    CSRF_LIFE = 86400

    # in memory session handler.
    # dict of form {token: {key: value, etc...}, etc...}
    session = {}

    def __init__(self, request):
        """Initialise session for this user."""
        self.request = request
        try:
            # Check is Cookie actually exists
            self.request.headers['Cookie']
            cookies = self.request.cookies
        except KeyError:
            self.request.headers['Cookie'] = ''
            cookies = self.request.cookies
        try:
            self.token = cookies['session']
        except KeyError:
            self.token = self._generate_new_session_token(Session.TOKEN_LENGTH)

        self._create_if_not_exists()
        self._new_token_if_expired()
        self._clear_flash()

    def _generate_new_session_token(self, length):
        # Just in case ;)
        while True:
            token = b64encode(os.urandom(length))
            try:
                Session.session[token]
            except KeyError:
                break

        return str(token)

    def _create_if_not_exists(self):
        """Try to get or create then return a session with the current token."""
        try:
            Session.session[self.token]
        except KeyError:
            self.token = self._generate_new_session_token(Session.TOKEN_LENGTH)
            self._set_fresh_session()

    def _new_token_if_expired(self):
        """Create a new token if the current one is expired."""
        sess = Session.session[self.token]
        if sess['expiry'] < time.time():
            self.token = self._generate_new_session_token(Session.TOKEN_LENGTH)
            sess['expiry'] = time.time() + Session.TOKEN_LIFE
            Session.session[self.token] = sess

    def _set_fresh_session(self):
        Session.session[self.token] = {
                'expiry': time.time() + Session.TOKEN_LIFE,
                'flash': {},
                'csrf': {}
            }

    def _clear_flash(self):
        try:
            if not self.get('dont_clear_flash'):
                raise KeyError()
        except KeyError:
            Session.session[self.token]['flash'] = {}

        self.delete('dont_clear_flash')

    def get(self, key):
        """Get a value from the current session."""
        try:
            return Session.session[self.token][key]
        except KeyError:
            return None

    def store(self, key, value):
        """Store a value in the session."""
        Session.session[self.token][key] = value

    def delete(self, key):
        """Delete a value from the session. Fails silently."""
        try:
            del Session.session[self.token][key]
        except KeyError:
            pass
    
    def destroy(self):
        """Destroy the session completely."""
        del Session.session[self.token]
        # remake new session
        self._set_fresh_session()

    def flash(self, key, value):
        """Store a value for one request/response cycle."""
        Session.session[self.token]['flash'][key] = value

    def get_flash(self, key):
        """Get specific key from flash."""
        try:
            return self.flash_data()[key]
        except KeyError:
            return None

    def flash_data(self):
        """Get values only available for one request/response cycle."""
        return Session.session[self.token]['flash']

    def new_csrf(self):
        """Generates and stores a new CSRF token."""
        token = secrets.token_urlsafe(32)
        Session.session[self.token]['csrf'][token] = time.time() + Session.CSRF_LIFE
        return token

    def check_csrf(self, tokenToCheck):
        """Check CSRF token on this session."""
        self._remove_old_csrf_tokens()
        try:
            Session.session[self.token]['csrf'][tokenToCheck]
            # TODO determine if csrf token should be invalidated here.
            return True
        except KeyError:
            return False

    def _remove_old_csrf_tokens(self):
        """Remove all old csrf tokens for this session."""
        Session.session[self.token]['csrf'] = dict([
            (token, life)
            for token, life in Session.session[self.token]['csrf'].items()
            if time.time() < life
        ])

    def set_response_session_token(self, response, path="/", max_age=3600):
        response.set_cookie('session', self.token)

    def __repr__(self):
        return str(Session.session[self.token])