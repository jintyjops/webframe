"""Utilities for generating views."""
from framework.core import app
from framework.utils import routes
from jinja2 import Template

def view(template, arguments={}):
    """Generate template."""
    env = app.userapp.settings.template_env
    template = env.get_template(template)
    return template.render(__get_global_args(arguments))

def direct_view(template_data, arguments={}):
    """Get the direct view."""
    template = Template(template_data)
    return template.render(__get_global_args(arguments))

def __get_global_args(arguments):
    """Gets the global arguments to be passed to the view."""
    return {**app.userapp.settings.GLOBAL_TEMPLATE_ARGS, **arguments}