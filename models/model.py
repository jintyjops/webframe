"""Base models."""

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from framework.core import app

class Model():
    """Functionality for models."""

    # This is the Base sqlalchemy functionality
    # and should be inherited first.
    Base = declarative_base(name='Base')

    id = Column(Integer, primary_key=True, nullable=False)

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'extend_existing': True,
    }

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
    
    @staticmethod
    def _remake_base():
        """Utility method remaking the base on server restart."""
        Model.Base = declarative_base(name='Base')


    