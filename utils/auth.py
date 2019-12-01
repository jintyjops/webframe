"""Defines some generic auth functions for login/logout"""

from framework.core import app

def auth(request):
    return Auth(request, app.userapp.settings.AUTH_MODEL)

class Auth():
    """A simple wrapper around the session for authentication of users."""

    def __init__(self, request, authmodel):
        self.request = request
        self.authmodel = authmodel

    def authorize(self, email, password):
        """Authorize the user with the given email/password."""

        # User is authorized.
        self.request.session.store('_auth', email)

        return True

    def unauth(self):
        """Destroy the current session."""
        self.request.session.destroy()

    def user(self):
        """Get the authorised user model."""
        return self.request.session.get('_auth')

    def authed(self):
        """Determine if this session is authorized."""
        return bool(self.request.session.get('_auth'))

