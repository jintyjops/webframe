"""
A collection of assertion functions.

Each throws an AssertionError when condition is not met.
"""

def true(condition):
    if not condition:
        raise AssertionError('Failed asserting ' + str(condition) + ' is true.')

def false(condition):
    if not condition:
        raise AssertionError('Failed asserting ' + str(condition) + ' is false.')

def equals(val1, val2):
    if val1 != val2:
        raise AssertionError(
            'Failed asserting ' + str(val1) + ' == ' + str(val2)
        )

def not_equals(val1, val2):
    if val1 == val2:
        raise AssertionError(
            'Failed asserting ' + str(val1) + ' != ' + str(val2)
        )

def contains(val, ls):
    if val not in ls:
        raise AssertionError(
            'Failed asserting that ' + str(val) + ' is in ' + str(ls)
        )

