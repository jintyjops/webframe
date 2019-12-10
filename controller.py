"""
Base controller for the application.
There will be one controller per page/view.
Each controller will implement a view method which will be in
charge of returning a string.
"""
from framework.utils import errors
from framework.utils import views
from framework.utils.auth import auth
from framework.forms.form import Form
from framework.core import app

class Controller(object):

    # The form to use. Default to None.
    form = None
    # The model to fetch from the REST params in the url.
    model = None
    model_id = None
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

        self.request.model = self._get_model_or_404()

        # Form handling
        self.form = self._form_setup()

        if self.form is not None:
            if not self.__class__.self_validating and not self.form.validate():
                self.form_invalid()
            self.form.extract()

        # View handling
        try:
            return self.view()
        finally:
            self._run_middleware_after()

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

    def _run_middleware_after(self):
        """
        Similar to __run_middleware(), except it is just global middleware.
        """
        middleware = app.userapp.settings.GLOBAL_AFTER_MIDDLEWARE

        for mware in middleware:
            mware(self.request, self.response)

    def _get_model_or_404(self):
        """
        Returns the model if model and model_id are set.
        Throws 404 not found if model cannot be found.
        Assigns the fetched model to model_name or the lowercase name of model.
        """
        model = self.__class__.model
        model_id = self.__class__.model_id
        if model is None or model_id is None:
            return None

        record = model.find(self.request.url_param(model_id))

        if record is None:
            errors.abort(
                404,
                'Unable to find record.'
            )

        return record


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

    def template(self, template, arguments={}, tokens=0):
        """
        Create a view with standard controller arguments.
        Arguments include, flash data, alerts, old input, errors.
        """
        arguments['_tokens'] = self.get_tokens(tokens)
        arguments['alerts'] = self._get_alerts()
        arguments['errors'] = self._get_errors()
        arguments['old'] = self._get_old_input()
        #  Only add authuser if it does not exist.
        try:
            arguments['authuser']
        except KeyError:
            arguments['authuser'] = auth(self.request).user()
        return views.view(template, arguments)

    def old(self, name):
        """Utility method to look in flash['old'] without throwing ke error."""
        try:
            old = self.request.session.get_flash('old')
            if old is None:
                return None
            return old[name]
        except KeyError:
            return None

    def get_tokens(self, num_tokens):
        """Get a list of newly created and valid csrf tokens."""
        return [self.request.session.new_csrf() for i in range(num_tokens)]

    def _get_alerts(self):
        """Return dict of alerts passed in session flash."""
        alerts = {}
        success = self.request.session.get_flash('alert-success')
        if success:
            alerts['success'] = success
        danger = self.request.session.get_flash('alert-danger')
        if danger:
            alerts['danger'] = danger

        return alerts

    def _get_errors(self):
        """Get errors from flash or return empty dict."""
        errors = self.request.session.get_flash('errors')
        if errors is None:
            return {}

        return errors            

    def _get_old_input(self):
        """Get the old form input or return an empty dict."""
        old = self.request.session.get_flash('old')
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