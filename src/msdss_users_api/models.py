import fastapi_users
import fastapi_users.models
import fastapi_users.db

from typing import List

class User(fastapi_users.models.BaseUser):
    pass

class UserCreate(fastapi_users.models.BaseUserCreate):
    pass

class UserUpdate(fastapi_users.models.BaseUserUpdate):
    pass

class UserDB(User, fastapi_users.models.BaseUserDB):
    pass

class UserManager(fastapi_users.BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = 'msdss-secret'
    verification_token_secret = 'msdss-secret'