"""Runs unit tests."""

import traceback
import time

LINE_COUNT = 50

all_test_cases = {}
all_tests = []

class _Watcher(type):

     def __init__(cls, name, bases, clsdict):
        super(_Watcher, cls).__init__(name, bases, clsdict)
        if name != 'TestCase':
            all_test_cases[name] = cls


class TestCase(metaclass=_Watcher):
    pass

def test(func):
    all_tests.append(func)
    return func

def run_tests(function=None):
    Tester(all_tests, function).run()

class Tester:

    def __init__(self, all_tests, function=None):
        self.all_tests = all_tests
        self.line_count = 0
        self.total = 0
        self.exceptions = {}
        self.assertion_errors = {}

        if function is not None :
            self.all_tests = [f for f in self.all_tests if f.__name__ == function]

    def run(self):
        start_time = time.time()

        for testfunc in self.all_tests:
            try:
                testfunc()
            except AssertionError as e:
                self.assertion_errors[testfunc] = traceback.format_exc()
                self.print_status('F'),
            except Exception as e:
                self.exceptions[testfunc] = traceback.format_exc()
                self.print_status('E')
            else:
                self.print_status('*')

        self.print_end_status(start_time)

    def print_status(self, status):
        print(status, end='')
        self.total += 1

        if self.total % LINE_COUNT == 0 and self.total != 0:
            self.print_line_end()
        if self.total == len(self.all_tests):
            self.print_line_end()
            
    def print_line_end(self):
        print('\t(' + str(self.total) + '/' + str(len(self.all_tests)) + ')')

    def print_end_status(self, start_time):
        time_string = self.get_time_string(time.time() - start_time)
        if len(self.exceptions) == 0 and len(self.assertion_errors) == 0:
            print (
                str(len(self.all_tests)) + ' tests run in ' + time_string + '. No Errors.'
            )
        
        for func in self.exceptions.keys():
            self.print_exception('Error', func, self.exceptions[func])
        for func in self.assertion_errors.keys():
            self.print_exception('Assertion Error', func, self.assertion_errors[func])

    def print_exception(self, type, func, ex):
        print('\n--------------------------------\n')
        print(type + ' when running ' + str(func))
        print(ex)

    def get_time_string(self, millis):
        string = ''
        minutes = (millis / (1000 * 60)) % 60
        seconds = (millis / 1000) % 60

        if minutes >= 1:
            string += str(minutes) + ' minutes '
        string += str(seconds) + ' seconds'

        return string
