from enum import Enum as Enum

from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Enum as Enumeration
from sqlalchemy import DateTime

from api_genius import Base
from api_genius import Column
from api_genius import Application

application = Application()

class Role(str, Enum):
    admin = 'admin'
    user = 'user'

@application.add_create_api(database_engine=None)
@application.add_create_api(path='/users/{id}', database_engine=None)
class User(Base):
    __tablename__ = 'users'

    company_id = Column(String(50), primary_key=True, comment='the unique id of company', example='huawei')
    department_id = Column(String(50), primary_key=True, comment='the unique id of department', example='paas')
    id = Column(String(50), primary_key=True, comment='the unique id of user', example='j19260817')
    name = Column(String(50), comment='the name of user', example='zhangbaohua')
    age = Column(Integer(), comment='the age of user', example=99, ge=18, le=100)
    role = Column(Enumeration(Role), comment='the role of user', example='user')
    create_time = Column(DateTime(), comment='the create time of this record', private=True)
