import os

from fastapi_users import BaseUserManager
from functools import partial
from msdss_base_dotenv import env_exists, load_env_file

from .models import UserCreate, UserDB

class Environment:
    """
    Environment

    Example
    -------
    .. jupyter-execute::

        from msdss_users_api.models import *
        from pprint import pprint

        pprint(dir(UserManager))
    """
    def __init__(
        self,
        env_file='./.env',
        key_path=None,
        **kwargs):

        # (EnvironnmentManager_kwargs) Set attrs and meths for key value args
        for k, v in kwargs.items():
            setattr(self, k, v)
            get_method = partial(lambda default=None: os.getenv(getattr(self, k), default))
            setattr(self, 'get_' + k, get_method)
        
        # (EnvironmentManager_attrs) Set standard attrs
        self.env_file = env_file
        self.key_path = key_path

    def load(self):
        if env_exists(file_path=self.env_file, key_path=self.key_path):
            load_env_file(file_path=self.env_file, key_path=self.key_path)

class UserManager(BaseUserManager[UserCreate, UserDB]):
    """
    See `UserManager model <https://fastapi-users.github.io/fastapi-users/configuration/user-manager/>`_ from ``fastapi-users``.

    Example
    -------
    .. jupyter-execute::

        from msdss_users_api.models import *
        from pprint import pprint

        pprint(dir(UserManager))
    """
    user_db_model = UserDB