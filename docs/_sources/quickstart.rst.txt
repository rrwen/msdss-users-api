Quick Start
===========

After installing the package, set up environment variables using ``msdss-dotenv`` in a command line terminal:

.. code::
   
   msdss-dotenv init
   msdss-dotenv set MSDSS_USERS_SECRET secret-phrase
   msdss-dotenv set MSDSS_USERS_JWT_SECRET secret-phrase-02

.. note::

    You can generate a strong ``secret-phrase`` and ``secret-phrase-02`` with: 
    
    .. code::

        openssl rand -hex 32

Then setup the database environment variables:

.. code::

    msdss-dotenv set MSDSS_DATABASE_DRIVER postgresql
    msdss-dotenv set MSDSS_DATABASE_USER msdss
    msdss-dotenv set MSDSS_DATABASE_PASSWORD msdss123
    msdss-dotenv set MSDSS_DATABASE_HOST localhost
    msdss-dotenv set MSDSS_DATABASE_PORT 5432
    msdss-dotenv set MSDSS_DATABASE_NAME msdss

Finally, create a ``superuser`` with the ``msdss-users`` command line interface:

.. code::

    msdss-users register --superuser

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
    @app.add('GET', '/protected-route')
    def protected_route(user: User = Depends(current_active_user)):
        return f'Hello, {user.email}'

    # Run the app with app.start()
    # API is hosted at http://localhost:8000
    # Try API at http://localhost:8000/docs
    # app.start()
