from fastapi_users.authentication import CookieAuthentication, JWTAuthentication

def get_jwt_auth(secret, name='jwt', lifetime_seconds=3600, tokenUrl='auth/jwt/login', *args, **kwargs):
    out = JWTAuthentication(secret=secret, lifetime_seconds=lifetime_seconds, tokenUrl=tokenUrl, name=name, *args, **kwargs)
    return out

def get_cookie_auth(secret, lifetime_seconds=3600, *args, **kwargs):
    out = CookieAuthentication(secret=secret, lifetime_seconds=lifetime_seconds, *args, **kwargs)
    return out