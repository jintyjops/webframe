"""Holds testing utilities."""

import random
import datetime
import string

class TestUtils:

    def str_random(self, length=10):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def email_random(self, length=10):
        return self.str_random(length) + '@example.com'

    def int_random(self, _min=0, _max=10000):
        return random.randrange(_min, _max)

    def fail(self, message='Failure manually induced.'):
        raise AssertionError(message)

    def bool_random(self):
        return bool(random.choice([0, 1]))

    def html_bool_random(self):
        return 'on' if bool(random.choice([0, 1])) else ''

    def date_random(self):
        return datetime.datetime.now()

tutils = TestUtils()