from api_genius import Application
from api_genius import Base
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import Enum

application = Application()

class User(Base):
    __tablename__ = 'users'

    id = Column(String(50), primary_key=True, comment='the unique id of user')
    name = Column(String(50))
    age = Column(Integer())
    role = Column(Enum('admin', 'user'))

    create_time = Column(DateTime())
    update_time = Column(DateTime())

application.add_create_api(path='/users/{id}', database_engine=None)(User)
