from threading import Thread
from importlib import reload
import time
import waitress
import checksumdir
import framework.core.wsgi as wsgi


class DevApp(object):
    """Development server and application."""

    def __init__(self, app):
        self.app = app
        self.server_thread = None
        self.old_module_val = None

        self.__make_server()
        self.__check_shutdown()

    def __check_shutdown(self):
        while True:
            time.sleep(0.1)
            if self.__has_changed(self.app.__file__ + '/../'):
                print('closing server')
                self.server_thread.close()
                self.app = reload(self.app)
                self.__make_server()

    def __has_changed(self, path):
        new_val = checksumdir.dirhash(path)
        if new_val != self.old_module_val:
            self.old_module_val = new_val
            return True
        return False

    def __make_server(self):
        # start server
        self.server_thread = DevServerThread(
            self.app.settings
        )
        # Don't let server thread continue if main thread goes down.
        self.server_thread.daemon = True
        print('starting new server')
        self.server_thread.start()


class DevServerThread(Thread):

    def __init__(self, settings):
        Thread.__init__(self)
        self.settings = settings
        self.server = None

    def run(self):
        domain = self.settings.HOST
        if self.settings.PORT:
            domain += ':' + str(self.settings.PORT)
        self.server = waitress.server.create_server(wsgi.app, listen=domain)
        self.server.run()

    def close(self):
        self.server.close()
