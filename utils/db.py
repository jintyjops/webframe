"""Handles database sessions."""

from sqlalchemy.orm import sessionmaker

def make_session(engine):
    return sessionmaker(engine)();