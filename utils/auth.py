"""Defines some generic auth functionality for login/logout."""

import bcrypt
from webframe.core.app import App

def auth(request):
    return Auth(request, App().settings().AUTH_MODEL)

def user():
    """
    Get the authorised user.
    This requires that Auth.authuser has been set.
    """
    return Auth.authuser

class Auth():
    """A simple wrapper around the session for authentication of users."""

    authuser = None

    def __init__(self, request, usermodel):
        self.request = request
        self.usermodel = usermodel

    def authorize(self, email, password, custom_check=None):
        """
        Authorize the user with the given email/password.

        Calls custom check with the fetched user argument if the email 
        and password are correct.
        If custom check returns False then authorisation fails.
        """

        user = self.usermodel.query().filter_by(email=email).first()

        if user is None:
            return False

        if not bcrypt.checkpw(password.encode('UTF-8'), user.password.encode('UTF-8')):
            return False

        if custom_check and not custom_check(user):
            return False
        
        # User is authorized store the users id.
        self.request.session.store('_auth', user.id)

        return user

    def deauth(self):
        """Destroy the current session."""
        self.request.session.destroy()

    def user(self):
        """
        Get the authorised user model.
        This fecthes the user model from the database, unlike the user() 
        function which will get Auth.authuser.
        """
        pk = self.request.session.get('_auth')
        if pk is None:
            return None
        return self.usermodel.findOrFail(pk)

    def authed(self):
        """Determine if this session is authorized."""
        return self.user() is not None

