from copy import deepcopy
from fastapi import APIRouter, Depends, Response

from .defaults import *
from .tools import *

def get_users_router(
    fastapi_users_objects=None,
    route_settings=DEFAULT_USERS_ROUTE_SETTINGS,
    *args, **kwargs):
    """
    Get a users router.

    Parameters
    ----------
    fastapi_users_objects : dict
        Dictionary returned from :func:`msdss_users_api.tools.create_fastapi_users_objects`.
    route_settings : dict
        Dictionary of settings for the users routes. Each route consists of the following keys:

        * ``path``: resource path for the route
        * ``tags``: tags for open api spec
        * ``_enable`` (bool): Whether this route should be included or not
        * ``_get_user`` (dict or None): Additional arguments passed to the :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` function for the route - if ``None``, a dependency will not be added
        * ``_enable_refresh (bool): Only applies to ``jwt`` route - whether to include a jwt refresh route or not
        * ``**kwargs``: Additional arguments passed to the :meth:`fastapi:fastapi.FastAPI.include_router` method for this route
        
        The default settings are:
        
        .. jupyter-execute::
            :hide-code:

            from msdss_users_api.defaults import DEFAULT_USERS_ROUTE_SETTINGS
            from pprint import pprint
            pprint(DEFAULT_USERS_ROUTE_SETTINGS)
        
        Any unspecified settings will be replaced by their defaults.

    *args, **kwargs
        Additional arguments passed to :class:`fastapi:fastapi.routing.APIRouter`.
    
    Returns
    -------
    :class:`fastapi:fastapi.routing.APIRouter`
        A router object used users routes. See `FastAPI bigger apps <https://fastapi.tiangolo.com/tutorial/bigger-applications/>`_.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_base_api import API
        from msdss_users_api.tools import create_fastapi_users_objects
        from msdss_users_api.routers import get_users_router

        # Create an app
        app = API()

        # Setup user manager secrets
        user_manager_settings = dict(
            reset_password_token_secret='reset-secret', # CHANGE TO STRONG PHRASE
            verification_token_secret='verify-secret' # CHANGE TO STRONG PHRASE
        )

        # Setup jwt and cookie secret
        jwt_settings = dict(secret='jwt-secret') # CHANGE TO STRONG PHRASE
        cookie_settings = dict(secret='cookie-secret') # CHANGE TO STRONG PHRASE

        # Create FastAPI Users objects
        fastapi_users_objects = create_fastapi_users_objects(
            user_manager_settings=user_manager_settings,
            jwt_settings=jwt_settings,
            cookie_settings=cookie_settings
        )

        # Add the users router
        router = get_users_router(fastapi_users_objects)
        app.add_router(router)

        # Setup startup and shutdown
        async_database = fastapi_users_objects['databases']['async_database']

        @app.event('startup')
        async def startup():
            await async_database.connect()

        @app.event('shutdown')
        async def shutdown():
            await async_database.disconnect()

        # Host app at https://localhost:8000
        # Try it at https://localhost:8000/docs
        # app.start()
    """

    # (get_users_router_create) Create api router for users routes
    out = APIRouter(*args, **kwargs)

    # (get_users_router_api) Create users api objs
    users_api = fastapi_users_objects['FastAPIUsers']
    jwt = fastapi_users_objects['auth']['jwt']
    cookie = fastapi_users_objects['auth']['cookie']
    UserManager = fastapi_users_objects['models']['UserManager']

    # (get_users_router_defaults) Merge defaults and user params 
    settings = deepcopy(DEFAULT_USERS_ROUTE_SETTINGS)
    for k in settings:
        if k in route_settings:
            settings[k].update(route_settings[k])

    # (get_users_router_apply) Apply settings to obtain dependencies
    get_user = {}
    enable = {}
    for k, v in settings.items():
        get_user[k] = users_api.current_user(**v['_get_user']) if users_api and v['_get_user'] else None
        del v['_get_user']
        enable[k] = v.pop('_enable')
    enable_jwt_refresh = settings['jwt'].pop('_enable_refresh', True)

    # (get_users_route_jwt) Add jwt auth route
    if enable['jwt']:

        # (get_users_route_jwt_create) Create jwt route
        jwt_router = users_api.get_auth_router(jwt)
        
        # (get_users_route_jwt_refresh) Create jwt refresh route
        if enable_jwt_refresh:
            @jwt_router.post('/refresh')
            async def refresh_jwt(response: Response, user=Depends(users_api.current_user(active=True))):
                return await jwt.get_login_response(user, response, UserManager)

        # (get_users_route_jwt_include) Include jwt route
        out.include_router(jwt_router, **settings['jwt'])

    # (get_users_route_auth_cookie) Add cookie auth route
    if enable['cookie']:
        auth_cookie_router = users_api.get_auth_router(cookie)
        out.include_router(auth_cookie_router, **settings['cookie'])

    # (get_users_route_register) Add register router
    if enable['register']:
        if get_user['register']:
            settings['register']['dependencies'] = settings['register'].get('dependencies', [])
            settings['register']['dependencies'].append(Depends(get_user['register']))
        register_router = users_api.get_register_router()
        out.include_router(register_router, **settings['register'])

    # (get_users_route_verify) Add verify router
    if enable['verify']:
        if get_user['verify']:
            settings['verify']['dependencies'] = settings['verify'].get('dependencies', [])
            settings['verify']['dependencies'].append(Depends(get_user['verify']))
        verify_router = users_api.get_verify_router()
        out.include_router(verify_router, **settings['verify'])
    
    # (get_users_route_reset) Add reset password router
    if enable['reset']:
        if get_user['reset']:
            settings['reset']['dependencies'] = settings['reset'].get('dependencies', [])
            settings['reset']['dependencies'].append(Depends(get_user['reset']))
        reset_router = users_api.get_reset_password_router()
        out.include_router(reset_router, **settings['reset'])

    # (get_users_route_users) Add users router
    if enable['users']:
        if get_user['users']:
            settings['users']['dependencies'] = settings['users'].get('dependencies', [])
            settings['users']['dependencies'].append(Depends(get_user['users']))
        users_router = users_api.get_users_router()
        out.include_router(users_router, **settings['users'])

    return out
