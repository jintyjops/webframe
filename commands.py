"""
Handles none runtime commands such as migrating data and unit tests.

migrate tables:             project.py migrate
migrate tables and seed:    project.py migrate seed
run unit tests:             project.py test
run specific unit test:     project.py test <function_name>

(note: the migrate command deletes the database and creates a fresh one.)
"""

import sys
from sqlalchemy_utils.functions import create_database, drop_database, database_exists
import framework.models as models
from framework.seeds import seeder
from framework.tests import unittest

# Import all models here.
from testapp.models import *

def parse_commands(settings):
    """Initiation point for parsing out of project runtime commands."""
    arg1 = None
    arg2 = None

    if len(sys.argv) > 1:
        arg1 = sys.argv[1]
    if len(sys.argv) > 2:
        arg2 = sys.argv[2]

    if arg1 == 'migrate':
        _migrate(settings, arg2)
    elif arg1 == 'test':
        _test(settings, arg2)
    else:
        _usage()


def _migrate(settings, arg):
    # Drop and recreate database if it exists.
    if database_exists(settings.DB_CONNECTION):
        print('dropping current database...')
        drop_database(settings.DB_CONNECTION)
    print('creating new database...')
    create_database(settings.DB_CONNECTION)
    print('creating tables...')
    models.model.Base.metadata.create_all(settings.ENGINE)

    if arg == 'seed':
        seeder.run_seeds(settings.seed_list, settings.ENGINE)


def _test(settings, arg):
    unittest.run_tests(arg)


def _usage():
    print(__doc__)

    

