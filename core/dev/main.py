"""
Development server.

DO NOT USE IN PRODUCTION!
"""

# ALL YE WHO ENTER TREMBLE IN FEAR. HERE BE DRAGONS.

from threading import Thread
import sys
import subprocess
import os
import signal
import __main__
import traceback
import time
import checksumdir
import waitress
import logging
import framework.core.wsgi as wsgi
import framework.core.app as frameworkapp
import framework.models.model as model


class DevApp(object):
    """Development server and application."""

    def __init__(self, app):
        self.app = app
        self.server_thread = None
        self.old_module_val = None

        try:
            if sys.argv[1] == 'run-once':
                self._run_server()
        except IndexError:
            self._dev_thread()

    def _dev_thread(self):
        """The main thread which runs the server."""
        while True:
            time.sleep(0.1)

            hasChanged = self._has_changed(self.app.__file__ + '/../')
            hasDied = self.server_thread is not None and self.server_thread.poll() is not None
            
            if hasChanged or hasDied:
                try:
                    # SIGHUP is the signal to kill waitress.
                    # See https://github.com/Pylons/waitress/pull/48 
                    os.kill(self.server_thread.pid, signal.SIGHUP)
                except AttributeError:
                    pass
                self.server_thread = self._make_new_server_thread()

    def _make_new_server_thread(self):
        """Creates a new subprocess of server thread."""
        cmd = sys.executable + ' ' + os.path.abspath(__main__.__file__) + ' run-once'
        return subprocess.Popen(cmd, shell=True)

    def _run_server(self):
        print('starting new server...')
        wsgiapp = wsgi.WSGIApp(self.app)
        domain = self.app.settings.HOST
        if self.app.settings.PORT:
            domain += ':' + str(self.app.settings.PORT)
        logging.getLogger('waitress').setLevel(logging.ERROR)
        waitress.serve(wsgiapp, listen=domain)

    def _has_changed(self, path):
        new_val = checksumdir.dirhash(path)
        if new_val != self.old_module_val:
            self.old_module_val = new_val
            return True
        return False
