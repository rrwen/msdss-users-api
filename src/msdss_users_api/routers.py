from fastapi import APIRouter, Depends, Response

from .defaults import *
from .tools import *

def get_users_router(
    api_objects=None,
    api_objects_settings={},
    enable_cookie_route=True,
    enable_jwt_route=True,
    enable_jwt_refresh_route=True,
    enable_register_route=True,
    enable_verify_route=True,
    enable_reset_route=True,
    enable_users_route=True,
    jwt_route_settings={
        'prefix': '/auth/jwt',
        'tags': ['auth']
    },
    cookie_route_settings={
        'prefix': '/auth',
        'tags': ['auth']
    },
    register_route_settings={
        'prefix': '/auth',
        'tags': ['auth']
    },
    register_get_user_settings={
        'superuser': True
    },
    verify_route_settings={
        'prefix': '/auth',
        'tags': ['auth']
    },
    verify_get_user_settings=None,
    reset_route_settings={
        'prefix': '/auth',
        'tags': ['auth']
    },
    reset_get_user_settings=None,
    users_route_settings={
        'prefix': '/users',
        'tags': ['users']
    },
    users_get_user_settings=None,
    *args, **kwargs):
    """
    Parameters
    ----------
    api_objects : dict or None
        Dictionary returned from :func:`msdss_users_api.tools.create_api_objects`.
        If ``None``, one will be created from ``api_objects_settings``.
    api_objects_settings : dict
        Keyword arguments passed to :func:`msdss_users_api.tools.create_api_objects`
    enable_jwt_route : bool
        Whether to use JWT auth or not.
    enable_jwt_refresh_route : bool
        Whether to include a jwt refresh route or not.
    enable_cookie_route : bool
        Whether to use cookie auth or not.
    enable_register_route : bool
        Whether to include the Fast API Users register route.
    enable_verify_route : bool
        Whether to include the Fast API Users verify route.
    enable_reset_route : bool
        Whether to include the Fast API Users reset password route.
    enable_users_route : bool
        Whether to include the Fast API Users users route.
    jwt_settings : dict
        Keyword arguments passed to :meth:`fastapi:fastapi.FastAPI.include_router` for this router.
    cookie_settings : dict
        Keyword arguments passed to :meth:`fastapi:fastapi.FastAPI.include_router` for this router.
    register_settings : dict
        Keyword arguments passed to :meth:`fastapi:fastapi.FastAPI.include_router` for this router.
    register_get_user_settings : dict or None
        Additional arguments passed to :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` for this route.
        If ``None``, a dependency will not be added. The default is to only allow superusers to access this route.
    verify_settings : dict
        Keyword arguments passed to :meth:`fastapi:fastapi.FastAPI.include_router` for this router.
    verify_get_user_settings : dict or None
        Additional arguments passed to :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` for this route.
        If ``None``, a dependency will not be added.
    reset_settings : dict
        Keyword arguments passed to :meth:`fastapi:fastapi.FastAPI.include_router` for this router.
    reset_get_user_settings : dict or None
        Additional arguments passed to :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` for this route.
        If ``None``, a dependency will not be added.
    users_settings : dict
        Keyword arguments passed to :meth:`fastapi:fastapi.FastAPI.include_router` for this router.
    users_get_user_settings : dict or None
        Additional arguments passed to :meth:`msdss_users_api.msdss_users_api.core.UsersAPI.get_current_user` for this route.
        If ``None``, a dependency will not be added.
    *args, **kwargs
        Additional arguments passed to :class:`fastapi:fastapi.routing.APIRouter`.
    
    Returns
    -------
    :class:`fastapi:fastapi.routing.APIRouter`
            A router object used for organizing larger applications and for modularity. See `FastAPI bigger apps <https://fastapi.tiangolo.com/tutorial/bigger-applications/>`_

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_base_api import API
        from msdss_users_api.tools import create_api_objects
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
        api_objects = create_api_objects(
            user_manager_settings=user_manager_settings,
            jwt_settings=jwt_settings,
            cookie_settings=cookie_settings
        )

        # Add the users router
        router = get_users_router(api_objects)
        app.add_router(router)

        # Setup startup and shutdown
        async_database = api_objects['databases']['async_database']

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
    api_objects = api_objects if api_objects else create_api_objects(**api_objects_settings)
    users_api = api_objects['users_api']
    jwt = api_objects['auth']['jwt']
    cookie = api_objects['auth']['cookie']
    UserManager = api_objects['models']['UserManager']

    # (get_users_router_depends) Add current user dependencies if not set
    mappings = {
        'register_get_user': register_get_user_settings,
        'verify_get_user:': verify_get_user_settings,
        'reset_get_user': reset_get_user_settings,
        'users_get_user': users_get_user_settings
    }
    mappings = {k:users_api.current_user(**v) for k, v in mappings.items() if v}
    register_get_user = mappings.get('register_get_user', None)
    verify_get_user = mappings.get('verify_get_user', None)
    reset_get_user = mappings.get('reset_get_user', None)
    users_get_user = mappings.get('users_get_user', None)

    # (get_users_route_jwt) Add jwt auth route
    if enable_jwt_route:

        # (get_users_route_jwt_create) Create jwt route
        jwt_router = users_api.get_auth_router(jwt)
        
        # (get_users_route_jwt_refresh) Create jwt refresh route
        if enable_jwt_refresh_route:
            @jwt_router.post('/refresh')
            async def refresh_jwt(response: Response, user=Depends(users_api.current_user(active=True))):
                return await jwt.get_login_response(user, response, UserManager)

        # (get_users_route_jwt_include) Include jwt route
        out.include_router(jwt_router, **jwt_route_settings)

    # (get_users_route_auth_cookie) Add cookie auth route
    if enable_cookie_route:
        auth_cookie_router = users_api.get_auth_router(cookie)
        out.include_router(auth_cookie_router, **cookie_route_settings)

    # (get_users_route_register) Add register router
    if enable_register_route:
        if register_get_user:
            register_route_settings['dependencies'] = register_route_settings.get('dependencies', [])
            register_route_settings['dependencies'].append(Depends(register_get_user))
        register_router = users_api.get_register_router()
        out.include_router(register_router, **register_route_settings)

    # (get_users_route_verify) Add verify router
    if enable_verify_route:
        if verify_get_user:
            verify_route_settings['dependencies'] = verify_route_settings.get('dependencies', [])
            verify_route_settings['dependencies'].append(Depends(verify_get_user))
        verify_router = users_api.get_verify_router()
        out.include_router(verify_router, **verify_route_settings)
    
    # (get_users_route_reset) Add reset password router
    if enable_reset_route:
        if reset_get_user:
            reset_route_settings['dependencies'] = reset_route_settings.get('dependencies', [])
            reset_route_settings['dependencies'].append(Depends(reset_get_user))
        reset_router = users_api.get_reset_password_router()
        out.include_router(reset_router, **reset_route_settings)

    # (get_users_route_users) Add users router
    if enable_users_route:
        if users_get_user:
            users_route_settings['dependencies'] = users_route_settings.get('dependencies', [])
            users_route_settings['dependencies'].append(Depends(users_get_user))
        users_router = users_api.get_users_router()
        out.include_router(users_router, **users_route_settings)

    return out
