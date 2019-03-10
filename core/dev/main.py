from threading import Thread
import sys
from importlib import reload
import time
import waitress
import checksumdir
import framework.core.wsgi as wsgi
import framework.core.app as frameworkapp


class DevApp(object):
    """Development server and application."""

    def __init__(self, app):
        self.app = app
        self.server_thread = None
        self.old_module_val = None

        try:
            self.__make_server()
            self.__check_shutdown()
        except KeyboardInterrupt:
            if self.server_thread:
                self.server_thread.close()

    def __check_shutdown(self):
        while True:
            time.sleep(0.1)
            if self.__has_changed(self.app.__file__ + '/../') or self.server_thread.failed:
                self.server_thread.close()
                try:
                    self.__make_server()
                except Exception as e:
                    print(e)
                    self.server_thread.failed = False


    def __has_changed(self, path):
        new_val = checksumdir.dirhash(path)
        if new_val != self.old_module_val:
            self.old_module_val = new_val
            return True
        return False

    def __make_server(self):
        # start server
        self.__reload_app(self.app)
        wsgiapp = wsgi.WSGIApp(self.app)
        self.server_thread = DevServerThread(
            self.app.settings,
            wsgiapp
        )
        # Don't let server thread continue if main thread goes down.
        self.server_thread.daemon = True
        print('starting new server...')
        self.server_thread.start()

    def __reload_app(self, userapp):
        """Reload the app."""
        # This is hacky and horrible.
        for module in sys.modules:
            if module.split('.')[0] == userapp.__name__:
                reload(sys.modules.get(module))
        reload(frameworkapp)


class DevServerThread(Thread):

    def __init__(self, settings, wsgiapp):
        Thread.__init__(self)
        self.settings = settings
        self.wsgiapp = wsgiapp
        self.server = None
        self.failed = False

    def run(self):
        domain = self.settings.HOST
        if self.settings.PORT:
            domain += ':' + str(self.settings.PORT)
        try:
            self.server = waitress.server.create_server(self.wsgiapp, listen=domain, channel_timeout=1)
            self.server.run()
        except:
            print('server failed, retrying...')
            self.failed = True

    def close(self):
        self.server.close()
