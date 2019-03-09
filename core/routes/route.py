"""This file is in charge of routing."""
from urllib.parse import urlparse
from parse import parse
from framework.utils.errors import abort

class Router():
    """The router."""

    def __init__(self, routes):
        self.routes = routes

    def get_route(self, path):
        """
        Return the callable for this route.
        Returns Route instance.
        """
        found = None
        for route_params in self.routes:
            candidate = route_params['path']

            if not self.__is_found(candidate, path):
                continue

            found = Route(route_params, path)
            break
        
        if not found:
            abort(404)

        return found

    def __is_found(self, candidate, requested):
        """Return dictionary of callables."""
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

        # the route paramaters
        self.parsed_path = parse(route_params['path'], path)
        self.callable = route_params['command']
        self.name = None
        try:
            self.name = route_params['name']
        except KeyError:
            pass

    def params(self):
        """Get the route parameters."""
        if self.parsed_path:
            return self.parsed_path.named
        return {}