"""Base forms and form utilities."""

import html

class Form(object):
    """Base Form."""

    def __init__(self):
        """Setup attributes."""
        self.request = None
        self.params = {}
        self.valid = False
        self.errors = {}

    def sanitize(self, _input):
        """
        Sanitize input with default sanitization.
        Can be extended, though make sure to call parent
        if not extending complete functionality.

        returns dictionary containing sanitized input.
        """
        sanitized = {}
        for key, inp in _input.items():
            key = html.escape(key).strip()
            inp = html.escape(inp).strip()

            sanitized[key] = inp
        
        return sanitized

    def rules(self):
        return {}

    def validate(self):
        # Sanitize first and set params from request
        self.params = self.sanitize(self.request.allInput())

        # Get rules
        rules = self.rules()
        for name, validator_list in rules.items():
            for validator in validator_list:
                msg = validator(name, self)
                if msg is not None:
                    self.errors.setdefault(name, []).append(msg)

        # False if length of errors > 0
        return not len(self.errors)

    def extract(self):
        """Extract the values from the form."""
        pass

    def has(self, name):
        """Check if the form has an input."""
        try:
            _input = self.params[name]
            if _input is None or _input.strip() == '':
                return False
        except KeyError:
            return False

        return True

    def input(self, name):
        """
        Helper method to get the input.
        Returns None if the input is blank.
        """
        try:
            _input = self.params[name].strip()
            if _input == '':
                return None
            return _input
        except KeyError:
            return None
