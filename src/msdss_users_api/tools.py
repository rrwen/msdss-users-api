from msdss_users_api.defaults import DEFAULT_COOKIE_SETTINGS, DEFAULT_JWT_SETTINGS
import pydantic
import contextlib
import databases

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieAuthentication, JWTAuthentication
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.jwt import generate_jwt
from fastapi_users.manager import UserAlreadyExists, UserNotExists
from msdss_base_database import Database

from .defaults import *
from .env import *
from .managers import *
from .models import *

def create_fastapi_users_objects(
    user_manager_settings={},
    jwt_settings=DEFAULT_JWT_SETTINGS,
    cookie_settings=DEFAULT_COOKIE_SETTINGS,
    database=Database(),
    enable_cookie=True,
    enable_jwt=True,
    cookie=None,
    jwt=None,
    Base=Base,
    User=User,
    UserCreate=UserCreate,
    UserUpdate=UserUpdate,
    UserDB=UserDB,
    UserTable=UserTable,
    UserManager=None):
    """
    Creates all the needed dependencies and models to build a `FastAPIUsers object <https://fastapi-users.github.io/fastapi-users/configuration/routers/>`_.

    Parameters
    ----------
    user_manager_settings : dict
        Keyword arguments to be passed to :func:`msdss_users_api.tools.create_user_manager`.
        
        Requires setting at least the following keys:

        * ``reset_password_token_secret`` (str): secret used to secure password reset tokens. Use a strong phrase (e.g. ``openssl rand -hex 32``)
        * ``verification_token_secret`` (str): secret used to secure verification tokens. Use a strong phrase (e.g. ``openssl rand -hex 32``)

    cookie_settings : dict
        Dictionary of keyword arguments passed to :class:`fastapi_users:fastapi_users.authentication.CookieAuthentication`.
        See `CookieAuthentication <https://fastapi-users.github.io/fastapi-users/configuration/authentication/cookie/>`_.
        
        Requires setting at least the following keys if ``enable_cookie`` is ``True``:

        * ``secret`` (str): secret for JWT encryption. Use a strong phrase (e.g. ``openssl rand -hex 32``)

        Other defaults will also be set if not specified:

        .. jupyter-execute::
            :hide-code:
            
            from msdss_users_api.defaults import DEFAULT_COOKIE_SETTINGS

            for k, v in DEFAULT_COOKIE_SETTINGS.items():
                print(f'{k} = {v}')

    jwt_settings : dict
        Dictionary of keyword arguments passed to :class:`fastapi_users:fastapi_users.authentication.JWTAuthentication`. 
        See `JWTAuthentication <https://fastapi-users.github.io/fastapi-users/configuration/authentication/jwt/>`_.

        Requires setting at least the following keys if ``enable_jwt`` is ``True``:

        * ``secret`` (str): secret for cookie encryption. Use a strong phrase (e.g. ``openssl rand -hex 32``)

        Other defaults will also be set if not specified:

        .. jupyter-execute::
            :hide-code:

            from msdss_users_api.defaults import DEFAULT_JWT_SETTINGS

            for k, v in DEFAULT_JWT_SETTINGS.items():
                print(f'{k} = {v}')

    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database to use for managing users.
    enable_cookie : bool
        Whether to enable cookie based authentication or not.
    enable_jwt : bool
        Whether to enable JSON Web Token (JWT) based authentication or not.
    cookie : :class:`fastapi_users:fastapi_users.authentication.CookieAuthentication` or None
        A cookie authentication object from FastAPI Users. If ``None``, one will be created from parameter ``cookie_settings``.
        See `CookieAuthentication <https://fastapi-users.github.io/fastapi-users/configuration/authentication/cookie/>`_.
    jwt : :class:`fastapi_users:fastapi_users.authentication.JWTAuthentication` or None
        A JSON Web Token (JWT) authentication object from FastAPI Users. If ``None``, one will be created from parameter ``jwt_settings``.
        See `JWTAuthentication <https://fastapi-users.github.io/fastapi-users/configuration/authentication/jwt/>`_.
    Base : class
        Class returned from :func:`sqlalchemy:sqlalchemy.orm.declarative_base`.
    User : :class:`msdss_users_api.models.User`
        User model for FastAPI Users. See :class:`msdss_users_api.models.User`.
    UserCreate : :class:`msdss_users_api.models.UserCreate`
        UserCreate model for FastAPI Users. See :class:`msdss_users_api.models.UserCreate`.
    UserUpdate : :class:`msdss_users_api.models.UserUpdate`
        UserUpdate model for FastAPI Users. See :class:`msdss_users_api.models.UserUpdate`.
    UserDB : :class:`msdss_users_api.models.UserDB`
        UserDB model for FastAPI Users. See :class:`msdss_users_api.models.UserDB`.
    UserTable : :class:`msdss_users_api.models.UserTable`
        UserTable model for FastAPI Users. See :class:`msdss_users_api.models.UserTable`.
    UserManager : :class:`msdss_users_api.managers.UserManager` or None
        UserManager model for FastAPI Users. See :class:`msdss_users_api.managers.UserManager`.
        If ``None``, one will be created using :func:`msdss_users_api.tools.create_user_manager`

    Returns
    -------
    dict
        A dictionary containing the following:

        * ``FastAPIUsers`` (:class:`fastapi_users:fastapi_users.FastAPIUsers`): configured FastAPI Users object
        * ``databases`` (dict): dictionary of database related objects
            * ``database`` (:class:`msdss_base_database:msdss_base_database.core.Database`): database object from parameter ``database``
            * ``database_engine`` (:func:`sqlalchemy:sqlalchemy.create_engine`): SQLAlchemy engine object
            * ``async_database`` (:class:`databases:databases.Database`): Async database object
        * ``dependencies`` (dict(func)): dictionary of dependencies
            * ``get_user_db`` (func): get_user_db function auto-configured - see :func:`msdss_users_api.tools.create_user_db_func`.
            * ``get_user_manager`` (func): get_user_manager function auto-configured - see :func`msdss_users_api.tools.create_user_manager_func`.
        * ``models`` (dict): dictionary of models
            * ``User`` (:class:`msdss_users_api.models.User`): see parameter ``User``
            * ``UserCreate`` (:class:`msdss_users_api.models.UserCreate`): see parameter ``UserCreate``
            * ``UserUpdate`` (:class:`msdss_users_api.models.UserUpdate`): see parameter ``UserUpdate``
            * ``UserDB`` (:class:`msdss_users_api.models.UserDB`): see parameter ``UserDB``
            * ``UserTable`` (:class:`msdss_users_api.models.UserTable`): see parameter ``UserTable``
            * ``UserManager`` (:class:`msdss_users_api.managers.UserManager`): see parameter ``UserManager``
        * ``auth`` (dict): dictionary of auth related objects
            * ``jwt`` (:class:`fastapi_users:fastapi_users.authentication.JWTAuthentication`): see parameter ``jwt``
            * ``cookie`` (:class:`fastapi_users:fastapi_users.authentication.CookieAuthentication`): see parameter ``cookie``

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_users_api.tools import *

        # Setup user manager secrets
        user_manager_settings = dict(
            reset_password_token_secret='reset-secret', # CHANGE TO STRONG PHRASE
            verification_token_secret='verify-secret' # CHANGE TO STRONG PHRASE
        )

        # Setup jwt and cookie secret
        jwt_settings = dict(secret='jwt-secret') # CHANGE TO STRONG PHRASE
        cookie_settings = dict(secret='cookie-secret') # CHANGE TO STRONG PHRASE

        # Create FastAPI Users object
        fastapi_users_objects = create_fastapi_users_objects(
            user_manager_settings=user_manager_settings,
            jwt_settings=jwt_settings,
            cookie_settings=cookie_settings
        )

        # Get FastAPI Users Object
        fastapi_users = fastapi_users_objects['FastAPIUsers']
    """

    # (setup_fastapi_users_vars) Setup vars
    for param, default in DEFAULT_COOKIE_SETTINGS.items():
        cookie_settings[param] = cookie_settings.get(param, default)
    for param, default in DEFAULT_JWT_SETTINGS.items():
        jwt_settings[param] = jwt_settings.get(param, default)

    # (setup_fastapi_users_db) Setup database connections
    database_engine = database._connection
    async_database = databases.Database(str(database_engine.url))
    
    # (setup_fastapi_users_auth_combine) Combine cookie and jwt auth if needed
    auth = []
    if enable_cookie:
        cookie = cookie if cookie else CookieAuthentication(**cookie_settings)
        auth.append(cookie)
    if enable_jwt:
        jwt = jwt if jwt else JWTAuthentication(**jwt_settings)
        auth.append(jwt)
    
    # (setup_fastapi_users_func) Setup required functions
    get_user_db = create_user_db_func(database_engine, async_database, Base=Base, UserTable=UserTable, UserDB=UserDB)
    UserManager = UserManager if UserManager else create_user_manager(**user_manager_settings)
    get_user_manager = create_user_manager_func(get_user_db, UserManager)

    # (setup_fastapi_user_create) Create users api func
    fastapi_users = FastAPIUsers(
        get_user_manager,
        auth,
        User,
        UserCreate,
        UserUpdate,
        UserDB
    )

    # (setup_fastapi_users_return) Return users api and constructed objects
    out = dict(
        FastAPIUsers=fastapi_users,
        databases=dict(
            database=database,
            database_engine=database_engine,
            async_database=async_database
        ),
        dependencies=dict(
            get_user_db=get_user_db,
            get_user_manager=get_user_manager
        ),
        models=dict(
            User=User,
            UserCreate=UserCreate,
            UserUpdate=UserUpdate,
            UserDB=UserDB,
            UserTable=UserTable,
            UserManager=UserManager
        ),
        auth=dict(
            jwt=jwt,
            cookie=cookie
        )
    )
    return out

def create_user_db_context(
    database=Database(),
    *args, **kwargs):
    """
    Create a context manager for an auto-configured :func:`msdss_users_api.tools.create_user_db_func` function.

    Parameters
    ----------
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database to use for managing users.
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
    database_engine = database._connection
    async_database = databases.Database(str(database_engine.url))
    
    # (get_user_db_context_return) Return user db context
    get_user_db = create_user_db_func(database_engine=database_engine, async_database=async_database, *args, **kwargs)
    out = dict(
        get_user_db_context=contextlib.asynccontextmanager(get_user_db),
        get_user_db=get_user_db,
        async_database=async_database,
        database_engine=database_engine
    )
    return out

def create_user_db_func(
    database_engine,
    async_database=None,
    Base=Base,
    UserTable=UserTable,
    UserDB=UserDB):
    """
    Create a function to return the the database adapter dependency.

    See `SQLAlchemy configuration <https://fastapi-users.github.io/fastapi-users/configuration/databases/sqlalchemy/>`_ for FastAPI Users,

    Parameters
    ----------
    database_engine : :func:`sqlalchemy:sqlalchemy.create_engine`
        SQLAlchemy engine object.
    async_database : :class:`databases:databases.Database` or None
        Async database object from ``databases``. If ``None``, one will be created from parameter ``database_engine``.
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
        db = Database()._connection

        # Get the user db func
        get_user_db = create_user_db_func(db)
    """

    # (create_user_db_func_db) Get engine and async database
    async_database = async_database if async_database else databases.Database(str(database_engine.url))

    # (create_user_db_func_table) Create user table in database
    Base.metadata.create_all(database_engine)
    table = UserTable.__table__

    # (create_user_db_func_return) Return the get_user_db function
    async def out():
        yield SQLAlchemyUserDatabase(UserDB, async_database, table)
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
    __base__: :class:`msdss_users_api.managers.UserManager`
        The base user manager model from FastAPI Users. See :class:`msdss_users_api.managers.UserManager`.
    *args, **kwargs
        Additional arguments passed to :func:`pydantic:pydantic.create_model`. See `pydantic dynamic model creation <https://pydantic-docs.helpmanual.io/usage/models/#dynamic-model-creation>`_.

    Return
    ------
    :class:`msdss_users_api.managers.UserManager`
       A configured :class:`msdss_users_api.managers.UserManager`.

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

def create_user_manager_context(
    get_user_db,
    user_manager_settings={},
    UserManager=None,
    load_env=True,
    env=UsersDotEnv()):
    """
    Create a context manager for an auto-configured :func:`msdss_users_api.tools.create_user_manager_func` function.

    Parameters
    ----------
    get_user_db : func
        Function for the user database dependency. See :func:`msdss_users_api.tools.create_user_db_func`.
    user_manager_settings : dict
        Keyword arguments passed to :func:`msdss_users_api.tools.create_user_manager`

        Requires at least the following parameters:

        * ``reset_password_token_secret`` (str): secret used to secure password reset tokens- use a strong phrase (e.g. ``openssl rand -hex 32``)
        * ``verification_token_secret`` (str): secret used to secure verification tokens - use a strong phrase (e.g. ``openssl rand -hex 32``)

    UserManager : :class:`msdss_users_api.managers.UserManager` or None
        The user manager model from FastAPI Users. See :class:`msdss_users_api.managers.UserManager` and :func:`msdss_users_api.tools.create_user_manager`. If ``None``, one will be created from ``user_manager_settings``.
    load_env : bool
        Whether to load variables from a file with environmental variables at ``env_file`` or not.
    env : :class:`msdss_users_api.env.UsersDotEnv`
        Object to load environment variables from. If the ``env_file`` and variable exists, it will overwrite parameters ``reset_password_token`` and ``verification_token_secret``.

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

        # Create a database object
        db = Database()._connection

        # Get the user db func
        get_user_db = create_user_db_func(db)

        # Create user manager secrets
        user_manager_settings = dict(
            reset_password_token_secret='reset-secret',
            verification_token_secret='verification-secret'
        )
        
        # Get user manager context
        get_user_manager_context = create_user_manager_context(
            get_user_db,
            user_manager_settings=user_manager_settings
        )
    """
    
    # (get_user_manager_context_env) Load env vars
    if env.exists() and load_env:
        env.load()
        user_manager_settings['reset_password_token_secret'] = env.get('reset_password_token_secret')
        user_manager_settings['verification_token_secret'] = env.get('verification_token_secret')

    # (get_user_manager_context_func) Create user manager func
    UserManager = UserManager if UserManager else create_user_manager(**user_manager_settings)
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
    UserManager : :class:`msdss_users_api.managers.UserManager`
        The user manager model from FastAPI Users. See :class:`msdss_users_api.managers.UserManager`.

    Return
    ------
    func
        A function yielding a configured :class:`msdss_users_api.managers.UserManager`.

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
        db = Database()._connection

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

        # Create user manager secrets
        kwargs = dict(
            user_manager_settings=dict(
                reset_password_token_secret='reset-secret',
                verification_token_secret='verification-secret'
            )
        )

        # Del users
        await delete_user('test@example.com', user_manager_context_kwargs=kwargs)
        await register_user('test@example.com', 'msdss123', user_manager_context_kwargs=kwargs)
        await delete_user('test@example.com', user_manager_context_kwargs=kwargs)
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

async def get_user(email, show=False, include_hashed_password=False, user_db_context_kwargs={}, user_manager_context_kwargs={}):
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
    user_db_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_db_context`.
    user_manager_context_kwargs : dict
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

        # Create user manager secrets
        kwargs = dict(
            user_manager_settings=dict(
                reset_password_token_secret='reset-secret',
                verification_token_secret='verification-secret'
            )
        )

        # Try to delete user
        await delete_user('test@example.com', user_manager_context_kwargs=kwargs)

        # Get user
        await register_user('test@example.com', 'msdss123', user_manager_context_kwargs=kwargs)
        user = await get_user('test@example.com', show=True, user_manager_context_kwargs=kwargs)
        await delete_user('test@example.com', user_manager_context_kwargs=kwargs)
    """

    # (get_user_context) Get db and manager context functions
    user_db_context = create_user_db_context(**user_db_context_kwargs)
    get_user_db_context = user_db_context['get_user_db_context']
    get_user_db = user_db_context['get_user_db']
    async_database= user_db_context['async_database']
    get_user_manager_context = create_user_manager_context(get_user_db=get_user_db, **user_manager_context_kwargs)

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
    user_db_context_kwargs={},
    user_manager_context_kwargs={},
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
    user_db_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_db_context`.
    user_manager_context_kwargs : dict
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

        # Create user manager secrets
        kwargs = dict(
            user_manager_settings=dict(
                reset_password_token_secret='reset-secret',
                verification_token_secret='verification-secret'
            )
        )

        # Try to delete user
        await delete_user('test@example.com', user_manager_context_kwargs=kwargs)
        
        # Register user
        await register_user('test@example.com', 'msdss123', user_manager_context_kwargs=kwargs)
        await delete_user('test@example.com', user_manager_context_kwargs=kwargs)
    """
    
    # (register_user_context) Get db and manager context functions
    user_db_context = create_user_db_context(**user_db_context_kwargs)
    get_user_db_context = user_db_context['get_user_db_context']
    get_user_db = user_db_context['get_user_db']
    async_database= user_db_context['async_database']
    get_user_manager_context = create_user_manager_context(get_user_db=get_user_db, **user_manager_context_kwargs)

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

async def reset_user_password(email, password, user_db_context_kwargs={}, user_manager_context_kwargs={}):
    """
    Reset password for a user.

    Parameters
    ----------
    email : str
        Email for the user.
    password : str
        New password for the user.
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

        # Create user manager secrets
        kwargs = dict(
            user_manager_settings=dict(
                reset_password_token_secret='reset-secret',
                verification_token_secret='verification-secret'
            )
        )

        # Try to delete user
        await delete_user('test@example.com', user_manager_context_kwargs=kwargs)

        # Reset user
        await register_user('test@example.com', 'msdss123', user_manager_context_kwargs=kwargs)
        await reset_user_password('test@example.com', 'msdss321', user_manager_context_kwargs=kwargs)
        await delete_user('test@example.com', user_manager_context_kwargs=kwargs)
    """

    # (reset_user_password_context) Get db and manager context functions
    user_db_context = create_user_db_context(**user_db_context_kwargs)
    get_user_db_context = user_db_context['get_user_db_context']
    get_user_db = user_db_context['get_user_db']
    async_database= user_db_context['async_database']
    get_user_manager_context = create_user_manager_context(get_user_db=get_user_db, **user_manager_context_kwargs)

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
    user_db_context_kwargs={},
    user_manager_context_kwargs={},
    *args, **kwargs):
    """
    Update a user.

    Parameters
    ----------
    email : str
        Email for the user.
    user_db_context_kwargs : dict
        Arguments passed to :class:`msdss_users_api.tools.create_user_db_context`.
    user_manager_context_kwargs : dict
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

        # Create user manager secrets
        kwargs = dict(
            user_manager_settings=dict(
                reset_password_token_secret='reset-secret',
                verification_token_secret='verification-secret'
            )
        )

        # Try to delete user
        await delete_user('test@example.com', user_manager_context_kwargs=kwargs)
        
        # Create a test user
        await register_user('test@example.com', 'msdss123', user_manager_context_kwargs=kwargs)
        print('\\nbefore_update:\\n')
        user = await get_user('test@example.com', show=True, user_manager_context_kwargs=kwargs)
        
        # Update the test user
        await update_user('test@example.com', is_verified=True, user_manager_context_kwargs=kwargs)
        print('\\nafter_update:\\n')
        user = await get_user('test@example.com', show=True, user_manager_context_kwargs=kwargs)
        await delete_user('test@example.com', user_manager_context_kwargs=kwargs)
    """
    
    # (register_user_context) Get db and manager context functions
    user_db_context = create_user_db_context(**user_db_context_kwargs)
    get_user_db_context = user_db_context['get_user_db_context']
    get_user_db = user_db_context['get_user_db']
    async_database= user_db_context['async_database']
    get_user_manager_context = create_user_manager_context(get_user_db=get_user_db, **user_manager_context_kwargs)

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