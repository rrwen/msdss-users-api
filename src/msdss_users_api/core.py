import databases

from fastapi import FastAPI
from msdss_base_api import API
from msdss_base_database import Database

from .env import *
from .models import *
from .routers import *
from .tools import *

class UsersAPI(API):
    """
    Users API class for managing users.
    
    * Extends the :class:`msdss_base_api:msdss_base_api.core.API` class
    * Users will be stored in a table named ``user``

    Parameters
    ----------
    cookie_secret : str or None
        A secret for cookie encryption. Use a strong phrase (e.g. ``openssl rand -hex 32``).
        If ``None``, the value will be taken from the environment variables. See parameter ``env``.
    jwt_secret : str or None
        A secret for JWT encryption. Use a strong phrase (e.g. ``openssl rand -hex 32``).
        If ``None``, the value will be taken from the environment variables. See parameter ``env``.
    reset_password_token_secret : str or None
        Secret used to secure password reset tokens. Use a strong phrase (e.g. ``openssl rand -hex 32``).
        If ``None``, the value will be taken from the environment variables. See parameter ``env``.
    verification_token_secret : str or None
        Secret used to secure verification tokens. Use a strong phrase (e.g. ``openssl rand -hex 32``).
        If ``None``, the value will be taken from the environment variables. See parameter ``env``.
    database : :class:`msdss_base_database.msdss_base_database.core.Database`
        Database to use for managing users.
    users_router_settings : dict
        Keyword arguments passed to :func:`msdss_users_api.routers.get_users_router`.

        * The parameter ``api_objects`` will replace the related parameters in ``get_users_router`` 

    api_objects : dict or None
        Dictionary returned from :func:`msdss_users_api.tools.create_api_objects`.
        If ``None``, then one will be setup based on parameter ``api_objects_settings``.
    api_objects_settings : dict
        Keyword arguments to be passed to :func:`msdss_users_api.tools.create_api_objects`.

        * The parameters ``cookie_secret`` and ``jwt_secret`` will overwrite the related keys inside ``cookie_settings`` and ``jwt_settings`` respectively
        * The parameters ``reset_password_token_secret`` and ``verification_token_secret`` will overwrite the related keys inside ``user_manager_settings``
    
    load_env : bool
        Whether to load variables from a file with environmental variables at ``env_file`` or not.
    env : :class:`msdss_base_database.env.DatabaseDotEnv`
        An object to set environment variables related to users configuration.
        These environment variables will overwrite the parameters above if they exist.

        By default, the related parameters above are assigned to each of the environment variables seen below if ``load_env`` is ``True``:

        .. jupyter-execute::
            :hide-code:

            from msdss_users_api.defaults import DEFAULT_DOTENV_KWARGS
            defaults = {k:v for k, v in DEFAULT_DOTENV_KWARGS.items() if k not in ['defaults', 'env_file', 'key_path']}
            print('<parameter> = <environment variable>\\n')
            for k, v in defaults.items():
                print(k + ' = ' + v)

    api : :class:`fastapi:fastapi.FastAPI`
        API object for creating routes.
    *args, **kwargs
        Additional arguments passed to :class:`msdss_base_api:msdss_base_api.core.API`.

    Attributes
    ----------
    database : :class:`msdss_base_database:msdss_base_database.core.Database`
        Database object for users API.
    misc : dict
        Dictionary of miscellaneous values:

        * ``users_api_objects`` (dict): see parameter ``api_objects``

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::
        :hide-output:

        from msdss_users_api import UsersAPI

        # Create users api app
        app = UsersAPI(
            cookie_secret='cookie-secret', # CHANGE TO STRONG PHRASE
            jwt_secret='jwt-secret', # CHANGE TO STRONG PHRASE
            reset_password_token_secret='reset-secret', # CHANGE TO STRONG PHRASE
            verification_token_secret='verification-secret' # CHANGE TO STRONG PHRASE
        )

        # Run the app with app.start()
        # Try API at http://localhost:8000/docs
        # app.start()
    """
    def __init__(
        self,
        cookie_secret=None,
        jwt_secret=None,
        reset_password_token_secret=None,
        verification_token_secret=None,
        database=Database(),
        users_router_settings={},
        api_objects=None,
        api_objects_settings={},
        load_env=True,
        env=UsersDotEnv(),
        api=FastAPI(
            title='MSDSS Users API',
            version='0.2.0'
        ),
        *args, **kwargs):
        super().__init__(api=api, *args, **kwargs)
        
        # (UsersAPI_env) Set env vars
        if env.exists() and load_env:
            env.load()
            cookie_secret = env.get('cookie_secret', cookie_secret)
            jwt_secret = env.get('jwt_secret', jwt_secret)
            reset_password_token_secret = env.get('reset_password_token_secret', reset_password_token_secret)
            verification_token_secret = env.get('verification_token_secret', verification_token_secret)

        # (UsersAPI_manager) Setup manager settings
        api_objects_settings['user_manager_settings'] = api_objects_settings.get('user_manager_settings', {})
        api_objects_settings['user_manager_settings']['reset_password_token_secret'] = reset_password_token_secret
        api_objects_settings['user_manager_settings']['verification_token_secret'] = verification_token_secret

        # (UsersAPI_cookie) Setup cookie settings
        api_objects_settings['cookie_settings'] = api_objects_settings.get('cookie_settings', {})
        print(env.get('cookie_secret'))
        api_objects_settings['cookie_settings']['secret'] = cookie_secret

        # (UsersAPI_jwt) Setup jwt settings
        api_objects_settings['jwt_settings'] = api_objects_settings.get('jwt_settings', {})
        api_objects_settings['jwt_settings']['secret'] = jwt_secret

        # (UsersAPI_database) Setup database
        api_objects_settings['database'] = database

        # (UsersAPI_objects) Create FastAPI Users objects
        api_objects = api_objects if api_objects else create_api_objects(**api_objects_settings)

        # (UsersAPI_attr) Add attributes
        self.misc = dict(users_api_objects=api_objects)
        self.database = database

        # (UsersAPI_router) Add users router
        users_router_settings['api_objects'] = api_objects
        users_router = get_users_router(**users_router_settings)
        self.add_router(users_router)

        # (UserAPI_startup) Setup app startup
        async_database = api_objects['databases']['async_database']
        @self.event('startup')
        async def startup():
            await async_database.connect()

        # (UserAPI_shutdown) Setup app shutdown
        @self.event('shutdown')
        async def shutdown():
            await async_database.disconnect()

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

            # Create users api app
            app = UsersAPI(
                cookie_secret='cookie-secret', # CHANGE TO STRONG PHRASE
                jwt_secret='jwt-secret', # CHANGE TO STRONG PHRASE
                reset_password_token_secret='reset-secret', # CHANGE TO STRONG PHRASE
                verification_token_secret='verification-secret' # CHANGE TO STRONG PHRASE
            )

            # Get a function dependency for the current active user
            current_active_user = app.get_current_user(active=True)

            # Add a protected route
            @app.route('GET', '/protected-route')
            def protected_route(user: User = Depends(current_active_user)):
                return f'Hello, {user.email}'

            # Run the app with app.start()
            # Try API at http://localhost:8000/docs
            # app.start()
        """
        out = self.misc['users_api_objects']['users_api'].current_user(*args, **kwargs)
        return out