"""Session handler for the framework."""
import os
import logging
import datetime
from base64 import b64encode
import time
import secrets
import json
import threading

from webframe.core import app

# XXX Race condition if with two requests to same session at once.
class SessionFileStore:
    """
    Interface for interacting with session store.
    Note: the object pattern {'_type': type, 'value': value} is reserved
    by this file store.
    """

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
                sess = json.loads(f.read(), object_hook=self.from_json_converter)
        except (IOError, json.decoder.JSONDecodeError) as e:
            logging.warning('Unable to load session.')
            logging.exception(e)
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
                f.write(json.dumps(self.session, default=self.to_json_converter))
            return True
        except IOError as e:
            logging.warning('Unable to commit sessions.')
            logging.exception(e)
            return False
        finally:
            self.lock.release()

    def to_json_converter(self, obj):
        """Converts non native json types to json from python objects."""
        if isinstance(obj, datetime.datetime):
            return {'_type': 'datetime', 'value': obj.isoformat()}
    
    def from_json_converter(self, obj):
        """Converts any non native json values to respective python objects"""
        if '_type' in obj and 'value' in obj:
            if obj['_type'] == 'datetime':
                return datetime.datetime.fromisoformat(obj['value'])
        return obj

    def exists(self):
        """True if session file exists."""
        return os.path.exists(self.session_dir + self.token)

    def set_new_token(self, token):
        """Sets new token, deletes old token."""
        # Delete old session file.
        self.lock.acquire()
        try:
            os.remove(self.session_dir + self.token)
        except IOError as e:
            logging.warning('Unable to remove old session.')
            logging.exception(e)
            pass
        finally:
            self.lock.release()

        # Set new session file.
        self.token = token
        self.commit()

    def destroy(self):
        """Destroy the session."""
        os.remove(os.path.join(self.session_dir, self.token))

    @staticmethod
    def all_session_tokens(session_dir):
        """Get all the current session tokens."""
        session_files = [
            f for f in os.listdir(session_dir)
            if os.path.isfile(os.path.join(session_dir, f))
        ]
        return session_files

class SessionMemoryStore:
    """Interface for interacting with session store in memory."""

    sessions = {}

    def __init__(self, token, session_dir):
        """Load the session."""
        # Lock for this token.
        self.token = token
        try:
            self.session = SessionMemoryStore.sessions[self.token]
        except KeyError:
            self.session = {}

    def fresh(self):
        """Get latest session data."""
        try:
            self.session = SessionMemoryStore.sessions[self.token]
        except KeyError:
            self.session = {}

    def commit(self):
        """Commit the current session to the store."""
        SessionMemoryStore.sessions[self.token] = self.session

    def exists(self):
        """True if session file exists."""
        try:
            SessionMemoryStore.sessions[self.token]
            return True
        except KeyError:
            return False

    def set_new_token(self, token):
        """Sets new token, deletes old token."""
        old = {}
        try:
            old = SessionMemoryStore.sessions[self.token]
            del SessionMemoryStore.sessions[self.token]
        except KeyError:
            pass
        SessionMemoryStore.sessions[token] = old
        self.token = token
    
    def destroy(self):
        """Destroy the session."""
        del SessionMemoryStore.sessions[self.token]

    @staticmethod
    def all_session_tokens(session_dir):
        """Get all the current session tokens."""
        return [k for k in SessionMemoryStore.sessions.keys()]

# 32 characters should be enough.
TOKEN_LENGTH = 32
class Session(object):

    # In seconds (86400 seconds == one day)
    CSRF_LIFE = 86400

    StoreType = SessionFileStore

    def __init__(self, request):
        """Initialise session for this user."""
        session_dir = app.userapp.settings.STORAGE_DIR + '/sessions/'

        self._purge_expired_sessions(session_dir)

        self.request = request
        self.session_expiry = app.userapp.settings.SESSION_EXPIRY
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
            self.token = self._generate_new_session_token()

        self._store = Session.StoreType(self.token, session_dir)
        self._create_if_not_exists()
        self._clear_flash()
        self._update_expiry()
        self.commit()

    def _purge_expired_sessions(self, session_dir):
        """Remove expired sessions."""
        tokens = Session.StoreType.all_session_tokens(session_dir)
        for token in tokens:
            store = Session.StoreType(token, session_dir)
            try:
                expiry = store.session['expiry']
                if expiry < datetime.datetime.now():
                    raise KeyError
            except KeyError:
                store.destroy()

    def _generate_new_session_token(self, length=TOKEN_LENGTH):
        """Returns a new session token."""
        return str(secrets.token_hex(32))

    def _create_if_not_exists(self):
        """Try to get or create then return a session with the current token."""
        if not self._store.exists():
            self._set_fresh_session()
            self.token = self._generate_new_session_token()
            self._store.set_new_token(self.token)

    def _get_new_session_expiry_from_now(self):
        expiry = datetime.datetime.now() + datetime.timedelta(days=365)
        if self.session_expiry > 0:
            expiry = datetime.datetime.now() + datetime.timedelta(seconds=self.session_expiry)
        return expiry

    def _set_fresh_session(self):
        self._store.session = {
            'flash': {},
            'csrf': None,
            'expiry': self._get_new_session_expiry_from_now()
        }

    def _clear_flash(self):
        try:
            self._store.session['dont_clear_flash']
        except KeyError:
            self._store.session['flash'] = {}

        self.delete('dont_clear_flash')
    
    def _update_expiry(self):
        """Updates expiry for this request."""
        try:
            self._store.session['expiry'] = self._get_new_session_expiry_from_now()
        except KeyError:
            pass

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
        self.token = self._generate_new_session_token()
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