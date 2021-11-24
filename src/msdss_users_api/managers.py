import os

from fastapi_users import BaseUserManager
from functools import partial
from msdss_base_dotenv import env_exists, load_env_file

from .models import UserCreate, UserDB

class Environment:
    """
    Class to manage environmental variables.

    Parameters
    ----------
    env_file : str
        The path of the file with environmental variables.
    key_path : str
        The path of the key file for the ``env_file``.
    **kwargs
        Keyword arguments defining the environmental attributes and variable names for this object.

        * Each key represents the attribute name, and each value represents the environmental variable name
        * For example, passing ``secret='MSDSS_SECRET'`` sets an attribute ``secret`` and a method ``get_secret``, which gets the environmental variable from the ``env_file``
        * The method can also accept a single default value, if the variable does not exist in the ``env_file``

    Example
    -------
    .. jupyter-execute::

        from msdss_base_dotenv import Environment

        env = Environment(secret='MSDSS_SECRET')
        secret = env.get_secret('default')
        print(secret)
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
            set_method = partial(lambda value: set_env_var(getattr(self, v), value))
            del_method = partial(lambda value: del_env_var(getattr(self, v)))
            setattr(self, 'get_' + k, get_method)
            setattr(self, 'set_' + k, set_method)
            setattr(self, 'del_' + k, del_method)
        
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