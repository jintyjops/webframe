"""
Validation functions/callables.
Each callable must take a Form argument and a name argument and return either:
    None for if there is no issue or a message if there is an issue.
"""

from abc import abstractmethod
import re
import mimetypes
import filetype
import tempfile
from sqlalchemy.sql.operators import ColumnOperators


RFC_EMAIL_REGEX = re.compile(r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""")
MAX_INT_SIZE = int((2**32) / 2) - 1

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

class file_required(Validator):
    """Returns error if input is not file."""

    def validate(self, name, form):
        if not form.has_file(name):
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

    def __init__(self, max_size=MAX_INT_SIZE, min_size=0, message=None):
        Validator.__init__(self, message)
        self.max_size = max_size
        self.min_size = min_size

    def validate(self, name, form):
        _input = form.input(name)
        if not form.has(name):
            return
        try:
            val = int(_input)
            if val >= self.max_size:
                return f'The {name} field must be smaller than {str(self.max_size)}.'
            if val < self.min_size:
                return f'The {name} field must be greater than {str(self.min_size)}.'
        except ValueError:
            return 'The ' + name + ' field must be an integer.'

class exists(Validator):
    """Checks if given id on model exists in the database."""

    def __init__(self, model, column="id", message=None):
        """
        model: the model to query on
        column: the column on the model to check
        exlude: ids to exclude
        """
        Validator.__init__(self, message)
        self.model = model
        self.column = column

    def validate(self, name, form):
        _input = form.input(name)

        if not form.has(name):
            return

        count = self.model.query().filter_by(**{self.column: _input}).count()
        if not count:
            return 'Invalid record.'

class confirm(Validator):
    """
    Fails if there is not another value which matches this one 
    with the key "<input_name>_confirm".
    """

    def validate(self, name, form):
        othername = name + '_confirm'

        if not form.has(name):
            return

        if form.has(name) and not form.has(othername):
            return f'You must confirm the {name}.'

        _input = form.input(name)
        other = form.input(othername)

        if _input != other:
            return f'The {name} field must match.'

class isin(Validator):
    """
    Fails if value is not in the given list
    """

    def __init__(self, values, message=None):
        """
        values: the values to check against
        """
        Validator.__init__(self, message)
        self.values = values
        self.one_of = ', '.join(v for v in values)

    def validate(self, name, form):
        if not form.has(name):
            return

        _input = form.input(name)

        if _input not in self.values:
            return f'The {name} field must be one of {self.one_of}.'

class _file(Validator):
    """
    Checks if file. Creates a tempfile for the file.
    """

    def __init__(self, mimetypes=[], max_size=MAX_INT_SIZE, message=None):
        """
        Set the acceptable mimetypes and max size (in bytes) of the file.
        Leave blank for any mimetype or filesize.
        """
        Validator.__init__(self, message)
        self.mimetypes = mimetypes
        self.max_size = max_size

    def validate(self, name, form):
        if not form.has(name):
            return

        _input = form.input(name)

        if _input.__class__.__name__ != 'cgi_FieldStorage' and not bool(_input):
            return

        if _input.__class__.__name__ != 'cgi_FieldStorage':
            return 'You must upload a file.'
        
        if len(_input.value) >= self.max_size:
            return f'File must be smaller than {int(self.max_size / 1000)}KB.'
        _type = filetype.guess(_input.value)
        if len(self.mimetypes) and _type is not None and _type.mime not in self.mimetypes:
            types = ', '.join([k for k, v in mimetypes.types_map.items() if v in self.mimetypes])
            return f'File must be one of {types}.'