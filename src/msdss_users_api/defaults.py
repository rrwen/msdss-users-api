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