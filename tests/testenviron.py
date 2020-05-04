"""In charge of setting up the test environment."""

from webframe.core import wsgi
from webframe.utils import db

def setup_unit_test_environment(application):
    """Setup unit test environment."""
    # For now, unit tests only need framework.core.app.py setup
    wsgi.WSGIApp(application)