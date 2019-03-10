"""This file is in charge of routing."""
from urllib.parse import urlparse
from parse import parse
from framework.utils.errors import abort

class Router():
    """The router."""

    def __init__(self, routes):
        self.routes = routes

    def get_route(self, request):
        """
        Return the callable for this route.
        Returns Route instance.
        """
        found = None
        for route_params in self.routes:

            if not self.__match(route_params, request):
                continue

            found = Route(route_params, request.path)
            break
        
        if not found:
            abort(404)

        return found

    def __match(self, route_params, request):
        """Check if route params match method, path, etc of request."""
        # Method match?
        try:
            method = route_params['method']
            if method.upper() != request.method.upper():
                return False
        except KeyError:
            # No method so don't filter by it.
            pass

        return self.__is_route_match(route_params['path'], request.path)

    def __is_route_match(self, candidate, requested):
        """Return dictionary of callables."""
        # TODO implement a better algorithm for this (more efficient)
        # split and remove empty.
        requested = [piece for piece in requested.split('/') if piece != '']
        candidate = [piece for piece in candidate.split('/') if piece != '']

        if len(requested) != len(candidate):
            return False

        for req, cand in zip(requested, candidate):
            # If candidate is a param then skip
            if cand[0] == '{' and cand[-1] == '}':
                continue
            # Break if any differences found.
            if req != cand:
                return False

        return True


class Route():
    """Wrapper for a route and its information."""

    def __init__(self, route_params, path):
        self.route_params = route_params

        # extract the route parameters
        parsed_path = parse(route_params['path'], path)
        self.params = {}
        if parsed_path:
            self.params = parsed_path.named

        self.callable = route_params['command']

        self.name = None
        try:
            self.name = route_params['name']
        except KeyError:
            pass

        self.middleware = []
        try:
            self.middleware = route_params['middleware']
        except KeyError:
            pass

        self.method = None
        try:
            self.method = route_params['method']
        except KeyError:
            pass