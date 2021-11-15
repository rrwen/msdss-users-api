import pydantic

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase

from .models import Base, UserDB, UserTable, UserManager

def create_user_db_func(engine, async_database, sqlalchemy_base=Base, user_table_model=UserTable, user_db_model=UserDB):
    """
    Create a function to return the the database adapter dependency.

    See `SQLAlchemy configuration <https://fastapi-users.github.io/fastapi-users/configuration/databases/sqlalchemy/>`_ for FastAPI Users,

    Parameters
    ----------
    engine : :class:`sqlalchemy:sqlalchemy.engine.Engine`
        SQLAlchemy engine object to use for creating tables.
    async_database : :class:`databases:databases.Database`
        The async database object to use for managing users. See `databases <https://pypi.org/project/databases/>`_.
    sqlalchemy_base : :func:`sqlalchemy:sqlalchemy.orm.declarative_base`
        The base class from sqlalchemy. See :func:`sqlalchemy:sqlalchemy.orm.declarative_base`.
    user_table_model : :class:`msdss_users_api.models.UserTable`
        The user table model to use for the database dependency. See :class:`msdss_users_api.models.UserTable`.
    user_db_model : :class:`msdss_users_api.models.UserDB`
        The user database model for the database dependency. See :class:`msdss_users_api.models.UserDB`.

    Return
    ------
    func
        A function yielding a :class:`fastapi_users:fastapi_users.db.SQLAlchemyUserDatabase`.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        import databases

        from msdss_base_database import Database
        from msdss_users_api.tools import create_user_db_func

        # Create a database object
        db = Database()

        # Get the engine object from the database
        engine = db._connection

        # Get the async database
        async_database = databases.Database(str(engine.url))

        # Get the user db func
        get_user_db = create_user_db_func(engine, async_database)
    """

    # (create_user_db_func_table) Create user table in database
    sqlalchemy_base.metadata.create_all(engine)
    table = user_table_model.__table__

    # (create_user_db_func_return) Return the get_user_db function
    async def out():
        yield SQLAlchemyUserDatabase(user_db_model, async_database, table)
    return out

def create_user_manager_func(get_user_db, user_manager_model=UserManager):
    """
    Create a function to return the the user manager class.

    See `UserManager configuration <https://fastapi-users.github.io/fastapi-users/configuration/user-manager/>`_ for FastAPI Users,

    Parameters
    ----------
    get_user_db : func
        Function for the user database dependency. See :func:`msdss_users_api.tools.create_user_db_func`.
    user_manager_model : :class:`msdss_users_api.models.UserManager`
        The user manager model from FastAPI Users. See :class:`msdss_users_api.models.UserManager` and :func:`msdss_users_api.tools.create_user_manager_model`.

    Return
    ------
    func
        A function yielding a configured :class:`msdss_users_api.models.UserManager`.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        import databases

        from msdss_base_database import Database
        from msdss_users_api.tools import *

        # Create a database object
        db = Database()

        # Get the engine object from the database
        engine = db._connection

        # Get the async database
        async_database = databases.Database(str(engine.url))

        # Get the user db func
        get_user_db = create_user_db_func(engine, async_database)

        # Create a user manager model
        UserManager = create_user_manager_model('msdss-secret')

        # Get the user manager func
        get_user_manager = create_user_manager_func(get_user_db, UserManager)
    """
    async def out(user_db=Depends(get_user_db)):
        yield user_manager_model(user_db)
    return out

def create_user_manager_model(
    secret,
    reset_password_token_secret=None,
    verification_token_secret=None,
    base_user_manager_model=UserManager,
    *args, **kwargs):
    """
    Create a function to return the the user manager class.

    See `UserManager configuration <https://fastapi-users.github.io/fastapi-users/configuration/user-manager/>`_ for FastAPI Users,

    Parameters
    ----------
    secret : str
        Secret to use for reset password tokens and verification tokens encryption.
    reset_password_token_secret : str or None
        Secret to use for reset password token encryption. If ``None``, then it will default to param ``secret``.
    verification_token_secret : str or None
        Secret to use for verification tokens encryption. If ``None``, then it will default to param ``secret``.
    base_user_manager_model : :class:`msdss_users_api.models.UserManager`
        The user manager model from FastAPI Users. See :class:`msdss_users_api.models.UserManager`.
    *args, **kwargs
        Additional arguments passed to :func:`pydantic:pydantic.create_model`. See `pydantic dynamic model creation <https://pydantic-docs.helpmanual.io/usage/models/#dynamic-model-creation>`_.

    Return
    ------
    :class:`msdss_users_api.models.UserManager`
       A configured :class:`msdss_users_api.models.UserManager`.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_users_api.tools import create_user_manager_model

        UserManager = create_user_manager_model('msdss-secret')
    """

    # (create_user_manager_model_vars) Set default vars
    reset_password_token_secret = secret if reset_password_token_secret is None else reset_password_token_secret
    verification_token_secret = secret if verification_token_secret is None else verification_token_secret

    # (create_user_manager_model_return) Returns created user manager model
    out = pydantic.create_model(
        'UserManager',
        reset_password_token_secret=reset_password_token_secret,
        verification_token_secret=verification_token_secret,
        __base__=base_user_manager_model, *args, **kwargs)
    return out
