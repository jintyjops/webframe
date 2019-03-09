"""Utilities for generating views."""

def view(template, arguments=None):
    """Generate template."""
    with open(template, 'r') as template:
        return direct_view(template.read(), arguments)

def direct_view(template_data, arguments=None):
    """Get the direct view."""
    # TODO make this function.
    return template_data