"""
Useful variables that the whole program should have access to.

Made this way so that parts of the program called from the user app
can access the settings module.
"""

# The implementing app
userapp = None

# The router
router = None

# The DB session
db = None