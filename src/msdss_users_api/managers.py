from fastapi_users import BaseUserManager

from .models import UserCreate, UserDB

class UserManager(BaseUserManager[UserCreate, UserDB]):
    """
    See `UserManager model <https://fastapi-users.github.io/fastapi-users/configuration/user-manager/>`_ from ``fastapi-users``.

    Example
    -------
    .. jupyter-execute::

        from msdss_users_api.managers import *
        from pprint import pprint

        pprint(dir(UserManager))
    """
    user_db_model = UserDB