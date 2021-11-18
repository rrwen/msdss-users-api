import contextlib
import databases
import os
import pydantic
import warnings

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.jwt import generate_jwt
from fastapi_users.manager import UserAlreadyExists, UserNotExists
from msdss_base_database import Database
from msdss_base_dotenv import env_exists, load_env_file

from .models import *

def create_user_db_context(
    engine=None,
    async_database=None,
    load_env=True,
    env_file='./.env',
    key_path=None,
    driver_key='MSDSS_DATABASE_DRIVER',
    user_key='MSDSS_DATABASE_USER',
    password_key='MSDSS_DATABASE_PASSWORD',
    host_key='MSDSS_DATABASE_HOST',
    port_key='MSDSS_DATABASE_PORT',
    database_key='MSDSS_DATABASE_NAME',
    engine_kwargs={},
    async_database_kwargs={},
    *args, **kwargs):
    """
    Create a context manager for an auto-configured :func:`msdss_users_api.tools.create_user_db_func` function.

    Parameters
    ----------
    engine : :class:`sqlalchemy:sqlalchemy.engine.Engine` or None
        SQLAlchemy engine object to use for creating tables. If ``None``, one will be auto-configured from the ``env_file``.
    async_database : :class:`databases:databases.Database`
        The async database object to use for managing users. See `databases <https://pypi.org/project/databases/>`_. If ``None``, one will be auto-configured from the ``env_file``.
    load_env : bool
        Whether to load variables from a file with environmental variables at ``env_file`` or not.
    env_file : str
        The path of the file with environmental variables.
    key_path : str
        The path of the key file for the ``env_file``.
    driver_key : str
        The environmental variable name for ``driver``.
    user_key : str
        The environmental variable name for ``user``.
    password_key : str
        The environmental variable name for ``password``.
    host_key : str
        The environmental variable name for ``key``.
    port_key : str
        The environmental variable name for ``port``.
    database_key : str
        The environmental variable name for ``database``.
    engine_kwargs : dict
        Keyword arguments passed to :class:`msdss_base_database:msdss_base_database.core.Database` if ``engine`` is ``None``.
    async_database_kwargs : dict
        Keyword arguments passed to :class:`databases:databases.Database` if ``async_database`` is ``None``.

    Return
    ------
    (:func:`contextlib.asynccontextmanager`, func, :class:`databases:databases.Database`, :class:`sqlalchemy:sqlalchemy.engine.Engine`)
        Returns a tuple of (in order):
        
        * Function returned from :func:`contextlib.asynccontextmanager` created from an auto-configured :func:`msdss_users_api.tools.create_user_db_func` function
        * Function for the user database dependency from ``get_user_db`` or auto-configured :func:`msdss_users_api.tools.create_user_db_func`.
        * Async database from parameter ``async_database`` or auto-configured :class:`databases:databases.Database` from env vars
        * Engine from parameter ``engine`` or auto-configured :class:`sqlalchemy:sqlalchemy.engine.Engine` from env vars

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    .. jupyter-execute::

        from msdss_users_api.tools import *
        
        get_user_db_context, get_user_db, async_database, engine = create_user_db_context()
    """

    # (get_user_db_context_env) Load env vars
    has_env = env_exists(file_path=env_file, key_path=key_path)
    if load_env and has_env:
        engine_kwargs['driver'] = os.getenv(driver_key, 'postgresql')
        engine_kwargs['user'] = os.getenv(user_key, 'msdss')
        engine_kwargs['password'] = os.getenv(password_key, 'msdss123')
        engine_kwargs['host'] = os.getenv(host_key, 'localhost')
        engine_kwargs['port'] = os.getenv(port_key, '5432')
        engine_kwargs['database'] = os.getenv(database_key, 'msdss')
    
    # (create_user_db_func_db) Create databases
    engine = engine if engine else Database(**engine_kwargs)._connection
    async_database = async_database if async_database else databases.Database(str(engine.url), **async_database_kwargs)
    
    # (get_user_db_context_return) Return user db context
    get_user_db = create_user_db_func(engine=engine, async_database=async_database, *args, **kwargs)
    out = (contextlib.asynccontextmanager(get_user_db), get_user_db, async_database, engine)
    return out

def create_user_db_func(
    engine,
    async_database,
    sqlalchemy_base=Base,
    user_table_model=UserTable,
    user_db_model=UserDB):
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

def create_user_manager_context(
    secret='msdss-secret',
    get_user_db=None,
    reset_password_token_secret=None,
    verification_token_secret=None,
    user_manager_model=None,
    load_env=True,
    env_file='./.env',
    key_path=None,
    secret_key='MSDSS_USERS_SECRET',
    reset_password_token_secret_key='MSDSS_USERS_RESET_PASSWORD_TOKEN_SECRET',
    verification_token_secret_key='MSDSS_USERS_VERIFICATION_TOKEN_SECRET',
    show_warnings=True,
    create_user_manager_model_kwargs={}):
    """
    Create a context manager for an auto-configured :func:`msdss_users_api.tools.create_user_manager_func` function.

    Parameters
    ----------
    secret : str
        A secret for security encryption and protecting user data. Use a strong phrase (e.g. ``openssl rand -hex 32``).
    get_user_db : func
        Function for the user database dependency. See :func:`msdss_users_api.tools.create_user_db_func`.
    verification_token_secret : str or None
        Secret used to secure verification tokens. If ``None``, it will default to param ``secret``.
    cookie_secret : str or None
        Secret used to secure cookies. If ``None``, it will default to param ``secret``.
    user_manager_model : :class:`msdss_users_api.models.UserManager`
        The user manager model from FastAPI Users. See :class:`msdss_users_api.models.UserManager` and :func:`msdss_users_api.tools.create_user_manager_model`.
    load_env : bool
        Whether to load variables from a file with environmental variables at ``env_file`` or not.
    env_file : str
        The path of the file with environmental variables.
    key_path : str
        The path of the key file for the ``env_file``.
    secret_key : str
        The environmental variable name for ``secret``.
    reset_password_token_secret_key : str
        The environmental variable name for ``reset_password_token_secret``.
    verification_token_secret_key : str
        The environmental variable name for ``verification_token_secret``.
    show_warnings : bool
        Whether to display warnings or not.
    create_user_manager_model_kwargs : dict
        Keyword arguments passed to :func:`msdss_users_api.tools.create_user_manager_model`

    Return
    ------
    :func:`contextlib.asynccontextmanager`
        Function returned from :func:`contextlib.asynccontextmanager` created from an auto-configured :func:`msdss_users_api.tools.create_user_manager_func` function.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    .. jupyter-execute::

        from msdss_users_api.tools import *
        
        get_user_manager_context = create_user_manager_context('msdss-secret')
    """

    # (get_user_manager_warn) Warn if default secret is used
    if secret == 'msdss-secret':
        warnings.warn('Default secret was used - please change secret phrase!')
    
    # (get_user_manager_context_env) Load env vars
    has_env = env_exists(file_path=env_file, key_path=key_path)
    if load_env and has_env:
        load_env_file(file_path=env_file, key_path=key_path)
        secret = os.getenv(secret_key, secret)
        reset_password_token_secret = os.getenv(reset_password_token_secret_key, reset_password_token_secret_key)
        verification_token_secret = os.getenv(verification_token_secret_key, verification_token_secret)
    
    # (get_user_manager_vars) Set default vars
    reset_password_token_secret = reset_password_token_secret if reset_password_token_secret else secret
    verification_token_secret = verification_token_secret if verification_token_secret else secret

    # (get_user_manager_context_func) Create user manager func
    user_manager_model = user_manager_model if user_manager_model else create_user_manager_model(
        secret,
        reset_password_token_secret=reset_password_token_secret,
        verification_token_secret=verification_token_secret,
        **create_user_manager_model_kwargs)
    get_user_manager = create_user_manager_func(get_user_db, user_manager_model)

    # (get_user_manager_context_return) Return user manager context
    out = contextlib.asynccontextmanager(get_user_manager)
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

async def delete_user(email, create_user_db_context_kwargs={}, create_user_manager_context_kwargs={}):
    """
    Delete a user.

    Parameters
    ----------
    email : str
        Email for the user.
    create_user_db_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_db_context`.
    create_user_manager_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_manager_context`.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    .. jupyter-execute::

        from msdss_users_api.tools import *

        await register_user('test@example.com', 'msdss123')
        await delete_user('test@example.com')
    """

    # (delete_user_context) Get db and manager context functions
    get_user_db_context, get_user_db, async_database, engine = create_user_db_context(**create_user_db_context_kwargs)
    get_user_manager_context = create_user_manager_context(get_user_db=get_user_db, **create_user_manager_context_kwargs)

    # (delete_user_run) Run delete user function
    try:
        async with get_user_db_context() as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                await async_database.connect()
                user = await user_manager.get_by_email(email)
                await user_manager.delete(user)
                print(f'User deleted {email}')
    except UserNotExists:
        print(f'User {email} does not exist')
    finally:
        await async_database.disconnect()

async def get_user(email, show=False, include_hashed_password=False, create_user_db_context_kwargs={}, create_user_manager_context_kwargs={}):
    """
    Get attributes for a user.

    Parameters
    ----------
    email : str
        Email for the user.
    show : bool
        Whether to print user attributes or not.
    include_hashed_password : bool
        Whether to include the ``hashed_password`` attribute.
    create_user_db_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_db_context`.
    create_user_manager_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_manager_context`.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Return
    ------
    :class:`msdss_users.models.User`
        A user model with attributes for the specified user with ``email``.

    Example
    -------

    .. jupyter-execute::

        from msdss_users_api.tools import register_user, get_user

        await register_user('test@example.com', 'msdss123')
        user = await get_user('test@example.com', show=True)

    """

    # (get_user_context) Get db and manager context functions
    get_user_db_context, get_user_db, async_database, engine = create_user_db_context(**create_user_db_context_kwargs)
    get_user_manager_context = create_user_manager_context(get_user_db=get_user_db, **create_user_manager_context_kwargs)

    # (get_user_run) Run get user function
    try:
        async with get_user_db_context() as user_db:
            async with get_user_manager_context(user_db) as user_manager:

                # (get_user_run_get) Connect and get the user from db
                await async_database.connect()
                out = await user_manager.get_by_email(email)

                # (get_user_run_hash) Remove hashed password if needed
                if not include_hashed_password:
                    del out.hashed_password
                
                # (get_user_run_show) Print user attributes
                if show:
                    for k, v in out.dict().items():
                        print(f'{k}: {v}')
                return out
    except UserNotExists:
        print(f'User {email} does not exist')
    finally:
        await async_database.disconnect()

async def register_user(
    email,
    password,
    superuser=False,
    create_user_db_context_kwargs={},
    create_user_manager_context_kwargs={},
    *args, **kwargs):
    """
    Register a user.

    Parameters
    ----------
    email : str
        Email for the user.
    password : str
        Password for the user.
    superuser : bool
        Whether the user is a superuser or not.
    create_user_db_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_db_context`.
    create_user_manager_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_manager_context`.
    *args, **kwargs
        Additional arguments passed to :class:`msdss_users_api.models.UserCreate`.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    .. jupyter-execute::

        from msdss_users_api.tools import *
        
        await register_user('test@example.com', 'msdss123')
    """
    
    # (register_user_context) Get db and manager context functions
    get_user_db_context, get_user_db, async_database, engine = create_user_db_context(**create_user_db_context_kwargs)
    get_user_manager_context = create_user_manager_context(get_user_db=get_user_db, **create_user_manager_context_kwargs)

    # (register_user_run) Run create user function
    try:
        async with get_user_db_context() as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                await async_database.connect()
                await user_manager.create(
                    UserCreate(
                        email=email,
                        password=password,
                        is_superuser=superuser,
                        *args, **kwargs))
                print(f'User created {email}')
    except UserAlreadyExists:
        print(f'User {email} already exists')
    finally:
        await async_database.disconnect()

async def reset_user_password(email, password, create_user_db_context_kwargs={}, create_user_manager_context_kwargs={}):
    """
    Reset password for a user.

    Parameters
    ----------
    email : str
        Email for the user.
    password : str
        New password for the user.
    create_user_db_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_db_context`.
    create_user_manager_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_manager_context`.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    .. jupyter-execute::

        from msdss_users_api.tools import *

        await register_user('test@example.com', 'msdss123')
        await reset_user_password('test@example.com', 'msdss321')
    """

    # (reset_user_password_context) Get db and manager context functions
    get_user_db_context, get_user_db, async_database, engine = create_user_db_context(**create_user_db_context_kwargs)
    get_user_manager_context = create_user_manager_context(get_user_db=get_user_db, **create_user_manager_context_kwargs)

    # (reset_user_password_run) Run password reset user function
    try:
        async with get_user_db_context() as user_db:
            async with get_user_manager_context(user_db) as user_manager:

                # (reset_user_password_run_user) Get user by email
                await async_database.connect()
                user = await user_manager.get_by_email(email)

                # (reset_user_password_run_token) Get forgot password token
                token_data = {
                    "user_id": str(user.id),
                    "aud": user_manager.reset_password_token_audience,
                }
                token = generate_jwt(
                    token_data,
                    user_manager.reset_password_token_secret,
                    user_manager.reset_password_token_lifetime_seconds,
                )

                # (reset_user_password_run_reset) Reset password with token
                await user_manager.reset_password(token, password)
                print(f'User password reset {email}')
    except UserNotExists:
        print(f'User {email} does not exist')
    finally:
        await async_database.disconnect()

async def update_user(
    email,
    create_user_db_context_kwargs={},
    create_user_manager_context_kwargs={},
    *args, **kwargs):
    """
    Update a user.

    Parameters
    ----------
    email : str
        Email for the user.
    create_user_db_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_db_context`.
    create_user_manager_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_manager_context`.
    *args, **kwargs
        Additional arguments passed to :class:`msdss_users_api.models.UserUpdate`.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    .. jupyter-execute::

        from msdss_users_api.tools import *
        
        # Create a test user
        await register_user('test@example.com', 'msdss123')
        print('\\nbefore_update:\\n')
        user = await get_user('test@example.com', show=True)
        
        # Update the test user
        await update_user('test@example.com', is_verified=True)
        print('\\nafter_update:\\n')
        user = await get_user('test@example.com', show=True)
    """
    
    # (register_user_context) Get db and manager context functions
    get_user_db_context, get_user_db, async_database, engine = create_user_db_context(**create_user_db_context_kwargs)
    get_user_manager_context = create_user_manager_context(get_user_db=get_user_db, **create_user_manager_context_kwargs)

    # (register_user_run) Run create user function
    try:
        async with get_user_db_context() as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                await async_database.connect()
                user = await user_manager.get_by_email(email)
                await user_manager.update(
                    UserUpdate(
                        email=email,
                        *args, **kwargs),
                    user
                )
                print(f'User updated {email}')
    except UserNotExists:
        print(f'User {email} does not exist')
    finally:
        await async_database.disconnect()