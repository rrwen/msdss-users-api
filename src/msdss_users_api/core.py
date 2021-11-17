import databases
import os

from fastapi import Depends, Response
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieAuthentication, JWTAuthentication
from msdss_base_api import API
from msdss_base_database import Database
from msdss_base_dotenv import env_exists, load_env_file

from .models import *
from .tools import *

class UsersAPI(API):
    """
    Users API class for managing users.
    
    * Extends the :class:`msdss_base_api:msdss_base_api.core.API` class
    * Users will be stored in a table named ``user``

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
    users_api : :class:`fastapi_users:fastapi_users.FastAPIUsers` or None
        A FastAPIUsers object to setup routes with. If ``None``, one will be setup using the params.
    enable_auth_router : bool
        Whether to include the Fast API Users api route.
    enable_register_router : bool
        Whether to include the Fast API Users register route.
    enable_verify_router : bool
        Whether to include the Fast API Users verify route.
    enable_reset_password_router : bool
        Whether to include the Fast API Users reset password route.
    enable_users_router : bool
        Whether to include the Fast API Users users route.
    enable_jwt_auth : bool
        Whether to use JWT auth or not.
    enable_cookie_auth : bool
        Whether to use cookie auth or not.
    setup_startup : bool
        Whether to setup a startup event to connect databases.
    setup_shutdown : bool
        Whether to setup a shutdown event to close databases.
    auth_router_jwt_kwargs : dict
        Keyword arguments passed to :meth:`fastapi_users:fastapi_users.FastAPIUsers.get_auth_router` using jwt auth. See `Auth router <https://fastapi-users.github.io/fastapi-users/configuration/routers/auth/>`_.
    auth_router_jwt_include_kwargs : dict
        Keyword arguments passed to :meth:`fastapi:fastapi.FastAPI.include_router` for the FastAPI Users auth router using jwt auth.
    auth_router_jwt_refresh : bool
        Whether to setup a token refresh route at ``auth_router_jwt_refresh_path``. This is setup according to the FastAPI Users `JWT authentication guide <https://fastapi-users.github.io/fastapi-users/configuration/authentication/jwt/>`_.
    auth_router_jwt_refresh_path : str
        Path to setup refresh token if ``auth_router_jwt_refresh`` is ``True``.
    auth_router_cookie_kwargs : dict
        Keyword arguments passed to :meth:`fastapi_users:fastapi_users.FastAPIUsers.get_auth_router` using cookie auth. See `Auth router <https://fastapi-users.github.io/fastapi-users/configuration/routers/auth/>`_.
    auth_router_cookie_include_kwargs : dict
        Keyword arguments passed to :meth:`fastapi:fastapi.FastAPI.include_router` for the FastAPI Users auth router using cookie auth.
    register_router_kwargs : dict
        Keyword arguments passed to :meth:`fastapi_users:fastapi_users.FastAPIUsers.get_register_router`. See `Register router <https://fastapi-users.github.io/fastapi-users/configuration/routers/register/>`_.
    register_router_include_kwargs : dict
        Keyword arguments passed to :meth:`fastapi:fastapi.FastAPI.include_router` for the FastAPI Users register router.
    register_router_superuser : bool
        Whether to limit registration control to superusers only. If ``dependencies`` are set in parameter ``register_router_include_kwargs``, then a superuser dependency will be added to the list if ``True``.
    verify_router_kwargs : dict
        Keyword arguments passed to :meth:`fastapi_users:fastapi_users.FastAPIUsers.get_verify_router`. See `Verify router <https://fastapi-users.github.io/fastapi-users/configuration/routers/verify/>`_.
    verify_router_include_kwarg : dict
        Keyword arguments passed to :meth:`fastapi:fastapi.FastAPI.include_router` for the FastAPI Users verify router.
    reset_password_router_kwargs : dict
        Keyword arguments passed to :meth:`fastapi_users:fastapi_users.FastAPIUsers.get_reset_password_router`. See `Reset password router <https://fastapi-users.github.io/fastapi-users/configuration/routers/reset/>`_.
    reset_password_router_include_kwargs : dict
        Keyword arguments passed to :meth:`fastapi:fastapi.FastAPI.include_router` for the FastAPI Users reset password router.
    users_router_kwargs : dict
        Keyword arguments passed to :meth:`fastapi_users:fastapi_users.FastAPIUsers.get_users_router`. See `Users router <https://fastapi-users.github.io/fastapi-users/configuration/routers/users/>`_.
    users_router_include_kwargs : dict
        Keyword arguments passed to :meth:`fastapi:fastapi.FastAPI.include_router` for the FastAPI Users users router.
    reset_password_token_secret : str
        Secret used to secure password reset tokens. If ``None``, it will default to param ``secret``.
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
    UserManager : :class:`msdss_users_api.models.UserManager`
        UserManager model for FastAPI Users. See :class:`msdss_users_api.models.UserManager`.
    database_engine : :func:`sqlalchemy:sqlalchemy.create_engine` or  None
        SQLAlchemy engine object. If ``None``, one will be created from the database connection params.
    async_database : :class:`databases:databases.Database` or None
        Async database object from ``databases``. If ``None``, one will be created from database connection params.
    get_user_db : func or None
        Function for getting the FastAPI Users DB object. If ``None``, one will be setup from params. See `FastAPI Users database config <https://fastapi-users.github.io/fastapi-users/configuration/databases/sqlalchemy/>`_.
    get_user_manager : func or None
        Function for getting the FastAPI UserManager object. If ``None``, one will be setup from params. See `FastAPI Users UserManager <https://fastapi-users.github.io/fastapi-users/configuration/user-manager/>`_.
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
    secret_key : str
        The environmental variable name for ``secret``.
    jwt_secret_key : str
        The environmental variable name for ``jwt_secret``.
    cookie_secret_key : str
        The environmental variable name for ``cookie_secret``.
    reset_password_token_secret_key : str
        The environmental variable name for ``reset_password_token_secret``.
    verification_token_secret_key : str
        The environmental variable name for ``verification_token_secret``.
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
    log_warnings : bool
        Whether to log warnings or not.
    *args, **kwargs
        Additional arguments passed to :class:`msdss_base_api:msdss_base_api.core.API`.

    Attributes
    ----------
    users_api : :class:`fastapi_users:fastapi_users.FastAPIUsers`
        Configured FastAPI Users object. See `FastAPIUsers object <https://fastapi-users.github.io/fastapi-users/configuration/routers/>`_.
    _users_databases : dict
        Dictionary of user database related objects:

        * ``engine`` (:func:`sqlalchemy:sqlalchemy.create_engine`): Engine from parameter ``database_engine``.
        * ``asynchronous`` (:class:`databases:databases.Database`): Async database from parameter ``async_database``.
    
    _users_functions : dict(func)
        Dictionary of user related functions from auto-config:

        * ``get_user_db`` (func): get_user_db function auto-configured or from parameter ``get_user_db``. See :func:`msdss_users_api.tools.create_user_db_func`.
        * ``get_user_manager`` (func): get_user_manager function auto-configured or from parameter ``get_user_manager``. See :func`msdss_users_api.tools.create_user_manager_func`.
    
    _users_events : dict(func)
        Dictionary of event functions registered from auto-config:

        * ``startup``: startup function registered if ``setup_startup`` is ``True``
        * ``shutdown``: shutdown function registered if ``setup_shutdown`` is ``True``
    
    _users_models : dict
        Dictionary of user models for the users API:

        * User (:class:`msdss_users_api.models.User`): see parameter ``User``.
        * UserCreate (:class:`msdss_users_api.models.UserCreate`): see parameter ``UserCreate``.
        * UserUpdate (:class:`msdss_users_api.models.UserUpdate`): see parameter ``UserUpdate``.
        * UserDB (:class:`msdss_users_api.models.UserDB`): see parameter ``UserDB``.
        * UserTable (:class:`msdss_users_api.models.UserTable`): see parameter ``UserTable``.
        * UserManager (:class:`msdss_users_api.models.UserManager`): see parameter ``UserManager``.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::
        :hide-output:

        from msdss_users_api import UsersAPI
        app = UsersAPI(
            secret='secret-phrase',
            jwt_secret='secret-phrase-02',
            driver='postgresql',
            user='msdss',
            password='msdss123',
            host='localhost',
            port='5432',
            database='msdss'
        )

        # Run the app with app.start()
        # Try API at http://localhost:8000/docs
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
        enable_auth_router=True,
        enable_register_router=True,
        enable_verify_router=True,
        enable_reset_password_router=True,
        enable_users_router=True,
        enable_jwt_auth=True,
        enable_cookie_auth=True,
        setup_startup=True,
        setup_shutdown=True,
        auth_router_jwt_kwargs={},
        auth_router_jwt_include_kwargs={
            'prefix': '/auth/jwt',
            'tags': ['auth']
        },
        auth_router_jwt_refresh=True,
        auth_router_jwt_refresh_path='/refresh',
        auth_router_cookie_kwargs={},
        auth_router_cookie_include_kwargs={
            'prefix': '/auth',
            'tags': ['auth']
        },
        register_router_kwargs={},
        register_router_include_kwargs={
            'prefix': '/auth',
            'tags': ['auth']
        },
        register_router_superuser=True,
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
        UserManager=None,
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
        log_warnings=True,
        *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        
        # (UserAPI_warn) Warn if default secret is used
        if secret == 'msdss-secret' and log_warnings:
            self.logger.warning('Default secret was used - please change secret phrase!')

        # (UserAPI_vars) Setup vars
        jwt_secret = secret if jwt_secret is None else jwt_secret
        cookie_secret = secret if cookie_secret is None else cookie_secret

        # (UserAPI_db) Setup database connections
        db = Database(driver=driver, user=user, password=password, host=host, port=port, database=database)
        database_engine = db._connection if database_engine is None else database_engine
        async_database = databases.Database(str(database_engine.url)) if async_database is None else async_database

        # (UserAPI_auth) Setup auth for users
        jwt_auth = JWTAuthentication(secret=jwt_secret, **jwt_kwargs) if jwt_secret and jwt_auth is None else jwt_auth
        cookie_auth = CookieAuthentication(secret=cookie_secret, **cookie_kwargs) if cookie_secret and cookie_auth is None else cookie_auth
        
        # (UserAPI_auth_combine) Combine cookie and jwt auths if needed
        auth = []
        if enable_cookie_auth:
            auth.append(cookie_auth)
        if enable_jwt_auth:
            auth.append(jwt_auth)
        auth = [a for a in auth if a is not None]
        
        # (UserAPI_func) Setup required functions
        get_user_db = create_user_db_func(database_engine, async_database, sqlalchemy_base=Base, user_table_model=UserTable, user_db_model=UserDB) if get_user_db is None else get_user_db
        UserManager = create_user_manager_model(secret, reset_password_token_secret=reset_password_token_secret, verification_token_secret=verification_token_secret) if UserManager is None else UserManager
        get_user_manager = create_user_manager_func(get_user_db, UserManager) if get_user_manager is None else get_user_manager

        # (UserAPI_api) Setup users api obj
        users_api = FastAPIUsers(
            get_user_manager,
            auth,
            User,
            UserCreate,
            UserUpdate,
            UserDB
        ) if users_api is None else users_api

        # (UsersAPI_router_auth) Add auth router
        if enable_auth_router:

            # (UsersAPI_router_auth_jwt) Add jwt auth route
            if enable_jwt_auth:

                # (UsersAPI_router_auth_jwt_method) Set method of auth for route
                auth_jwt_router = users_api.get_auth_router(jwt_auth, **auth_router_jwt_kwargs)
                
                # (UsersAPI_router_auth_jwt_refresh) Create jwt auth refresh route
                if auth_router_jwt_refresh:
                    @auth_jwt_router.post(auth_router_jwt_refresh_path)
                    async def refresh_jwt(response: Response, user=Depends(users_api.current_user(active=True))):
                        return await jwt_auth.get_login_response(user, response, UserManager)

                # (UsersAPI_router_auth_jwt_add) Add jwt auth route
                self.add_router(auth_jwt_router, **auth_router_jwt_include_kwargs)

            # (UsersAPI_router_auth_cookie) Add cookie auth route
            if enable_cookie_auth:

                    # (UsersAPI_router_auth_cookie_method) Set method of auth for route
                auth_cookie_router = users_api.get_auth_router(cookie_auth, **auth_router_cookie_kwargs)

                # (UsersAPI_router_auth_cookie_add) Add auth route
                self.add_router(auth_cookie_router, **auth_router_cookie_include_kwargs)

        # (UsersAPI_router_register) Add register router
        if enable_register_router:
            if register_router_superuser:
                register_router_include_kwargs['dependencies'] = register_router_include_kwargs['dependencies'] if 'dependencies' in register_router_include_kwargs else []
                register_router_include_kwargs['dependencies'].append(Depends(users_api.current_user(superuser=True)))
            register_router = users_api.get_register_router(**register_router_kwargs)
            self.add_router(register_router, **register_router_include_kwargs)

        # (UsersAPI_router_verify) Add verify router
        if enable_verify_router:
            verify_router = users_api.get_verify_router(**verify_router_kwargs)
            self.add_router(verify_router, **verify_router_include_kwargs)
        
        # (UsersAPI_router_reset) Add reset password router
        if enable_reset_password_router:
            reset_password_router = users_api.get_reset_password_router(**reset_password_router_kwargs)
            self.add_router(reset_password_router, **reset_password_router_include_kwargs)

        # (UsersAPI_router_users) Add users router
        if enable_users_router:
            users_router = users_api.get_users_router(**users_router_kwargs)
            self.add_router(users_router, **users_router_include_kwargs)

        # (UserAPI_attr) Add attributes
        self.users_api = users_api
        self.users_database = db
        self._users_databases = dict(
            engine = database_engine,
            asynchronous = async_database
        )
        self._users_functions = dict(
            get_user_db = get_user_db,
            get_user_manager = get_user_manager
        )
        self._users_models = dict(
            User = User,
            UserCreate = UserCreate,
            UserUpdate = UserUpdate,
            UserDB = UserDB,
            UserTable = UserTable,
            UserManager = UserManager
        )
        self._users_events = {}

        # (UserAPI_events_startup) Setup app startup
        if setup_startup:
            @self.on('startup')
            async def startup():
                await self._users_databases.asynchronous.connect()
            self._users_events['startup'] = startup

        # (UserAPI_events_shutdown) Setup app shutdown
        if setup_shutdown:
            @self.on('shutdown')
            async def shutdown():
                await self._users_databases.asynchronous.disconnect()
            self._users_events['shutdown'] = shutdown

    def get_current_user(self, *args, **kwargs):
        """
        Get a dependency function to retrieve the current authenticated user.

        Parameters
        ----------
        *args, **kwargs
            Additional arguments passed to :meth:`fastapi_users:fastapi_users.FastAPIUsers.current_user`. See `current_user <https://fastapi-users.github.io/fastapi-users/usage/current-user/>`_.

        Return
        ------
        func
            A function to retrieve the current authenticated user. Useful for adding protected routes accessible only by authenticated users.

        Author
        ------
        Richard Wen <rrwen.dev@gmail.com>

        Example
        -------
        .. jupyter-execute::
            :hide-output:

            from fastapi import Depends
            from msdss_users_api import UsersAPI
            from msdss_users_api.models import User

            app = UsersAPI(
                secret='secret-phrase',
                jwt_secret='secret-phrase-02',
                driver='postgresql',
                user='msdss',
                password='msdss123',
                host='localhost',
                port='5432',
                database='msdss'
            )

            # Get a function dependency for the current active user
            current_active_user = app.get_current_user(active=True)

            # Add a protected route
            @app.add('GET', '/protected-route')
            def protected_route(user: User = Depends(current_active_user)):
                return f'Hello, {user.email}'

            # Run the app with app.start()
            # Try API at http://localhost:8000/docs
            # app.start()
        """
        out = self.users_api.current_user(*args, **kwargs)
        return out