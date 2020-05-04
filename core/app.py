"""
Useful variables that the whole program should have access to.

Made this way so that parts of the program called from the user app
can access the settings module.
"""

from threading import Semaphore
from webframe.utils import db

class App():
    """
    An interface to the users application as well as external connections
    such as the database. In short it is a storage location for important
    data.
    """

    # The implementing application.
    _userapp = None
    # The router instance.
    _router = None
    # The databse session.
    _db = None
    # The connection pool
    _conn_pool = None

    def settings(self):
        """Get the settings module of the implementing application."""
        return App._userapp.settings

    def routes(self):
        """Get the list of routes on the implementing application."""
        return App._userapp.routes.route.routes

    def router(self):
        """Get the router instance."""
        return App._router

    def db(self):
        """Get the database session instance."""
        return App._db

    def conn_pool(self):
        """Get the connection pool Sempaphore for this instance."""
        return App._conn_pool

    @staticmethod
    def app_setup(usersapp):
        """Set up global variables."""
        # import here to avoid circular dependency issues.
        from webframe.core.route import Router
        App._userapp = usersapp
        App._router = Router(App._userapp.routes.route.routes)
        if App._db is not None:
            App._db.close()
        App._db = db.make_session(App._userapp.settings.ENGINE)
        if App._conn_pool is None:
            App._conn_pool = Semaphore(App._userapp.settings.MAX_CONNECTIONS)