"""Defines some generic auth functionality for login/logout."""

import bcrypt
from framework.core import app
from teamhub.models import User

def auth(request):
    return Auth(request, app.userapp.settings.AUTH_MODEL)

class Auth():
    """A simple wrapper around the session for authentication of users."""

    def __init__(self, request, usermodel):
        self.request = request
        self.usermodel = usermodel

    def authorize(self, email, password):
        """Authorize the user with the given email/password."""

        user = self.usermodel.query().filter_by(email=email).first()

        if user is None:
            return False

        if not bcrypt.checkpw(password.encode('UTF-8'), user.password.encode('UTF-8')):
            return False
        
        # User is authorized store the users id.
        self.request.session.store('_auth', user.id)

        return True

    def deauth(self):
        """Destroy the current session."""
        self.request.session.destroy()

    def user(self):
        """Get the authorised user model."""
        pk = self.request.session.get('_auth')
        if pk is None:
            return None
        return self.usermodel.find(pk)

    def authed(self):
        """Determine if this session is authorized."""
        return self.user() is not None

