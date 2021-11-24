import contextlib
import databases
import os
from msdss_users_api.defaults import DEFAULT_DATABASE_KWARGS
import pydantic
import warnings

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieAuthentication, JWTAuthentication
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.jwt import generate_jwt
from fastapi_users.manager import UserAlreadyExists, UserNotExists
from msdss_base_database import Database
from msdss_base_dotenv import env_exists, load_env_file

from .managers import *
from .models import *

def create_fastapi_users(
    secret,
    reset_password_token_secret,
    verification_token_secret,
    enable_cookie=True,
    enable_jwt=True,
    driver='postgresql',
    user='msdss',
    password='msdss123',
    host='localhost',
    port='5432',
    database='msdss',
    user_manager_kwargs={},
    cookie=None,
    cookie_kwargs={
        'lifetime_seconds': 3600
    },
    jwt=None,
    jwt_kwargs= {
        'lifetime_seconds': 3600,
        'tokenUrl': 'auth/jwt/login'
    },
    Base=Base,
    User=User,
    UserCreate=UserCreate,
    UserUpdate=UserUpdate,
    UserDB=UserDB,
    UserTable=UserTable,
    get_user_db=None):

    # (setup_fastapi_users_vars) Setup vars
    jwt_kwargs['secret'] = jwt_kwargs.get('secret', secret)
    cookie_kwargs['secret'] = cookie_kwargs.get('secret', secret)
    user_manager_kwargs['reset_password_token_secret'] = reset_password_token_secret
    user_manager_kwargs['verification_token_secret'] = verification_token_secret

    # (setup_fastapi_users_db) Setup database connections
    db = Database(driver=driver, user=user, password=password, host=host, port=port, database=database)
    database_engine = db._connection
    async_database = databases.Database(str(database_engine.url))

    # (setup_fastapi_users_auth) Setup auth for users
    jwt = jwt if jwt else JWTAuthentication(**jwt_kwargs)
    cookie = cookie if cookie else CookieAuthentication(**cookie_kwargs)
    
    # (setup_fastapi_users_auth_combine) Combine cookie and jwt auth if needed
    auth = []
    if enable_cookie:
        auth.append(cookie)
    if enable_jwt:
        auth.append(jwt)
    
    # (setup_fastapi_users_func) Setup required functions
    get_user_db = get_user_db if get_user_db else create_user_db_func(database_engine, async_database, sqlalchemy_base=Base, user_table_model=UserTable, user_db_model=UserDB)
    UserManager = create_user_manager(**user_manager_kwargs)
    get_user_manager = create_user_manager_func(get_user_db, UserManager)

    # (setup_fastapi_users_return) Return users api obj
    out = FastAPIUsers(
        get_user_manager,
        auth,
        User,
        UserCreate,
        UserUpdate,
        UserDB
    )
    return out

def create_user_db_context(
    database=Database(**DEFAULT_DATABASE_KWARGS),
    *args, **kwargs):
    """
    Create a context manager for an auto-configured :func:`msdss_users_api.tools.create_user_db_func` function.

    Parameters
    ----------
    database : :class:`msdss_base_database.msdss_base_database.core.Database`
        Database to use for managing users. The default Database has the following argument settings:

        .. jupyter-execute::
            :hide-code:

            from msdss_users_api import DEFAULT_DATABASE_KWARGS
            from pprint import pprint
            pprint(DEFAULT_DATABASE_KWARGS)

    *args, **kwargs
        Additional arguments passed to :func:`msdss_users_api.tools.create_user_db_func`.

    Return
    ------
    dict
        Returns a dictionary with the following keys:
        
        * ``get_user_db_context`` (:func:`contextlib.asynccontextmanager`): function returned from :func:`contextlib.asynccontextmanager` created from an auto-configured :func:`msdss_users_api.tools.create_user_db_func` function
        * ``get_user_db`` (func): user db function from :func:`msdss_users_api.tools.create_user_db_func`
        * ``async_database`` (:class:`databases:databases.Database`): auto-configured :class:`databases:databases.Database` from env vars
        * ``database_engine`` (:class:`sqlalchemy:sqlalchemy.engine.Engine`): auto-configured :class:`sqlalchemy:sqlalchemy.engine.Engine` from env vars

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    .. jupyter-execute::

        from msdss_users_api.tools import *
        
        results = create_user_db_context()
        get_user_db_context = results['get_user_db_context']
        async_database = results['async_database']
    """
    
    # (create_user_db_func_db) Create databases
    engine = database._connection
    async_database = databases.Database(str(engine.url))
    
    # (get_user_db_context_return) Return user db context
    get_user_db = create_user_db_func(engine=engine, async_database=async_database, *args, **kwargs)
    out = dict(
        get_user_db_context=contextlib.asynccontextmanager(get_user_db),
        get_user_db=get_user_db,
        async_database=async_database,
        database_engine=engine
    )
    return out

def create_user_db_func(
    database=Database(**DEFAULT_DATABASE_KWARGS),
    Base=Base,
    UserTable=UserTable,
    UserDB=UserDB):
    """
    Create a function to return the the database adapter dependency.

    See `SQLAlchemy configuration <https://fastapi-users.github.io/fastapi-users/configuration/databases/sqlalchemy/>`_ for FastAPI Users,

    Parameters
    ----------
    database : :class:`msdss_base_database.msdss_base_database.core.Database`
        Database to use for managing users. The default Database has the following argument settings:

        .. jupyter-execute::
            :hide-code:

            from msdss_users_api import DEFAULT_DATABASE_KWARGS
            from pprint import pprint
            pprint(DEFAULT_DATABASE_KWARGS)
            
    Base : :func:`sqlalchemy:sqlalchemy.orm.declarative_base`
        The base class from sqlalchemy. See :func:`sqlalchemy:sqlalchemy.orm.declarative_base`.
    UserTable : :class:`msdss_users_api.models.UserTable`
        The user table model to use for the database dependency. See :class:`msdss_users_api.models.UserTable`.
    UserDB : :class:`msdss_users_api.models.UserDB`
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

        # Get the user db func
        get_user_db = create_user_db_func(db)
    """

    # (create_user_db_func_db) Get engine and async database
    engine = database._connection
    async_database = databases.Database(str(engine.url))

    # (create_user_db_func_table) Create user table in database
    Base.metadata.create_all(engine)
    table = UserTable.__table__

    # (create_user_db_func_return) Return the get_user_db function
    async def out():
        yield SQLAlchemyUserDatabase(UserDB, async_database, table)
    return out

def create_user_manager_context(
    reset_password_token_secret,
    verification_token_secret,
    get_user_db,
    UserManager=None,
    load_env=True,
    env_file='./.env',
    key_path=None,
    reset_password_token_secret_key='MSDSS_USERS_RESET_PASSWORD_TOKEN_SECRET',
    verification_token_secret_key='MSDSS_USERS_VERIFICATION_TOKEN_SECRET',
    user_manager_kwargs={}):
    """
    Create a context manager for an auto-configured :func:`msdss_users_api.tools.create_user_manager_func` function.

    Parameters
    ----------
    reset_password_token_secret : str
        Secret used to secure password reset tokens. Use a strong phrase (e.g. ``openssl rand -hex 32``).
    verification_token_secret : str or None
        Secret used to secure verification tokens. Use a strong phrase (e.g. ``openssl rand -hex 32``).
    get_user_db : func
        Function for the user database dependency. See :func:`msdss_users_api.tools.create_user_db_func`.
    UserManager : :class:`msdss_users_api.models.UserManager`
        The user manager model from FastAPI Users. See :class:`msdss_users_api.models.UserManager` and :func:`msdss_users_api.tools.create_user_manager`. If ``None``, one will be created.
    load_env : bool
        Whether to load variables from a file with environmental variables at ``env_file`` or not.
    env_file : str
        The path of the file with environmental variables.
    key_path : str
        The path of the key file for the ``env_file``.
    reset_password_token_secret_key : str
        The environmental variable name for ``reset_password_token_secret``.
    verification_token_secret_key : str
        The environmental variable name for ``verification_token_secret``.
    user_manager_kwargs : dict
        Keyword arguments passed to :func:`msdss_users_api.tools.create_user_manager`

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
        
        get_user_manager_context = create_user_manager_context('msdss-reset-secret', 'msdss-verify-secret')
    """
    
    # (get_user_manager_context_env) Load env vars
    has_env = env_exists(file_path=env_file, key_path=key_path)
    if load_env and has_env:
        load_env_file(file_path=env_file, key_path=key_path)
        user_manager_kwargs['reset_password_token_secret'] = os.getenv(reset_password_token_secret_key, reset_password_token_secret_key)
        user_manager_kwargs['verification_token_secret'] = os.getenv(verification_token_secret_key, verification_token_secret)

    # (get_user_manager_context_func) Create user manager func
    UserManager = UserManager if UserManager else create_user_manager(**user_manager_kwargs)
    get_user_manager = create_user_manager_func(get_user_db, UserManager)

    # (get_user_manager_context_return) Return user manager context
    out = contextlib.asynccontextmanager(get_user_manager)
    return out

def create_user_manager_func(get_user_db, UserManager=UserManager):
    """
    Create a function to return the the user manager class.

    See `UserManager configuration <https://fastapi-users.github.io/fastapi-users/configuration/user-manager/>`_ for FastAPI Users,

    Parameters
    ----------
    get_user_db : func
        Function for the user database dependency. See :func:`msdss_users_api.tools.create_user_db_func`.
    UserManager : :class:`msdss_users_api.models.UserManager`
        The user manager model from FastAPI Users. See :class:`msdss_users_api.models.UserManager`.

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

        # Get the user db func
        get_user_db = create_user_db_func(db)

        # Create a user manager model
        UserManager = create_user_manager('msdss-reset-secret', 'msdss-verify-secret')

        # Get the user manager func
        get_user_manager = create_user_manager_func(get_user_db, UserManager)
    """
    async def out(user_db=Depends(get_user_db)):
        yield UserManager(user_db)
    return out

def create_user_manager(
    reset_password_token_secret,
    verification_token_secret,
    __base__=UserManager,
    *args, **kwargs):
    """
    Create a function to return the the user manager class.

    See `UserManager configuration <https://fastapi-users.github.io/fastapi-users/configuration/user-manager/>`_ for FastAPI Users,

    Parameters
    ----------
    reset_password_token_secret : str
        Secret to use for reset password token encryption.
    verification_token_secret : str
        Secret to use for verification tokens encryption.
    __base__: :class:`msdss_users_api.models.UserManager`
        The base user manager model from FastAPI Users. See :class:`msdss_users_api.models.UserManager`.
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

        from msdss_users_api.tools import create_user_manager

        UserManager = create_user_manager('msdss-reset-secret', 'msdss-verify-secret')
    """
    out = pydantic.create_model(
        'UserManager',
        reset_password_token_secret=reset_password_token_secret,
        verification_token_secret=verification_token_secret,
        __base__=__base__,
        *args, **kwargs)
    return out

async def delete_user(email, user_db_context_kwargs={}, user_manager_context_kwargs={}):
    """
    Delete a user.

    Parameters
    ----------
    email : str
        Email for the user.
    user_db_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_db_context`.
    user_manager_context_kwargs : dict
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
    user_db_context = create_user_db_context(**user_db_context_kwargs)
    get_user_db_context = user_db_context['get_user_db_context']
    get_user_db = user_db_context['get_user_db']
    async_database= user_db_context['async_database']
    get_user_manager_context = create_user_manager_context(get_user_db=get_user_db, **user_manager_context_kwargs)

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