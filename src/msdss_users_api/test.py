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

from msdss_base_database import Database
from msdss_base_database.tools import get_database_url

DATABASE_URL = get_database_url()
database = databases.Database(DATABASE_URL)

engine=Database()._connection
Base: DeclarativeMeta = declarative_base()
Base.metadata.create_all(engine)
# class UserTable(Base, fastapi_users.db.SQLAlchemyBaseUserTable):
#     pass

def get_user_db(user_db_model=UserDB, async_database=database):
    table = Database()._get_table('user')
    def out():
        yield SQLAlchemyUserDatabase(user_db_model, async_database, table)
    return out

def get_user_manager(secret, base_model=UserManager):

    model = pydantic.create_model('UserManager', verification_token_secret=secret, __base__=base_model)

    def out(user_db=Depends(get_user_db())):
        yield model(user_db)
    return out

# def get_user_manager(user_db=Depends(get_user_db)):
#     yield UserManager(user_db)

jwt_authentication = get_jwt_auth('secret')

fastapi_users = FastAPIUsers(
    get_user_manager('secret'),
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

@app.on_event('startup')
async def startup_event():
    await database.connect()

@app.on_event('shutdown')
async def shutdown_event():
    await database.disconnect()