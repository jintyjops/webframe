"""The WSGI entry/communication point for the app."""


def app(environ, start_response):
    """The app entry point."""
    response_body = b'yeet'
    status = '200 OK'
    start_response(status, headers=[])
    return iter([response_body])
