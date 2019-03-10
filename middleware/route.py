"""Do stuff with the route."""

def store_last_route(request, response):
    """Store the last route used for things like redirect_back()."""
    try:
        last_route = request.session.get('this_route')
    except KeyError:
        last_route = ''
    request.session.store('last_route', last_route)
    request.session.store('this_route', request.path)