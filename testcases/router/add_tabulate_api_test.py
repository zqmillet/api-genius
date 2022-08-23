from pytest import mark
from requests import get
from requests import post
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer

from api_genius import Application

Base = declarative_base()

class User(Base): # type: ignore
    """
    this class is used for testing.
    """
    __tablename__ = 'users'

    id = Column(String(50), primary_key=True)
    name = Column(String(50))
    age = Column(Integer())

@mark.create_tables(models=[User])
def test_gen_api(database_engine):
    application = Application()
    application.add_create_api(database_engine=database_engine, path='/user/{id}')(User)
    test_client = TestClient(app=application)

    print(test_client.post('/user/id1'))
