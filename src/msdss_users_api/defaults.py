DEFAULT_DOTENV_KWARGS = dict(
    env_file='./.env',
    key_path=None,
    cookie_secret='MSDSS_USERS_COOKIE_SECRET',
    jwt_secret='MSDSS_USERS_JWT_SECRET',
    reset_password_token_secret='MSDSS_USERS_RESET_PASSWORD_TOKEN_SECRET',
    verification_token_secret='MSDSS_USERS_VERIFICATION_TOKEN_SECRET'
)

DEFAULT_COOKIE_SETTINGS = dict(
    lifetime_seconds=30 * 86400 # 30 days
)

DEFAULT_JWT_SETTINGS = dict(
    lifetime_seconds=15 * 60, # 15 minutes
    tokenUrl='auth/jwt/login'
)

DEFAULT_USERS_ROUTE_SETTINGS = dict(
    cookie=dict(
        prefix='/auth',
        tags=['auth'],
        _enable=True,
        _get_user=None
    ),
    jwt=dict(
        prefix='/auth/jwt',
        tags=['auth'],
        _enable=True,
        _get_user=None,
        _enable_refresh=True
    ),
    register=dict(
        prefix='/auth',
        tags=['auth'],
        _enable=True,
        _get_user={'superuser': True}
    ),
    verify=dict(
        prefix='/auth',
        tags=['auth'],
        _enable=True,
        _get_user=None
    ),
    reset=dict(
        prefix='/auth',
        tags=['auth'],
        _enable=True,
        _get_user=None
    ),
    users=dict(
        prefix='/users',
        tags=['users'],
        _enable=True,
        _get_user=None
    )
)