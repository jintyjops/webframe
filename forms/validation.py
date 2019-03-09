"""
Validation functions/callables.
Each callable must take a Form argument and a name argument and return either:
    None for if there is no issue or a message if there is an issue.
"""

from abc import abstractmethod

class Validator():
    """Base validator."""

    def __init__(self, message=None):
        self.message = message

    def __call__(self, name, form):
        msg = self.validate(name, form)
        if msg is not None and self.message is not None:
            msg = self.message
        return msg

    @abstractmethod
    def validate(self, name, form):
        pass

class required(Validator):
    """Returns error if input is None."""

    def validate(self, name, form):
        if form.input(name) is None:
            return 'The ' + name + ' field is required.'

class max_len(Validator):
    """The maximum length of the input in characters."""
    def __init__(self, length, message=None):
        Validator.__init__(self, message)
        self.length = length
    
    def validate(self, name, form):
        _input = form.input(name)
        if _input is None:
            return
        if len(_input) > self.length:
            return 'The ' + name + ' field is too long.'

class min_len(Validator):
    """The maximum length of the input in characters."""
    def __init__(self, length, message=None):
        Validator.__init__(self, message)
        self.length = length
    
    def validate(self, name, form):
        _input = form.input(name)
        if _input is None:
            return
        if len(_input) < self.length:
            return 'The ' + name + ' field is too short.'