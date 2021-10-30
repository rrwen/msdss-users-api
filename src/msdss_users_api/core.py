from fastapi_users import FastAPIUsers
from msdss_base_api import API

from .auth import *
from .models import *
from .users import *

class UsersAPI(API):

    def __init__(
        self,
        reset_password_token_secret,
        verification_token_secret,
        cookie_secret=None,
        jwt_secret=None,
        User=User,
        UserCreate=UserCreate,
        UserUpdate=UserUpdate,
        UserDB=UserDB,
        get_user_manager=None,
        cookie_auth=None,
        jwt_auth=None):

        super().__init__()

        jwt_auth = get_jwt_auth(secret=jwt_secret) if jwt_secret and jwt_auth is None else jwt_auth
        cookie_auth = get_cookie_auth(secret=cookie_secret) if cookie_secret and cookie_auth is None else cookie_auth
        auth = [a for a in [cookie_auth, jwt_auth] if a is not None]

        get_user_manager = create_user_manager_func(reset_password_token_secret=reset_password_token_secret, verification_token_secret=verification_token_secret) if get_user_manager is None else get_user_manager

        self.users_api = FastAPIUsers(
            get_user_manager,
            auth,
            User,
            UserCreate,
            UserUpdate,
            UserDB,
        )