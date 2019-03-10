"""
Session handling middleware.
Should be seperated into small operations so user can pick and choose
how to use it.
"""

from framework.core.http.session import Session


def fetch_or_create_session(request, response):
    request.session = Session(request)

def set_session_token_on_response(request, response):
    request.session.set_response_session_token(response)
