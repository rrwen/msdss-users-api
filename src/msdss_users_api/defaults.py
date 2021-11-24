DEFAULT_DATABASE_KWARGS = dict(
    load_env=True,
    env_file='./.env',
    key_path=None,
    driver_key='MSDSS_DATABASE_DRIVER',
    user_key='MSDSS_DATABASE_USER',
    password_key='MSDSS_DATABASE_PASSWORD',
    host_key='MSDSS_DATABASE_HOST',
    port_key='MSDSS_DATABASE_PORT',
    database_key='MSDSS_DATABASE_NAME'
)
DEFAULT_ENV_KWARGS = dict(
    env_file='./.env',
    key_path=None,
    secret='MSDSS_USERS_SECRET',
    jwt_secret='MSDSS_USERS_JWT_SECRET',
    cookie_secret='MSDSS_USERS_COOKIE_SECRET',
    reset_password_token_secret='MSDSS_USERS_RESET_PASSWORD_TOKEN_SECRET',
    verification_token_secret='MSDSS_USERS_VERIFICATION_TOKEN_SECRET'
)