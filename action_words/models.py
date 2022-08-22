from sqlalchemy.orm import declarative_base
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer

Base = declarative_base()

class User(Base): # type: ignore
    """
    this class is used for testing.
    """
    __tablename__ = 'users'

    id = Column(String(50), primary_key=True)
    name = Column(String(50))
    age = Column(Integer())
