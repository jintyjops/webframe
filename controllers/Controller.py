"""
Base controller for the application.
There will be one controller per page/view.
Each controller will implement a view method which will be in
charge of returning a string.
"""
from framework.utils import errors

class Controller(object):

    def __init__(self):
        """Declare class attributes."""
        self.request = None
        self.response = None
        self.form = None

    def __call__(self, request, response):
        """Call the controller instance."""
        self.request = request
        self.response = response

        self.form = self.form_setup()
        return self.view()

    def form_setup(self):
        """
        For initialising and setting up a form.
        Implement if this controller will handle form input.
        """
        return None

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