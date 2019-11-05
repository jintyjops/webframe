"""Utilities for generating views."""
from framework.core import app
from jinja2 import Template

def view(template, arguments=None):
    """Generate template."""
    template_dir = app.userapp.settings.TEMPLATES
    with open(template_dir + template + '.html', 'r') as template:
        return direct_view(template.read(), arguments)

def direct_view(template_data, arguments={}):
    """Get the direct view."""
    template = Template(template_data)
    return template.render(arguments)