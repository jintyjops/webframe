# Web Frame
A simple WSGI based web framework.
This framework was made for a university project. It is still very much under development and you may encounter bugs or incomplete features.

## Installation
Web Frame requires python 3.7 or above.
It is recommended to use Pipenv to install dependencies. The Pipfile has been included.

### Steps:
 1. Clone the web frame repository.
 2. Install the dependencies from the Pipfile and start the Pipenv.
 3. Run `python webframe/install.py` which will guide you through the steps to create a simple application. For the purposes of this documentation the application will be called `myapp`.
 4. At this stage you should have a folder structure that looks like this:
```
│   dev.py
│   project.py
│   settings.conf
├───myapp
│   │   settings.py
│   │   wsgi.py
│   │   __init__.py
│   ├───controllers
│   │       controllers.py
│   ├───forms
│   ├───models
│   ├───resources
│   │   └───templates
│   │           webframe.html
│   └───routes
│           route.py
│           __init__.py
├───storage
│   ├───logs
│   └───sessions
└───webframe
    └───core web frame modules...
```
5. Test that it works by running `python dev.py` and going to `http://localhost:8000` in your browser.

## The Development Server
A development server is included with Web Frame, it simply checks the application folder `myapp` for changes and restarts if any are detected. It will also restart if a fatal error is encountered (syntax errors for example).
This behaviour can be disabled by specifying the `run-once` flag (`python dev.py run-once`). This will disable auto restarting of the server and change detection.
## Handling Requests
Web Frame uses a routes file to direct incoming requests to specific controllers. A controller is simply any callable which takes a Request and Response object and returns a string.
### Request and Response Objects
Web Frame makes heavy use of the WebOb library and the `Request` and `Response` objects passed to controllers are simply extensions of those defined in the WebOb library. More information can on WebOb can be found [here](https://docs.pylonsproject.org/projects/webob/en/stable/)
### Routing
The routes file is defined in `routes/route.py` and is simply a list of defined routes that the framework will check when it received a request.
```
routes =  [
	{
		'path':  '/', 					  # The path of the route
		'command':  exampleGETController, # The controller callable (takes Request and Response objects)
		'name':  'GETExample', 			  # The name of the route for url generation.
		'method':  'GET', 				  # The method of the route (only GET and POST are supported as of now)
		'middleware':[] 				  # route middleware (see middleware section)
	},
	{
		'path':  '/submit',
		'command':  examplePOSTController,
		'name':  'POSTExample',
		'method':  'POST',
		'middleware':[]
	},
]
```

 - `path` is the path that of that route, it may be parameterised using the `{param}` syntax. For example: `/edit/user/{user_id}`.  The user id parameter can then be accessed in the controller with `request.url_param('user_id')`.
 - `command` is the controller to call when the route `path` is matched to a request URL. It takes `Request` and `Response` objects and returns either a string or a `FileApp` object (see [WebOb Documentation](https://docs.pylonsproject.org/projects/webob/en/stable/api/static.html#webob.static.FileApp)) and "Serving Public?" section).
 - `name` can be considered a label for a route. It can be used to generate a URL using the `url(route_name)` function found in `webframe.utils.route`.
 - `method` simply defines the request method that this route accepts. Currently only `GET` and `POST` are supported.
 - `middleware` is where the middleware to be run on the route is set. This is talked about more the "Middleware" section below.
### Controllers
Controllers may be any callable which take a `Request` and `Response` object in the form `controller(request, response)` These must return either a string, which will become the body of the request or a [`FileApp`](https://docs.pylonsproject.org/projects/webob/en/stable/api/static.html#webob.static.FileApp) object.
An example of a very basic controller would be:
```
def helloworld(request, response):
	return '<h1>Hello World!</h1>' # This becomes the body of the request.
```
*Note, this type of controller will not run middleware. You must use the* `Controller` *class for that.*

Controllers can also extend the `Controller` class which can be found in `webframe.controller`. This class provides a structured way of handling requests and will do a lot of repetitive work for you.
The `Controller` class version of the simple controller above is:
```
from webframe.controller import Controller
class  ExampleController(Controller):
	def  view(self):
		return '<h1>Hello World!</h1>'
```
The route example for this type of controller is:
```
from myapp.controllers import ExampleController
{
	'path':  '/controller/example',
	'command':  ExampleController(), # Controller object must be instantiated.
	'name':  'controller.example',
	'method':  'GET',
	'middleware':[]
}
```
As you can see in the example above, the `view()` method is used to handle the request.
Let's have a look at a more complicated controller that uses a lot more of the power of the `Controller` class as well as sessions and database connectivity.
```
from myapp.models.user import User
from myapp.forms.user_forms import UserNameEditForm
class  UserNameEditController(Controller):
	model=User
	model_id='user_id'
	form=UserNameEditForm
	def  view(self):
		self.request.model.name = self.request.input('name')
		self.request.model.save()
		self.request.session.flash('alert-success', 'User Successfully Saved')
		return self.response.redirect_back()
```
As you can see, there is a lot more to understand here. Let's break it down:

 - The `model` static field points to a `User` model, this is the model that the controller will try and fetch from the database based the url parameter `user_id`, whose value is the primary key of the `User` model (see the "Database Connectivity" section). This fetched model instance is then available in the `view()` method with `self.model`. If the model record is not found a 404 error is thrown automatically.
 - The `form` static field defines a form that is automatically checked before `view()` method called. If the form is invalid, it will redirect (301) back to the previous route and the errors are then flashed to the session. For more information on this see the "Forms" section below as well as the "Sessions" section.
 - If the model is fetched and the form submitted is valid. Then the `view()` method is then called. This begins by getting the fetched model from the request using `self.request.model`. It then fetches the `name` field from the request using the `self.request.input(field_name)` method.
 - The model is then saved.
 - A success alert is then flashed to the session. This message will be saved for one more request before being destroyed.
 - A redirect response is then returned using `self.response.redirect_back()`. This uses the `Referer` HTTP header to find the route that the user came from.

## Forms
Forms are used for validating submitted HTML forms. Although they are an optional part of Web Frame, they are quite powerful and should be used where necessary.
Forms are usually defined in the `myapp/forms` directory however they can be defined anywhere and used in `Controller` classes (see "Controllers" section above).
Following from the Controller example above, an example form to edit a users name may be:
```
from webframe.forms.form import Form
from webframe.forms import validation as v
class  UserEditForm(Form):
	def  rules(self):
		return  {
			'name':  [ 				# The name of the field to be checked.
				v.required(),		# The field is required
				v.max_len(255),		# The field must be shorter than 255 characters
				v.min_len(2)		# The field length must be greater or equal to 2 characters
			],
		}
	def  extract(self): 					# This is called automatically
		self.name  = self.input('name')		# Extract the name and assign it to the form.
```
The example above defines several rules that the name field must follow:
 - It is a required field. If it does not exist or is empty then it form validation will fail.
 - It must be no more than 255 characters long.
 - It must be longer than 2 characters long.

If all the above rules are met, the form is declared as valid.
Many more validation rules exist in the system. These are:

 - `required`: requires that the field exists and is not empty.
 - `max_len`: requires that the field is no longer than the given number of characters.
 - `min_len`: requires that the field is no shorter than the given number of characters.
 - `email`: validates email against [RFC 5322 Regex](https://emailregex.com/)
 - `unique`: requires that the field not exist on the given table/colum combination given to the validator, this excludes certain values given in the exclude parameter (e.g. `unique(User, name, exlude=[self.request.model.id])`).
 - `integer`: requires that the field be an integer of optional min and max sizes.
 - `exists`: requires that the given table/column exists with the value of the field in the database.
 - `confirm`: requires that a second field exist on the form with the extension `_confirm` and has the same value (e.g. if `password` is the field then confirm requires that `password_confirm` also exists and contains the same value as `password`).
 - `isin`: requires that the fields value exists in the given list.
 - `file_required`:  a special form of require that checks for the existence of a file.
 - `_file`: requires that a file exists and conforms to the given mimetypes (e.g. application/pdf, image/png, etc...) and is no bigger than the max_size given.

You can also define more types of validators if you need them. Please check the source code at `webframe/forms/validation.py` for examples of how to do this.

## Templates
Web Frame uses the Jinja2 HTML templating library. For more information on how to use this see the [Jinja 2 Documentation.](https://jinja.palletsprojects.com/en/2.11.x/).
The templates directory is set in the `settings.conf` file. Usually a template will be called with the `Controller` classes `template()` method. This provides some extra functionality, such as gathering alerts authorised users, csrf tokens, old field data, form error data and passing those data to the template as arguments.
Other than this, the `webframe.utils.views` utility can be used for template generation, and in fact the `template()` method is simply a wrapper around these utilities. See the "Utilities" section for more information.
## Sessions
Sessions are handled somewhat automatically by Web Frame. As of the time of writing, the session handling portion of the system is the biggest bottleneck in multi-threaded performance and this will be addressed in a later revision.
There are two types of Session stores, the `SessionFileStore` and the `SessionMemoryStore`. The former is the default and will store session data in the `storage/sessions` folder while the latter stores data directly in memory, this is mostly used for testing purposes (see "Testing" section below). To set a new session store simply assign the `StoreType` static field on `webframe.core.http.session.Session` to the new memory store class you wish to use.

The session for a user is automatically fetched when using a `Controller` instance and can be accessed with `self.session`. The session defines several useful methods for storing data:

 - `store(key, value)` will store a value indefinitely in the session.
 - `get(key)` will get a stored value or return None.
 - `delete(key)` will delete a value from the session.
 - `flash(key, value)` will store a value for one request/response cycle in the session.
 - `get_flash(key)` will return flashed data or None.
 - `flash_data()` will get the entire session flash as a dictionary.
 - `destroy()` will destroy the current session and start a new one.
 - `csrf_token()` will generate a session token and return it. If you are using the `Controller` class with the `template()` method you shouldn't have to use this.
 - `check_csrf(token_to_check)` will check the given csrf token against the sessions token. You shouldn't have to use this with the global `check_csrf_on_post` middleware set up.

## Middleware
Middleware, as the name suggests, is designed to run before or after the main controller is called. 
Like a controller, the middleware is simply a callable which takes a `Request` and `Response` object. The difference lies in that it does not return anything. Instead, it can set values on the system, gather values to be passed to the template, or raise errors (either general errors or redirection errors, which are picked up further upstream).
An example of a completely useless middleware is as follows:
```
def example_middleware(request, response):
	print('The middleware is running!')
```

There are 3 distinct kinds of middleware in the system:
- Per route:
This is set in the route parameters. For example if you wanted to add our example above to run in a route before the controller you would do:
```
{
	'path':  '/',
	'command':  example_controller,
	'name':  'middleware.example',
	'method':  'GET',
	'middleware':[
		example_middleware
	]
}
```

- Global:
This middleware is set in the `settings.py` file in the `GLOBAL_MIDDLEWARE` list. It works the same as in the above example except that this middleware will be run for every route in the system.

- Global after:
This is similar to the global middleware except it is set in the `GLOBAL_AFTER_MIDDLEWARE` list and, as the name suggests, it 		is run on every route *after* the controller is called.

To set template arguments in middleware, you can simply set the values in the `response.template_args` dictionary. For example `response.template_args['main_menu_title'] = 'My App'`
*Note: at the time of writing, middleware is only run when using the* `Controller` *class.*

## Database Connectivity
Database connections and interactions are handled with [SQLAlchemy](https://www.sqlalchemy.org/).
Web Frame uses MySQL as a default database, however it should not be too hard to replace this with another type of database. The database connection settings must be set in `settings.py` before proceeding with database connectivity.
A default base model has been created as a sort of wrapper around SQLAlchemy.
To make life simpler, the model class gives each child class an auto incrementing primary key called `id`.
Following the advanced `Controller` example, an example `User` model would look something like this:
```
from sqlalchemy import String
from webframe.models import model
class User(model.Model.Base,  model.Model):
	__tablename__ =  'user'
	name = Column(String(255),  nullable=False)
	email = Column(String(255),  nullable=False)
```

This model needs to imported into the system somehow so that SQLAlchemy can pick it up. It is recommended to do this in the `settings.py` file.

Once your models are created, creating the database is quite simple. Simply run `python project.py db:fresh` to create the tables at the database specified in the `settings.py` file.

Creating a record is the same as using an SQLAlchemy model. However saving it is slightly different and uses the `save()` method specified in the base `Model` class:
```
from myapp.models.user import User
user = User(name='John Smith', email='johnsmith@example.com')
user.save()
```
Deleting records is also slightly different: in the example above it would be `user.delete()`.

## Factories
Factories are a way of easily creating records in the database with either random or semi-random data.
Creating a factory is quite simple, especially when reusing functionality from the testing module.
```
from webframe.factories.factory import Factory
from webframe.tests.testutils import tutils
from myapp.models.user import User
@Factory(User)
def data():
	return {
		'name': tutils.str_random(),
		'email': tutils.str_random()  +  '@example.com',
	}
```
Using a factory is even simpler, simply import the factory somewhere in the system (`settings.py` is recommended).
An example of factory usage is:
```
from webframe.factories.factory import factory
from myapp.models.user import User
user = factory(User).save()
```

## Seeders
Seeders are a way of populating the database. They are useful for creating default data that your system needs to function.
Unlike factories, these must be specified in the `seed_list` in the `settings.py` file. This allows you to easily choose which seeders need to be run.
An example of a seeder is:
```
from webframe.seeds import seeder
from myapp.models.user import User
class UserSeeder(seeder.Seeder):
	def run(self):
		User(
			name='admin user',
			email='admin@example.com'
		).save()
```
Once the seeder is created and imported, the database can be seeded with `python project.py db:fresh seed`.
*Warning: running this command will re-create your database! A better solution to seeding will be available soon.*

## Utilities
### Auth
The authorisation functionality of Web Frame requires that a User model be available. This model can be set in the `settings.py` file. 
The authorisation functionality can be accessed at `webframe.utils.auth` provides several utility functions. An instance of the `Auth` functionality can be easily grabbed by running `auth(request)`. 

From here you have access to several methods. These have been bundled together below.
```
from webframe.utils.auth import auth
auth(request).authed()													# == False
auth(request).authorize('incorrect@example.com', 'incorrectpw') 		# == False
auth(request).authed('correct@example.com', 'correctpw') 				# == True
auth(request).authed() 													# == True
autheduser = auth(request).user() # The currently authorised user.
auth(request).deauth()
auth(request).authed()													# == False
```

### Routes
There two functions of note in the routes utility at `webframe.utils.routes`.

 - `url(routename, url_params, get_params, include_host=False)` This generates a URL from a named route.
 - `resource(path)` This generates a resource route based on the public files path in `settings.py`.
### Storage
The storage utility is a nice little utility to interact with the storage folder. It is recommended to use this when accessing data within this folder, however it is not necessary. 
There are many functions within this module and if you plan on using it, it is worth reading the source code as it's not too complicated. The source code can be found at `webframe/utils/storage.py`.
### Views
The views utility at `webframe.utils.views` is used to generate templates. Usually this is handled by the `Controller.template()` method.
It defines two methods of note:
 - `view(template_path, template_arguments={})` this will load the template and render it with the arguments. Returns a string.
 - `direct_view(template_data, template_arguments={})` This will take a string of a template and render it in the same fashion as the `view()` method.

### Errors
Web Frame defines a couple of errors that can be used to handle errors or force redirects from anywhere. The latter of these are useful for middleware. For more information on using errors to redirect, see the "Utilities" section.

 - `HttpError` The standard http error. It is unlikely you will use this directly but it is good to know about it. This takes a status code (302, 404, 500, etc...) and a message to display to the user.
 - `DebugError` A more specialised version of `HttpError` which will display the given message only if the application is in debug mode.
## The Settings File
The settings system of Web Frame is divided into two parts. The `settings.conf` file and the `myapp/settings.py` file. The `settings.conf` file stores data such as database connections, the app name, whether debug mode is on, etc...
The `myapp/settings.py` file loads the data from `settings.conf` and provides them in a form that python can access.
A lot more data is stored in the `myapp/settings.py` file than just configuration data.
 - The `globalTemplateArgs()` method is run on every request and the returned data in the dictionary are passed as arguments to generated templates.
 - The `ERROR_HANDLERS` list is a list of controllers which are run on certain errors. An example of this list would be:
```
from myapp.controllers import errorcontrollers
ERROR_HANDLERS =  {
	404: errorcontrollers.error404,
	401: errorcontrollers.error401,
	500: errorcontrollers.error500,
}
```
- The `app_setup()` function is located in `settings.py` for ease of access. It is used mainly for setting up things which cannot be set up before the rest of the system has finished loading.

## Using a Production Server
Due to the simplicity of the WSGI interface, it is very easy to integrate this framework with a production server. All that is needed is a library such as `mod_wsgi` to point to the `app()` method in `myapp/wsgi.py` to bridge the gap between the production server and the framework. The development server does this automatically already.
## Testing
More testing documentation coming soon. Feel free to look through `webframe.tests` to see how the testing framework works until then.
## More Information
For more information, please don't hesitate to contact me.
