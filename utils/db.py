"""Handles database sessions."""

from sqlalchemy.orm import sessionmaker

def make_session(engine):
    return sessionmaker(engine)();

def get_connection_string(_type, engine, user, password, ip, port, name):
    """Get the connection string."""
    return '%s+%s://%s:%s@%s:%i/%s?charset=utf8mb4' % (
        _type,
        engine,
        user,
        password,
        ip,
        port,
        name
    )