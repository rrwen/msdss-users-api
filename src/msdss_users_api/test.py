from typing import Optional

from fastapi import Depends, Request, FastAPI
from fastapi_users import BaseUserManager, FastAPIUsers

import pydantic
import databases
import sqlalchemy
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from .auth import *
from .models import *

from msdss_base_database.tools import get_database_url

SECRET = "SECRET"

DATABASE_URL = get_database_url('postgresql', user='msdss', password='msdss123', database='msdss')
database = databases.Database(DATABASE_URL)
Base: DeclarativeMeta = declarative_base()


class UserTable(Base, SQLAlchemyBaseUserTable):
    pass

engine = sqlalchemy.create_engine(
    DATABASE_URL
)
Base.metadata.create_all(engine)

users = UserTable.__table__


def get_user_db():
    yield SQLAlchemyUserDatabase(UserDB, database, users)

# def get_func(secret):

#     m = pydantic.create_model('UserManager', verification_token_secret=secret, __base__=UserManager)

#     def get_user_manager(user_db=Depends(get_user_db)):
#         yield m(user_db)
#     return get_user_manager

def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

jwt_authentication = get_jwt_auth('secret')

fastapi_users = FastAPIUsers(
    get_user_manager,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

app = FastAPI()
app.include_router(
    fastapi_users.get_register_router(),
    prefix="/auth",
    tags=["auth"],
)