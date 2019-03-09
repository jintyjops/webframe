"""
Base controller for the application.
There will be one controller per page/view.
Each controller will implement a view method which will be in
charge of returning a string.
"""
from framework.utils import errors
from framework.forms.form import Form

class Controller(object):

    form = Form

    def __init__(self):
        """Declare class attributes."""
        self.request = None
        self.response = None
        self.form = None

    def __call__(self, request, response):
        """Call the controller instance."""
        self.request = request
        self.response = response

        # Order of operations for controller

        # Middleware
        # TODO write middleware

        # Form handling
        self.form = self._form_setup()
        if not self.form.validate():
            # Redirect back one page and apply errors.
            return 'Form Error: ' + str(self.form.errors)
        self.form.extract()

        # View handling
        return self.view()

    def _form_setup(self):
        """
        For initialising and setting up a form.
        """
        form = self.__class__.form()
        form.request = self.request
        return form

    def view(self):
        """
        This should be in charge of handling generating the view.
        If not implemented then throws http 500 error.
        """
        errors.abort(
            500,
            'Unimplemented view method in: ' +\
            self.__class__.__name__
        )