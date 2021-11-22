Quick Start
===========

Setup Secrets
-------------

After installing the package, set up environment variables using ``msdss-dotenv`` in a command line terminal:

.. code::
   
   msdss-dotenv init
   msdss-dotenv set MSDSS_USERS_SECRET secret-phrase
   msdss-dotenv set MSDSS_USERS_RESET_PASSWORD_TOKEN_SECRET secret-phrase-02
   msdss-dotenv set MSDSS_USERS_VERIFICATION_TOKEN_SECRET secret-phrase-03

.. note::

    You can generate a strong secret phrases with:
    
    .. code::

        openssl rand -hex 32

.. warning::

    Copy and save these secret phrases as they will be needed to authenticate your users.

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

.. note::

    You can get help for the command line with:
    
    .. code::

        msdss-users --help
