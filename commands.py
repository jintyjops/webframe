"""
Handles none runtime commands such as migrating data and unit tests.

available commands are as follows:
db:fresh
    create a fresh database with all tables in main/projects.
db:fresh seed
    same as migrate but seeds tables as well with registered seeders.
test
    run all unit tests.
test <function_name>
    run unit tests with a filter, this may match on more than one function.
register-models
    register or re-register all models. This should be run before migrate
    when new models have been added.
"""

import sys
import os
import glob
import time
import stringcase
from sqlalchemy import MetaData
from sqlalchemy_utils.functions import create_database, drop_database, database_exists
import webframe.models as models
from webframe.seeds import seeder
from webframe.tests import unittest

def parse_commands(settings):
    """Initiation point for parsing out of project runtime commands."""
    arg1 = None
    arg2 = None

    if len(sys.argv) > 1:
        arg1 = sys.argv[1]
    if len(sys.argv) > 2:
        arg2 = sys.argv[2]

    if arg1 == 'db:fresh':
        _reset_db(settings, arg2)
    elif arg1 == 'test':
        _test(settings, arg2)
    elif arg1 == 'register-models':
        register_models(settings)
    else:
        _usage()


def _reset_db(settings, arg):
    # Drop and recreate database if it exists.
    if database_exists(settings.DB_CONNECTION):
        print('dropping current database...')
        drop_database(settings.DB_CONNECTION)
    print('creating new database...')
    create_database(settings.DB_CONNECTION)
    print('creating tables...')
    start_time = time.time()
    models.model.Model.Base.metadata.create_all(settings.ENGINE, checkfirst=False)
    print('tables created in ' + str(time.time() - start_time)[:5] + ' seconds.')

    if arg == 'seed':
        seeder.run_seeds(settings.seed_list, settings.ENGINE)

def _test(settings, arg):
    unittest.run_tests(settings, arg)

def register_models(settings):
    initfile = settings.APP_LOCATION + '/models/__init__.py'
    modelfiles = glob.glob(settings.APP_LOCATION + '/models/*.py')
    modelfiles = [os.path.basename(p).split('.py')[0] for p in modelfiles]
    modelfiles.remove('__init__')

    str = "\n".join(['from .' + i + ' import ' + stringcase.pascalcase(i) for i in modelfiles])
    
    with open(initfile, 'w') as init:
        init.write(str)

def _usage():
    print(__doc__)

    

