"""
Validation functions/callables.
Each callable must take a Form argument and a name argument and return either:
    None for if there is no issue or a message if there is an issue.
"""

from abc import abstractmethod
import re
from sqlalchemy.sql.operators import ColumnOperators


RFC_EMAIL_REGEX = re.compile(r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""")
MAX_INT_SIZE = 2**32 - 1

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
        _input = form.input(name)
        if not form.has(name):
            return 'The ' + name + ' field is required.'

class max_len(Validator):
    """The maximum length of the input in characters."""
    def __init__(self, length, message=None):
        Validator.__init__(self, message)
        self.length = length
    
    def validate(self, name, form):
        _input = form.input(name)
        if not form.has(name):
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
        if not form.has(name):
            return
        if len(_input) < self.length:
            return 'The ' + name + ' field is too short.'

class email(Validator):
    """Returns error if input is not in email format."""

    def validate(self, name, form):
        _input = form.input(name)
        if not form.has(name):
            return
        if not bool(RFC_EMAIL_REGEX.fullmatch(_input)):
            return 'The ' + name + ' field must be an email.'

class unique(Validator):
    """Returns error if input is the same as an existing record column."""

    def __init__(self, model, column, exclude=[], message=None):
        """
        model: the model to query on
        column: the column on the model to check
        exlude: ids to exclude
        """
        Validator.__init__(self, message)
        self.model = model
        self.column = column
        self.exclude = exclude

    def validate(self, name, form):
        _input = form.input(name)

        if not form.has(name):
            return

        count = self.model.query() \
            .filter_by(**{self.column: _input}) \
            .filter(self.model.id.notin_(self.exclude)) \
            .count()

        if count > 0:
            return 'A record already exists with this ' + name + '.'

class integer(Validator):
    """Returns error if input is not in email format."""

    def __init__(self, max_size=MAX_INT_SIZE, message=None):
        Validator.__init__(self, message)
        self.max_size = max_size

    def validate(self, name, form):
        _input = form.input(name)
        if not form.has(name):
            return
        try:
            val = int(_input)
            if val >= self.max_size:
                return f'The {name} field must be smaller than {str(self.max_size)}.'
        except ValueError:
            return 'The ' + name + ' field must be an integer.'

class exists(Validator):
    """Checks if given id on model exists in the database."""

    def __init__(self, model, message=None):
        """
        model: the model to query on
        column: the column on the model to check
        exlude: ids to exclude
        """
        Validator.__init__(self, message)
        self.model = model

    def validate(self, name, form):
        _input = form.input(name)

        if not form.has(name):
            return

        model = self.model.find(_input)

        if model is None:
            return 'Invalid record.'