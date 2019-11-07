"""Holds testing utilities."""

import random
import string

class TestUtils:

    def str_random(self, length=10):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def int_random(self, _min=0, _max=10000):
        return random.randrange(_min, _max)

    def fail(self, message='Failure manually induced.'):
        raise AssertionError(message)