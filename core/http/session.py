"""Session handler for the framework."""
import os
from base64 import b64encode
import time
import secrets
import json
import threading

from framework.core import app

# XXX Race condition if with two requests to same session at once.
class SessionFileStore:
    """Interface for interacting with session store."""

    def __init__(self, token, session_dir):
        """Load the session."""
        # Lock for this token.
        self.lock = threading.Lock()
        self.token = token
        self.session_dir = session_dir

        self._create_session_dir_if_not_exists()
        self.session = self._load_session()

    def _create_session_dir_if_not_exists(self):
        """Create the session directory if it does not exist."""
        if not os.path.exists(self.session_dir) or not os.path.isdir(self.session_dir):
            os.mkdir(self.session_dir)

    def _load_session(self):
        """Load the entire session and decode to dict."""
        sess = {}

        self.lock.acquire()
        try:
            with open(self.session_dir + self.token, 'r') as f:
                sess = json.loads(f.read())
        except (IOError, json.decoder.JSONDecodeError):
            pass
        finally:
            self.lock.release()

        return sess

    def fresh(self):
        """Get fresh data from the session file."""
        self.session = self._load_session()

    def commit(self):
        """Commit the current session to the store."""
        self.lock.acquire()
        try:
            with open(self.session_dir + self.token, 'w') as f:
                f.write(json.dumps(self.session))
            return True
        except IOError:
            return False
        finally:
            self.lock.release()

    def exists(self):
        """True if session file exists."""
        return os.path.exists(self.session_dir + self.token)

    def set_new_token(self, token):
        """Sets new token, deletes old token."""
        # Delete old session file.
        self.lock.acquire()
        try:
            os.remove(self.session_dir + self.token)
        except IOError:
            pass
        finally:
            self.lock.release()

        # Set new session file.
        self.token = token
        self.commit()


class Session(object):

    # 32 characters should be enough.
    TOKEN_LENGTH = 32
    # In seconds (86400 seconds == one day)
    CSRF_LIFE = 86400

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

        session_dir = app.userapp.settings.STORAGE_DIR + '/sessions/'

        self._store = SessionFileStore(self.token, session_dir)
        self._create_if_not_exists()
        self._clear_flash()

    def _generate_new_session_token(self, length):
        """Returns a new session token."""
        return str(secrets.token_hex(32))

    def _create_if_not_exists(self):
        """Try to get or create then return a session with the current token."""
        if not self._store.exists():
            self._set_fresh_session()
            self.token = self._generate_new_session_token(Session.TOKEN_LENGTH)
            self._store.set_new_token(self.token)

    def _set_fresh_session(self):
        self._store.session = {
            'flash': {},
            'csrf': None
        }

    def _clear_flash(self):
        try:
            if not self.get('dont_clear_flash'):
                raise KeyError()
        except KeyError:
            self._store.session['flash'] = {}
            pass

        self.delete('dont_clear_flash')

    def get(self, key):
        """Get a value from the current session."""
        self._store.fresh()
        try:
            return self._store.session[key]
        except KeyError:
            return None

    def store(self, key, value):
        """Store a value in the session."""
        self._store.session[key] = value
        self.commit()

    def delete(self, key):
        """Delete a value from the session. Fails silently."""
        try:
            del self._store.session[key]
        except KeyError:
            pass
        self.commit()
    
    def destroy(self):
        """Destroy the session completely."""
        self._set_fresh_session()
        self.token = self._generate_new_session_token(Session.TOKEN_LENGTH)
        self._store.set_new_token(self.token)

    def flash(self, key, value):
        """Store a value for one request/response cycle."""
        self._store.session['flash'][key] = value
        self.commit()

    def get_flash(self, key):
        """Get specific key from flash."""
        try:
            return self.flash_data()[key]
        except KeyError:
            return None

    def flash_data(self):
        """Get values only available for one request/response cycle."""
        self._store.fresh()
        return self._store.session['flash']

    def csrf_token(self):
        """
        Generates or gets/stores the CSRF token.
        Returns the CSRF token for the session.
        """
        self._store.fresh()
        token = None
        try:
            token = self._store.session['csrf']
            if token == '' or token is None:
                raise KeyError
        except KeyError:
            token = str(secrets.token_hex(32))
            self._store.session['csrf'] = token
            self.commit()
        return token

    def check_csrf(self, tokenToCheck):
        """Check CSRF token on this session."""
        try:
            token = self._store.session['csrf']
            if tokenToCheck != token:
                raise KeyError
            return True
        except KeyError:
            return False

    def set_response_session_token(self, response, path="/", max_age=3600):
        response.set_cookie('session', self.token)

    def commit(self):
        """
        Commit the current session data.
        This is a wrapper method around the commit method of the 
        chosen session store.
        """
        self._store.commit()

    def __repr__(self):
        return str(self._store.session)