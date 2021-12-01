.. _quick-start:

Quick Start
===========

Setup Secrets
-------------

After installing the package, set up environment variables using ``msdss-dotenv`` in a command line terminal:

.. code::
   
   msdss-dotenv init --key_path <KEY_PATH>
   msdss-dotenv set MSDSS_USERS_COOKIE_SECRET cookie-secret --key_path <KEY_PATH>
   msdss-dotenv set MSDSS_USERS_JWT_SECRET jwt-secret --key_path <KEY_PATH>
   msdss-dotenv set MSDSS_USERS_RESET_PASSWORD_TOKEN_SECRET reset-phrase --key_path <KEY_PATH>
   msdss-dotenv set MSDSS_USERS_VERIFICATION_TOKEN_SECRET verification-phrase --key_path <KEY_PATH>

.. note::

    Set the ``<KEY_PATH>`` to a secure location (preferable outside of the project directory) as you will need this to unlock your created ``.env`` file

.. note::

    The variables above should be a strong passphrase. You can generate strong phrases with:
    
    .. code::

        openssl rand -hex 32

.. warning::

    Copy and save these secret phrases as they will be needed to authenticate your users or recreate the environment variables if you lose the files.

Setup Database
--------------

Setup the database environment variables:

.. code::

    msdss-dotenv set MSDSS_DATABASE_DRIVER postgresql
    msdss-dotenv set MSDSS_DATABASE_USER msdss
    msdss-dotenv set MSDSS_DATABASE_PASSWORD msdss123
    msdss-dotenv set MSDSS_DATABASE_HOST localhost
    msdss-dotenv set MSDSS_DATABASE_PORT 5432
    msdss-dotenv set MSDSS_DATABASE_NAME msdss

Create Superuser
----------------

Create a ``superuser`` with the ``msdss-users`` command line interface:

.. code::

    msdss-users register --superuser

Running the API
---------------

Run a ``msdss-users-api`` server with the following command:

.. code::

    msdss-users start

Go to http://localhost:8000/docs to try out the API with your created superuser.

.. note::

    You can get help for the command line with:
    
    .. code::

        msdss-users --help
