"""Runs unit tests."""

import sys
import traceback
import time

from webframe.tests.testutils import TestUtils
from webframe.tests import _assert
from webframe.models.model import Model
from webframe.core import app
from webframe.core.http.requests import Request, Body
from webframe.core.http.responses import Response
from webframe.core import wsgi

from webframe.core.http.session import Session, SessionMemoryStore

LINE_COUNT = 50

all_test_cases = {}
all_tests = {}

class _Watcher(type):

    def __init__(cls, name, bases, clsdict):
        super(_Watcher, cls).__init__(name, bases, clsdict)
        if name != 'TestCase':
            all_test_cases[name] = cls


class TestCase(TestUtils, metaclass=_Watcher):
    """Base test case."""

    def __init__(self, settings):
        self.settings = settings
        self.wsgiapp = None
        self.session = None

    def setup(self):
        self.wsgiapp = wsgi.WSGIApp(self.settings.APP)
        Session.StoreType = SessionMemoryStore
        self.session = Session(Request.mock())
        self.session.commit()
        Model.commit_external = True

    def teardown(self):
        SessionMemoryStore.sessions = {}
        app.db.rollback()
        app.db.close()

    def GET(self, url, data={}, previous=None):
        data['_token'] = self.session.csrf_token()
        environ = {
            'PATH_INFO': url,
            'REQUEST_URI': url,
            'HTTP_COOKIE': f'session={self.session.token}'
        }
        request = Request.mock(get=data, environ=environ)
        request.referer = previous
        return self.request(request)

    def POST(self, url, data={}, previous=None, json=False):
        data['_token'] = self.session.csrf_token()
        environ = {
            'PATH_INFO': url,
            'REQUEST_URI': url,
            'HTTP_COOKIE': f'session={self.session.token}'
        }
        body = Body()
        if json:
            body.json(data)
        else:
            body.urlencoded(data)

        request = Request.mock(body=body, environ=environ)
        request.referer = previous
        request.session = self.session
        return self.request(request)

    def request(self, request):
        response = Response(request)
        return self.wsgiapp.generate(request, response)

    def auth(self, user):
        """Authorize this user for the duration of the unit test."""
        self.session.store('_auth', user.id)
        self.session.commit()

class Test:
    def __init__(self, cls_name):
        self.cls_name = cls_name

    def __call__(self, func):
        """
        Decorator that marks this function as a test.
        Class methods which are decorated must be static (i.e. no self argument)
        """
        all_tests[func] = self.cls_name
        return func

def run_tests(settings, function=None):
    Tester(settings, all_tests, function).run()

class Tester:

    def __init__(self, settings, all_tests, function_filter=None):
        self.settings = settings
        self.all_tests = all_tests
        self.line_count = 0
        self.total = 0
        self.exceptions = {}
        self.assertion_errors = {}
        self.risky_tests = {}

        if function_filter is not None :
            self.all_tests = dict([
                [f, self.all_tests[f]] 
                for f in self.all_tests.keys() 
                if function_filter in f.__name__
            ])

    def run(self):
        start_time = time.time()

        for testfunc in self.all_tests.keys():
            clsInstance = all_test_cases[self.all_tests[testfunc]](self.settings)
            clsInstance.setup()
            try:
                testfunc(clsInstance)

                if _assert._AssertionCounter.getCount() <= 0:
                    self.print_status('R')
                    self.risky_tests[testfunc] = 'No assertions found in test.'
                else:
                    self.print_status('.')
            except AssertionError as e:
                self.assertion_errors[testfunc] = e
                self.print_status('F'),
            except Exception:
                self.exceptions[testfunc] = traceback.format_exc()
                self.print_status('E')
            finally:
                clsInstance.teardown()
            
            _assert._AssertionCounter.clearCount()

        self.print_end_status(start_time)

    def print_status(self, status):
        print(status, end='', flush=True)
        self.total += 1

        if self.total % LINE_COUNT == 0 and self.total != 0:
            self.print_line_end()
        if self.total == len(self.all_tests):
            self.print_line_end()
            
    def print_line_end(self):
        count = self.total % LINE_COUNT
        print(
            (' ' * (LINE_COUNT - (count if count else LINE_COUNT))) +\
            '\t(' + str(self.total) +\
            '/' +\
            str(len(self.all_tests)) +\
            ')'
        )

    def print_end_status(self, start_time):
        time_string = self.get_time_string(time.time() - start_time)
        end = 'No issues.'
        if len(self.exceptions) > 0:
            end = 'Errors found.'
        elif len(self.assertion_errors):
            end = 'Failures found.'
        elif(len(self.risky_tests) > 0):
            end = 'No failures, risky tests found.'
        
        print (
            str(len(self.all_tests)) +
            ' tests and ' +
            str(_assert._AssertionCounter.getTotal()) +
            ' assertions run in ' +
            time_string +
            '. ' +
            end
        )
        
        for func in self.exceptions.keys():
            self.print_exception('Error', func, self.exceptions[func])
        for func in self.assertion_errors.keys():
            self.print_exception('Assertion Error', func, self.assertion_errors[func])
        for func in self.risky_tests.keys():
            self.print_risky(func, self.risky_tests[func])

    def print_exception(self, type, func, ex):
        print('\n--------------------------------\n')
        print(type + ' when running ' + str(func))
        print(ex)

    def print_risky(self, func, info):
        print('\n--------------------------------\n')
        print('Risky test: ' + info)
        print(str(func))

    def get_time_string(self, seconds):
        _string = ''
        minutes = (seconds / (60)) % 60
        seconds = str((seconds) % 60)

        if len(seconds) > 4:
            seconds = seconds[:4]

        if minutes >= 1:
            _string += str(minutes) + ' minutes '
        _string += str(seconds) + ' seconds'

        return _string
