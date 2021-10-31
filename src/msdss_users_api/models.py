import fastapi_users
import fastapi_users.models
import fastapi_users.db

from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

class User(fastapi_users.models.BaseUser):
    """
    See `User model <https://fastapi-users.github.io/fastapi-users/configuration/models/>`_ from ``fastapi-users``.

    Example
    -------
    .. jupyter-execute::

        from msdss_users_api.models import *
        from pprint import pprint

        fields = User.__fields__
        pprint(fields)
    """
    pass

class UserCreate(fastapi_users.models.BaseUserCreate):
    """
    See `UserCreate model <https://fastapi-users.github.io/fastapi-users/configuration/models/>`_ from ``fastapi-users``.

    Example
    -------
    .. jupyter-execute::

        from msdss_users_api.models import *
        from pprint import pprint

        fields = UserCreate.__fields__
        pprint(fields)
    """
    pass

class UserUpdate(fastapi_users.models.BaseUserUpdate):
    """
    See `UserUpdate model <https://fastapi-users.github.io/fastapi-users/configuration/models/>`_ from ``fastapi-users``.

    Example
    -------
    .. jupyter-execute::

        from msdss_users_api.models import *
        from pprint import pprint

        fields = UserUpdate.__fields__
        pprint(fields)
    """
    pass

class UserDB(User, fastapi_users.models.BaseUserDB):
    """
    See `UserDB model <https://fastapi-users.github.io/fastapi-users/configuration/models/>`_ from ``fastapi-users``.

    Example
    -------
    .. jupyter-execute::

        from msdss_users_api.models import *
        from pprint import pprint

        fields = UserDB.__fields__
        pprint(fields)
    """
    pass

Base: DeclarativeMeta = declarative_base()
class UserTable(Base, fastapi_users.db.SQLAlchemyBaseUserTable):
    """
    See `UserTable model <https://fastapi-users.github.io/fastapi-users/configuration/databases/sqlalchemy/>`_ from ``fastapi-users``.

    Example
    -------
    .. jupyter-execute::

        from msdss_users_api.models import *

        table = UserTable.__table__
        columns = table.c

        for c in columns:
            print(c)
    """
    pass

class UserManager(fastapi_users.BaseUserManager[UserCreate, UserDB]):
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