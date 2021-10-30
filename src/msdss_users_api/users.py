import databases
import pydantic
import sqlalchemy

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from msdss_base_database.tools import get_database_url
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from .models import UserDB, UserManager

def get_user_db(table='msdss_users', UserDB=UserDB, load_env=True, *args, **kwargs):

    database = databases.Database(get_database_url(load_env=load_env, *args, **kwargs))
    engine = sqlalchemy.create_engine(get_database_url(load_env=load_env, *args, **kwargs), connect_args={"check_same_thread": False})

    Base: DeclarativeMeta = declarative_base()
    Base.metadata.create_all(engine)

    yield SQLAlchemyUserDatabase(UserDB, database, table)

def create_user_manager_func(
    reset_password_token_secret,
    verification_token_secret,
    name='UserManager',
    UserDB=UserDB,
    *args, **kwargs):

    CustomUserManager = pydantic.create_model(
        name,
        __base__=UserManager,
        user_db_model=UserDB,
        reset_password_token_secret=reset_password_token_secret,
        verification_token_secret=verification_token_secret,
        *args, **kwargs
    )

    def out(user_db=Depends(get_user_db)):
        yield CustomUserManager(user_db)
    return out