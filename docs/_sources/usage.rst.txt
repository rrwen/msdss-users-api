Usage
=====

Command Line Interface (CLI)
----------------------------

Start an API server (go to http://localhost:8000/docs to try the API):

>>> msdss-users start

Register a user:

>>> msdss-users register

Get user info:

>>> msdss-users get <email>

Update a user's attributes:

>>> msdss-users update <email> --is_superuser True

Reset password for a user:

>>> msdss-users reset <email>

Delete a user:

>>> msdss-users delete <email>

.. warning::

    Do not forget to setup your environmental variables (see :ref:`quick-start`)

.. note::

    For more information, you can get help for each command:

    >>> msdss-users --help
    >>> msdss-users start --help
    >>> msdss-users register --help
    >>> msdss-users get --help
    >>> msdss-users update --help
    >>> msdss-users reset --help
    >>> msdss-users delete --help

Python
------

In Python, use the package via :class:`msdss_users_api.core.UsersAPI`:

.. jupyter-execute::
    :hide-output:

    from fastapi import Depends
    from msdss_users_api import UsersAPI
    from msdss_users_api.models import User

    # Create app using env vars
    app = UsersAPI()

    # Get a function dependency for the current active user
    current_active_user = app.get_current_user(active=True)

    # Add a protected route
    @app.route('GET', '/protected-route')
    def protected_route(user: User = Depends(current_active_user)):
        return f'Hello, {user.email}'

    # Run the app with app.start()
    # API is hosted at http://localhost:8000
    # Try API at http://localhost:8000/docs
    # app.start()

.. warning::

    Do not forget to setup your environmental variables (see :ref:`quick-start`)

.. note::

    You can also manage users programmatically with the following functions:

    * :func:`msdss_users_api.tools.register_user`
    * :func:`msdss_users_api.tools.get_user`
    * :func:`msdss_users_api.tools.update_user`
    * :func:`msdss_users_api.tools.reset_user_password`
    * :func:`msdss_users_api.tools.delete_user`
    