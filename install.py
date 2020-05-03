"""Installer for the project."""

import sys
import os

args_to_get = {
    'name': {
        'text': 'Enter name for your application',
        'validation': []
    }
}

to_make = {
    'folders': [
        'controllers',
        'forms',
        'models',
        'resources',
        'resources/templates',
        'routes',
        '../storage',
        '../storage/logs',
        '../storage/sessions',
    ],
    'files': {

# FILE
'controllers/controllers.py': 
"""
from webframe.controller import Controller

class ExampleGETController(Controller):

    def view(self):
        \"\"\"An example of a simple GET Controller.\"\"\"
        return self.template('webframe.html')
""",

# FILE
'resources/templates/webframe.html':
"""
<html>
    <head>
        <style>
            body {
                color: #2d3436;
                font-family: sans-serif;
            }

            div.center {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 70%;
                text-align: center;
            }

            .green {
                background-color: #00b894;
                color: white;
                border-radius: 5px;
                width: 300px;
                padding: 5px;
            }
        </style>
    </head>
    <body>
        <div class="center">
            <h1 class="green">It Worked!</h1>
            <h1>Welcome to WebFrame</h1>
            <table>
                <tr>
                    <td>Current Version:</td>
                    <td>v0.1 alpha</td>
                </tr>
            </table>
            <p>
                You can find more information at <a href="https://github.com/jintyjops/webframe">https://github.com/jintyjops/webframe</a>
                <br>
                <br>
                Or you can contact me at <a href="">patricksheppardd@gmail.com</a>
            </p>
        </div>
    </body>
</html>
""",

# FILE
'routes/route.py':
"""
from {%name%}.controllers.controllers import ExampleGETController

routes = [
    {
        'path': '/',
        'command': ExampleGETController(),
        'name': 'GETExample',
        'method': 'GET',
        'middleware':[]
    },
]
""",

# FILE
'routes/__init__.py':
"""
from {%name%}.routes import route
""",

# FILE
'__init__.py':
"""
import {%name%}.settings
import {%name%}.routes as routes
""",

# FILE
'wsgi.py':
"""
\"\"\"WSGI handler for starting the app.\"\"\"

import logging
from webframe.core.wsgi import WSGIApp, app_setup
import {%name%}
from {%name%} import settings

logging.info('Starting web app...')
logging.info('Running setup...')
settings.app_setup()
logging.info('Setup complete.')
logging.info('Waiting for requests :)')

def app(environ, start_response):
    wsgi_app = WSGIApp({%name%})
    return wsgi_app(environ, start_response)
""",

# FILE
'settings.py':
"""
# connection data
import logging
from webframe.utils import storage
from webframe.config import config, config_bool, config_int
import {%name%}

HOST = config('host')
PORT = config_int('port')
USING_SSL = config_bool('using_ssl')
MAX_CONNECTIONS = 1
SESSION_EXPIRY = 3600

APP_NAME = config('app_name')
APP_LOCATION = config('app_location')
APP = {%name%}

# Files and other data are stored here.
STORAGE_DIR = config('storage_dir')

# Is the app in debug mode
DEBUG = config_bool('debug')

# Authorization/login/logout
# The model which authorization is performed on (usually user).
AUTH_MODEL = None

# public resoures
RESOURCE_URL = config('resource_url')
RESOURCE_DIR = config('resource_dir')
# whether the app should serve resources itself (not recommended outside of development)
SERVE_PUBLIC = config_bool('serve_public')
TEMPLATES = config('templates_dir')

# DB data 
DB_TYPE = config('db_type')
DB_ENGINE = config('db_engine')
DB_USER = config('db_user')
DB_PASS = config('db_pass')
DB_IP = config('db_ip')
DB_PORT = config_int('db_port')
DB_NAME = config('db_name')

################
# DB
################
from {%name%}.models import *
from sqlalchemy import create_engine
from webframe.utils import db
DB_CONNECTION = db.get_connection_string(DB_TYPE, DB_ENGINE, DB_USER, DB_PASS, DB_IP, DB_PORT, DB_NAME)
ENGINE = create_engine(DB_CONNECTION, pool_recycle=60)

################
# Templates
################
from jinja2 import Environment, PackageLoader, select_autoescape
from webframe.utils.routes import resource, url
template_env = Environment(
    loader=PackageLoader('{%name%}', TEMPLATES),
    autoescape=select_autoescape(['html', 'xml']),
)

def globalTemplateArgs():
    return {
        # Add named global template args here.
    }

################
# Middleware
################
from webframe import middleware
GLOBAL_MIDDLEWARE = [
    # Middleware to be run before the request is processed.
    middleware.session.fetch_or_create_session,
    middleware.session.set_session_token_on_response,
]

GLOBAL_AFTER_MIDDLEWARE = [
    middleware.session.session_commit
]

seed_list = [
    # Place all seeders here.
]

ERROR_HANDLERS = {
    # Custom error handlers
}

################
# Post initial setup
################

from webframe.core import wsgi
callbacks = []
def app_setup():
    \"\"\"Setup the app.\"\"\"
    wsgi.app_setup(APP)
    
    # Logging
    if not storage.folder_exists('logs'):
        storage.make_folder('logs')
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        filename=storage.path('logs', 'main.log'),
        level=logging.DEBUG if DEBUG else logging.INFO
    )
""",

# FILE
'../dev.py':
"""
\"\"\"Run the server.\"\"\"
import os
import subprocess
from webframe.core.dev import main
from {%name%} import wsgi
import {%name%}
from {%name%} import settings

main.DevApp({%name%})

""",

# FILE
'../project.py':
"""
\"\"\"Run commands for the project such as migration and unit test.\"\"\"

import sys
from webframe import commands
from {%name%} import settings

if __name__ == '__main__':
    commands.parse_commands(settings)
""",

# FILE
'../settings.conf':
"""
// Is the app in debug mode
debug=true

host=localhost
port=8000
using_ssl=false
app_name={%name%}
app_location={%name%}

// Storage for sessions and log files
storage_dir=storage
// Public resource url
resource_url=/public
// Resource location
resource_dir={%name%}/public
// If the app serves its own public files
serve_public=true

// Location of templates
templates_dir=resources/templates

// Database settings
db_type=mysql
db_engine=pymysql
db_user=root
db_pass=
db_ip=127.0.0.1
db_port=3306
db_name=
""",
    }
}

def get_args():
    fetched = {}
    for name, arg in args_to_get.items():
        while True:
            valid = True
            val = input(f'{arg["text"]} ->')
            for validation in arg['validation']:
                if not validation(val):
                    print(f'Invalid value for {name}')
                    valid = False
            if valid:
                fetched[name] = val
                break
    return fetched

def install():
    """Create new application from parameters."""
    args = get_args()
    print()
    for name, val in args.items():
        print(f'{name}: {val}')
    while True:
        confirm = input('Are you happy with the above information? (Y/n) ->').strip().lower()

        if confirm.lower() in ('yes', 'y'):
            break
        elif confirm in ('no', 'n'):
            print('Exiting...')
            sys.exit()
        else:
            print('Please type yes or no.')

    # Install here.
    print('Installing...')

    current = os.path.abspath(__file__)

    root = make_folders(current, args['name'])
    make_files(root, args)

    print('Done.')
    print('Run "python dev.py" to start the server.')
    print('Server be accessed at "localhost:8000" by default.')
    print('For more information see: https://github.com/jintyjops/webframe')

def make_folders(current, appname):
    """Make root folder "appname" and folders under root."""
    root = os.path.join(os.path.dirname(current), f'../{appname}')
    os.mkdir(root)

    for folder in to_make['folders']:
        os.mkdir(os.path.join(root, folder))
    
    return root

def make_files(root, args):
    """Write data to files."""

    for filename, data in to_make['files'].items():
        print(f'Creating: "{filename}"...')
        for name, val in args.items():
            data = data.replace('{%' + name + '%}', val)
        with open(os.path.join(root, filename), 'w') as f:
            f.write(data)

if __name__ == "__main__":
    install()