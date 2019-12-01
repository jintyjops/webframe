"""
Base controller for the application.
There will be one controller per page/view.
Each controller will implement a view method which will be in
charge of returning a string.
"""
from framework.utils import errors
from framework.utils import views
from framework.forms.form import Form
from framework.core import app

class Controller(object):

    # The form to use. Default to None.
    form = None
    # defines if the subclass of this controller will handle validation.
    self_validating = False

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
        self.__run_middleware()

        # Form handling
        self.form = self._form_setup()

        if self.form is not None:
            if not self.__class__.self_validating and not self.form.validate():
                self.form_invalid()
            self.form.extract()

        # View handling
        return self.view()

    def __run_middleware(self):
        """
        Run the middleware for the route.
        Returning from middleware will do nothing. The middleware should
        either call abort() or response.force_redirect()
        """
        # To collect: global middleware, route specific middleware.
        # Global middleware takes priority.
        middleware = app.userapp.settings.GLOBAL_MIDDLEWARE +\
                     self.request.route.middleware

        for mware in middleware:
            mware(self.request, self.response)

    def _form_setup(self):
        """
        For initialising and setting up a form.
        """
        if not self.__class__.form:
            return
        form = self.__class__.form()
        form.request = self.request
        return form

    def form_invalid(self):
        """What to do if the form is invalid."""
        # Flash old input to session for later use.
        self.request.session.flash('old', self.form.params)
        # Flash Errors
        self.request.session.flash('errors', self.form.errors)
        # Redirect to previous url
        self.response.force_redirect_back()

    def template(self, template, arguments={}):
        """
        Create a view with standard controller arguments.
        Arguments include, flash data, alerts, old input, errors.
        """
        arguments['alerts'] = self._get_alerts()
        arguments['errors'] = self._get_errors()
        arguments['old'] = self._get_old_input()
        return views.view(template, arguments)

    def _get_alerts(self):
        """Return dict of alerts passed in session flash."""
        alerts = {}
        success = self.request.session.getFlash('alert-success')
        if success:
            alerts['success'] = success
        danger = self.request.session.getFlash('alert-danger')
        if danger:
            alerts['danger'] = danger

        return alerts

    def _get_errors(self):
        """Get errors from flash or return empty dict."""
        errors = self.request.session.getFlash('errors')
        if errors is None:
            return {}

        return errors            

    def _get_old_input(self):
        """Get the old form input or return an empty dict."""
        old = self.request.session.getFlash('old')
        if old is None:
            return {}
        
        return old

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