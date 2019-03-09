"""
Validation functions/callables.
Each callable must take a Form argument and a name argument and return either:
    None for if there is no issue or a message if there is an issue.
"""

def required(name, form):
    if form.input(name) is None:
        return 'The ' + name + ' field is required.'

class max_len():
    """The maximum length of the input in characters."""
    def __init__(self, length):
        self.length = length
    
    def __call__(self, name, form):
        _input = form.input(name)
        if _input is None:
            return
        if len(_input) > self.length:
            return 'The ' + name + ' field is too long.'

class min_len():
    """The maximum length of the input in characters."""
    def __init__(self, length):
        self.length = length
    
    def __call__(self, name, form):
        _input = form.input(name)
        if _input is None:
            return
        if len(_input) < self.length:
            return 'The ' + name + ' field is too short.'