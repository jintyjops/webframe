"""Base models."""

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from framework.core import app

# This is the Base sqlalchemy functionality
# and should be inherited first.
Base = declarative_base()

class Model():
    """Functionality for models."""

    id = Column(Integer, primary_key=True)

    def stage(self):
        app.db.add(self)

    def save(self):
        """Save the model."""
        self.stage()
        app.db.commit()

    @staticmethod
    def save_all():
        """Commit all staged changes to the database."""
        app.db.commit()


    