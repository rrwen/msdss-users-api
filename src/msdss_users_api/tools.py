import pydantic
import sqlalchemy

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase

from .models import Base, UserDB, UserTable, UserManager

def create_user_db_func(engine, async_database, sqlalchemy_base=Base, user_table_model=UserTable, user_db_model=UserDB):

    # (create_user_db_func_table) Create user table in database
    sqlalchemy_base.metadata.create_all(engine)
    table = user_table_model.__table__

    # (create_user_db_func_return) Return the get_user_db function
    def out():
        yield SQLAlchemyUserDatabase(user_db_model, async_database, table)
    return out

def create_user_manager_func(
    get_user_db,
    secret,
    reset_password_token_secret=None,
    verification_token_secret=None,
    base_user_manager_model=UserManager,
    *args, **kwargs):

    # (create_user_manager_func_vars) Set default vars
    reset_password_token_secret = secret if reset_password_token_secret is None else reset_password_token_secret
    verification_token_secret = secret if verification_token_secret is None else verification_token_secret

    # (create_user_manager_func_model) Construct user manager model
    model = pydantic.create_model(
        'UserManager',
        reset_password_token_secret=reset_password_token_secret,
        verification_token_secret=verification_token_secret,
        __base__=base_user_manager_model, *args, **kwargs)

    # (create_user_manager_func_return) Return get_user_manager func
    def out(user_db=Depends(get_user_db)):
        yield model(user_db)
    return out