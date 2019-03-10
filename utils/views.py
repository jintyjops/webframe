"""Utilities for generating views."""
from framework.core import app

def view(template, arguments=None):
    """Generate template."""
    template_dir = app.userapp.settings.TEMPLATES
    with open(template_dir + template + '.html', 'r') as template:
        return direct_view(template.read(), arguments)

def direct_view(template_data, arguments=None):
    """Get the direct view."""
    # TODO make this function.
    return template_data + str(arguments)