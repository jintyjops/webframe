"""Base forms and form utilities."""

class Form(object):
    """Base Form."""

    def __init__(self):
        """Setup attributes."""
        self.request = None
        self.valid = False
        self.errors = {}

    def rules(self):
        return {}

    def validate(self):
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

    def input(self, name):
        """Helper method. Calls request.input(name)."""
        return self.request.input(name)
