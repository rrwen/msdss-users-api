import databases
import os

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieAuthentication, JWTAuthentication
from msdss_base_api import API
from msdss_base_database import Database
from msdss_base_dotenv import env_exists, load_env_file

from .models import *
from .tools import *

class UsersAPI(API):
    """
    Users API class for managing users. Extends the :class:`msdss_base_api:msdss_base_api.core.API` class.

    Parameters
    ----------
    secret : str
        A secret for security encryption and protecting user data. Use a strong phrase (e.g. ``openssl rand -hex 32``).
    driver : str
        The driver name of the database connection, which are commonly ``postgresql``, ``sqlite``, ``mysql``, ``oracle`` or ``mssql``.  (see `SQLAlchemy supported databases <https://docs.sqlalchemy.org/en/14/core/engines.html#supported-databases>`_).
    user : str
        User name for the connection.
    password : str
        Password for the user.
    host : str
        Host address of the connection.
    port : str
        Port number of the connection.
    database : str
        Database name of the connection.
    users_api : :class:`fastapi_users:fastapi_users.FastAPIUsers` or None
        FastAPI Users object. See `FastAPIUsers object <https://fastapi-users.github.io/fastapi-users/configuration/routers/>`_.
        If ``None``, then one will be setup based on other parameters.
    users_api=None,

    use_auth_router=True,

    use_register_router=True,

    use_verify_router=True,

    use_reset_password_router=True,

    use_users_router=True,

    setup_startup=True,

    setup_shutdown=True,

    auth_router_auth='jwt',

    auth_router_kwargs={},

    auth_router_include_kwargs={
        'prefix': '/auth/jwt',
        'tags': ['auth']
    },

    register_router_kwargs={},

    register_router_include_kwargs={
        'prefix': '/auth',
        'tags': ['auth']
    },

    verify_router_kwargs={},

    verify_router_include_kwargs={
        'prefix': '/auth',
        'tags': ['auth']
    },

    reset_password_router_kwargs={},

    reset_password_router_include_kwargs={
        'prefix': '/auth',
        'tags': ['auth']
    },

    users_router_kwargs={},

    users_router_include_kwargs={
        'prefix': '/users',
        'tags': ['users']
    },

    reset_password_token_secret : str,
        Secret used to secure verification tokens. If ``None``, it will default to param ``secret``.
    verification_token_secret : str or None
        Secret used to secure verification tokens. If ``None``, it will default to param ``secret``.
    cookie_secret : str or None
        Secret used to secure cookies. If ``None``, it will default to param ``secret``.
    cookie_kwargs : dict
        Dictionary of keyword arguments passed to :class:`fastapi_users:fastapi_users.authentication.CookieAuthentication`. See `CookieAuthentication <https://fastapi-users.github.io/fastapi-users/configuration/authentication/cookie/>`_.
    jwt_secret : str or None
        Secret used to secure JWT tokens. If ``None``, it will default to param ``secret``.
    jwt_kwargs : dict
        Dictionary of keyword arguments passed to :class:`fastapi_users:fastapi_users.authentication.JWTAuthentication`.  See `JWTAuthentication <https://fastapi-users.github.io/fastapi-users/configuration/authentication/jwt/>`_.
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
    database_engine : :func:`sqlalchemy:sqlalchemy.create_engine` or  None
        SQLAlchemy engine object. If ``None``, one will be created from the database connection params.
    async_database : :class:`databases:databases.Database` or None
        Async database object from ``databases``. If ``None``, one will be created from database connection params.
    get_user_db : func or None
        Function for getting the FastAPI Users DB object. If ``None``, one will be setup from params. See ``FastAPI Users database config <https://fastapi-users.github.io/fastapi-users/configuration/databases/sqlalchemy/>``_.
    get_user_manager : func or None
        Function for getting the FastAPI UserManager object. If ``None``, one will be setup from params. See ``FastAPI Users UserManager <https://fastapi-users.github.io/fastapi-users/configuration/user-manager/>``_.
    cookie_auth : :class:`fastapi_users:fastapi_users.authentication.CookieAuthentication` or None
        A cookie authentication object from FastAPI Users. See `CookieAuthentication <https://fastapi-users.github.io/fastapi-users/configuration/authentication/cookie/>`_.
    jwt_auth : :class:`fastapi_users:fastapi_users.authentication.JWTAuthentication` or None
        A JSON Web Token (JWT) authentication object from FastAPI Users. See `JWTAuthentication <https://fastapi-users.github.io/fastapi-users/configuration/authentication/jwt/>`_.
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
    *args, **kwargs
        Additional arguments passed to :class:`fastapi_users:fastapi_users.FastAPIUsers`.

    Attributes
    ----------
    users_api : :class:`fastapi_users:fastapi_users.FastAPIUsers`
        Configured FastAPI Users object. See `FastAPIUsers object <https://fastapi-users.github.io/fastapi-users/configuration/routers/>`_.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_base_api.core import API
        app = API()

        # Add route via function
        def hello_world():
            return "hello world!"
        app.add_route("GET", "/", hello_world)

        # Add route via decorator
        @app.add("GET", "/two")
        def hello_world2():
            return "hello world 2!"

        # Run the app with app.start()
        # API is hosted at http://localhost:8000
        # app.start()
    """
    def __init__(
        self,
        secret='msdss-secret',
        driver='postgresql',
        user='msdss',
        password='msdss123',
        host='localhost',
        port='5432',
        database='msdss',
        users_api=None,
        use_auth_router=True,
        use_register_router=True,
        use_verify_router=True,
        use_reset_password_router=True,
        use_users_router=True,
        setup_startup=True,
        setup_shutdown=True,
        auth_router_auth='jwt',
        auth_router_kwargs={},
        auth_router_include_kwargs={
            'prefix': '/auth/jwt',
            'tags': ['auth']
        },
        register_router_kwargs={},
        register_router_include_kwargs={
            'prefix': '/auth',
            'tags': ['auth']
        },
        verify_router_kwargs={},
        verify_router_include_kwargs={
            'prefix': '/auth',
            'tags': ['auth']
        },
        reset_password_router_kwargs={},
        reset_password_router_include_kwargs={
            'prefix': '/auth',
            'tags': ['auth']
        },
        users_router_kwargs={},
        users_router_include_kwargs={
            'prefix': '/users',
            'tags': ['users']
        },
        reset_password_token_secret=None,
        verification_token_secret=None,
        cookie_secret=None,
        cookie_kwargs={'lifetime_seconds': 3600},
        jwt_secret=None,
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
        database_engine=None,
        async_database=None,
        get_user_db=None,
        get_user_manager=None,
        cookie_auth=None,
        jwt_auth=None,
        load_env=True,
        env_file='./.env',
        key_path=None,
        secret_key='MSDSS_USERS_SECRET',
        jwt_secret_key='MSDSS_USERS_JWT_SECRET',
        cookie_secret_key='MSDSS_USERS_COOKIE_SECRET',
        reset_password_token_secret_key='MSDSS_USERS_RESET_PASSWORD_TOKEN_SECRET',
        verification_token_secret_key='MSDSS_USERS_VERIFICATION_TOKEN_SECRET',
        driver_key='MSDSS_DATABASE_DRIVER',
        user_key='MSDSS_DATABASE_USER',
        password_key='MSDSS_DATABASE_PASSWORD',
        host_key='MSDSS_DATABASE_HOST',
        port_key='MSDSS_DATABASE_PORT',
        database_key='MSDSS_DATABASE_NAME',
        *args, **kwargs):
        super().__init__()

        # (UserAPI_env) Load env vars
        has_env = env_exists(file_path=env_file, key_path=key_path)
        if load_env and has_env:
            load_env_file(file_path=env_file, key_path=key_path)
            secret = os.getenv(secret_key, secret)
            jwt_secret = os.getenv(jwt_secret_key, jwt_secret)
            cookie_secret = os.getenv(cookie_secret_key, cookie_secret)
            reset_password_token_secret = os.getenv(reset_password_token_secret_key, reset_password_token_secret_key)
            verification_token_secret = os.getenv(verification_token_secret_key, verification_token_secret)
            driver = os.getenv(driver_key, driver)
            user = os.getenv(user_key, user)
            password = os.getenv(password_key, password)
            host = os.getenv(host_key, host)
            port = os.getenv(port_key, port)
            database = os.getenv(database_key, database)

        # (UserAPI_vars) Setup vars
        jwt_secret = secret if jwt_secret is None else jwt_secret
        cookie_secret = secret if cookie_secret is None else cookie_secret

        # (UserAPI_db) Setup database connections
        database_engine = Database(driver=driver, user=user, password=password, host=host, port=port, database=database)._connection if database_engine is None else database_engine
        async_database = databases.Database(str(database_engine.url)) if async_database is None else async_database

        # (UserAPI_auth) Setup auth for users
        jwt_auth = JWTAuthentication(secret=jwt_secret, **jwt_kwargs) if jwt_secret and jwt_auth is None else jwt_auth
        cookie_auth = CookieAuthentication(secret=cookie_secret, **cookie_kwargs) if cookie_secret and cookie_auth is None else cookie_auth
        
        # (UserAPI_auth_combine) Combine cookie and jwt auths if needed
        jwt_auth = [jwt_auth] if not isinstance(jwt_auth, list) else jwt_auth
        cookie_auth = [cookie_auth] if not isinstance(cookie_auth, list) else cookie_auth
        auth = [a for a in cookie_auth + jwt_auth if a is not None]
        
        # (UserAPI_func) Setup required functions
        get_user_db = create_user_db_func(database_engine, async_database, sqlalchemy_base=Base, user_table_model=UserTable, user_db_model=UserDB) if get_user_db is None else get_user_db
        get_user_manager = create_user_manager_func(get_user_db, secret, reset_password_token_secret=reset_password_token_secret, verification_token_secret=verification_token_secret) if get_user_manager is None else get_user_manager

        # (UserAPI_api) Setup users api obj
        users_api = FastAPIUsers(
            get_user_manager,
            auth,
            User,
            UserCreate,
            UserUpdate,
            UserDB,
            *args, **kwargs
        ) if users_api is None else users_api

        # (UsersAPI_router_auth) Add auth router
        if use_auth_router:

            # (UsersAPI_router_auth_method) Set method of auth for route
            print(str(jwt_auth))
            if auth_router_auth == 'jwt':
                auth_router_auth = jwt_auth[0]
            elif auth_router_auth == 'cookie':
                auth_router_auth = cookie_auth[0]

            # (UsersAPI_router_auth_add) Add auth route
            self.app.include_router(users_api.get_auth_router(auth_router_auth, **auth_router_kwargs), **auth_router_include_kwargs)

        # (UsersAPI_router_register) Add register router
        if use_register_router:
            self.app.include_router(users_api.get_register_router(**register_router_kwargs), **register_router_include_kwargs)

        # (UsersAPI_router_verify) Add verify router
        if use_verify_router:
            self.app.include_router(users_api.get_verify_router(**verify_router_kwargs), **verify_router_include_kwargs)
        
        # (UsersAPI_router_reset) Add reset password router
        if use_reset_password_router:
            self.app.include_router(users_api.get_reset_password_router(**reset_password_router_kwargs), **reset_password_router_include_kwargs)

        # (UsersAPI_router_reset) Add reset password router
        if use_users_router:
            self.app.include_router(users_api.get_users_router(**users_router_kwargs), **users_router_include_kwargs)

        # (UserAPI_events_startup) Setup app startup
        if setup_startup:
            @self.on('startup')
            async def before_startup():
                await async_database.connect()

        # (UserAPI_events_shutdown) Setup app shutdown
        if setup_shutdown:
            @self.on('shutdown')
            async def during_shutdown():
                await async_database.disconnect()

        # (UserAPI_attr) Add attributes
        self.users_api = users_api
        self._database_engine = database_engine
        self._async_database = async_database