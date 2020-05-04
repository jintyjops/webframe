"""Base models."""

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy import Column, Integer, String
from webframe.core.app import App
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
        App().db().add(self)

    def save(self):
        """Save the model."""
        self.stage()
        Model.save_all()

        return self

    def delete(self):
        """Delete the model from the database."""
        App().db().delete(self)
        Model.save_all()

    def fresh(self):
        """Get a fresh object from the db."""
        return App().db().expire(self)

    @classmethod
    def create(cls):
        """Create the table in the database. Does nothing if table exists."""
        engine = App().settings().ENGINE
        if not engine.dialect.has_table(engine, cls.__tablename__):
            cls.__table__.create(App().settings().ENGINE)

    @classmethod
    def drop(cls):
        """Drop the table from the database. Nothing if table does not exist."""
        engine = App().settings().ENGINE
        if engine.dialect.has_table(engine, cls.__tablename__):
            cls.__table__.drop(App().settings().ENGINE)

    @classmethod
    def query(cls):
        """Create a new session query object for implementing class."""
        return App().db().query(cls)

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
        if Model.commit_external:
            App().db().flush()
        else:
            App().db().commit()
    
    @staticmethod
    def _remake_base():
        """Utility method remaking the base on server restart."""
        Model.Base = declarative_base(name='Base')
    
    @staticmethod
    def raw_command(command, **kwargs):
        """Apply a raw command to the database."""
        connection = App().settings().ENGINE.connect()
        connection.execute(command, **kwargs)
        connection.commit()

    @staticmethod
    def drop_table(tablename):
        """Drop a given table."""
        Model.raw_command(
            text('DROP TABLE IF EXISTS :tablename'),
            tablename=tablename
        )
    


    