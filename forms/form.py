"""Base forms and form utilities."""

class Form(object):
    """Base Form."""

    def __init__(self):
        """Setup attributes."""
        self.request = None
        self.validated = False

    def valid(self):
        return self.validated

    def validate(self):
        """
        Return true or false depending on whether form was valid.
        Should be overriden by implementing class.
        Returns True by default.
        """
        return True

    def input(self, name):
        """Helper method. Calls request.input(name)."""
        return self.request.input(name)