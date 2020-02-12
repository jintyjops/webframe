"""Base models."""

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from webframe.core import app
from webframe.utils.errors import abort

class Model():
    """Functionality for models."""

    # Flag which determines if transaction commits will be applied 
    # external to this class.
    # Default is False, which will commit a transaction 
    # on save(), save_all(), or delete()
    commit_external = False

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
        Model.save_all()

        return self

    def delete(self):
        """Delete the model from the database."""
        app.db.delete(self)
        Model.save_all()

    @classmethod
    def query(cls):
        """Create a new session query object for implementing class."""
        return app.db.query(cls)

    @classmethod
    def find(cls, pk):
        """Find by primary key."""
        return cls.query().get(pk)

    @classmethod
    def findOrFail(cls, pk):
        """Find model by primary key or throw 404."""
        if pk is None:
            abort(404, 'Unable to find record.')
        model = cls.find(pk)
        if model is None:
            abort(404, 'Unable to find record.')
        return model

    @staticmethod
    def save_all():
        """Commit all staged changes to the database."""
        if not Model.commit_external:
            app.db.commit()
    
    @staticmethod
    def _remake_base():
        """Utility method remaking the base on server restart."""
        Model.Base = declarative_base(name='Base')


    