import argparse
import asyncio
import inspect

from getpass import getpass

from .core import *
from .tools import *

def _get_parser():
    """
    Builds an ``argparse`` parser for the ``msdss-users`` command line tool.

    Returns
    -------
    :class:`argparse.ArgumentParser`
        An ``argparse`` parser for ``msdss-users``.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    .. jupyter-execute::
        :hide-output:

        from msdss_users_api.cli import _get_parser

        parser = _get_parser()
        parser.print_help()
    """

    # (_get_parser_parsers) Create main parser and sub parsers
    parser = argparse.ArgumentParser(description='Manages users with a database')
    subparsers = parser.add_subparsers(title='commands', dest='command')
    
    # (_get_parser_register) Add register command
    register_parser = subparsers.add_parser('register', help='register a user')
    register_parser.add_argument('email', type=str, nargs='?', help='email for user')
    register_parser.add_argument('password', type=str, nargs='?', help='password for user')
    register_parser.add_argument('--superuser', dest='superuser', action='store_true', help='register a superuser')
    register_parser.set_defaults(superuser=False)

    # (_get_parser_get) Add get command
    get_parser = subparsers.add_parser('get', help='get user attributes')
    get_parser.add_argument('email', type=str, help='email for user')

    # (_get_parser_delete) Add delete command
    delete_parser = subparsers.add_parser('delete', help='delete a user')
    delete_parser.add_argument('email', type=str, help='email of user to delete')

    # (_get_parser_reset) Add reset command
    reset_parser = subparsers.add_parser('reset', help='reset user password')
    reset_parser.add_argument('email', type=str, help='email of user to reset')
    reset_parser.add_argument('password', type=str, nargs='?', help='new password to use')

    # (_get_parser_update) Add update command
    update_parser = subparsers.add_parser('update', help='update a user\'s attribute')
    update_parser.add_argument('email', type=str, help='email of user')
    update_parser.add_argument('--is_active', type=bool, default=None, help='set is_active attribute')
    update_parser.add_argument('--is_superuser', type=bool, default=None, help='set is_superuser attribute')
    update_parser.add_argument('--is_verified', type=bool, default=None, help='set is_verified attribute')

    # (_get_parser_start) Add start command
    start_parser = subparsers.add_parser('start', help='start a users api server')
    start_parser.add_argument('--host', type=str, default='127.0.0.1', help='address to host server')
    start_parser.add_argument('--port', type=int, default=8000, help='port to host server')
    start_parser.add_argument('--log_level', type=str, default='info', help='level of verbose messages to display')
    start_parser.add_argument('--auth_prefix', type=str, default='/auth', help='path prefix for auth routes')
    start_parser.add_argument('--users_prefix', type=str, default='/users', help='path prefix for users routes')
    start_parser.add_argument('--auth_lifetime', type=int, default=3600, help='token/cookie lifetime before expiry in secs')
    start_parser.add_argument('--disable_register_superuser', dest='register_router_superuser', action='store_false', help='disable superuser requirement for register route')
    start_parser.add_argument('--disable_auth_router', dest='enable_auth_router', action='store_false', help='disable auth router')
    start_parser.add_argument('--disable_register_router', dest='enable_register_router', action='store_false', help='disable register router')
    start_parser.add_argument('--disable_verify_router', dest='enable_verify_router', action='store_false', help='disable verify router')
    start_parser.add_argument('--disable_reset_password_router', dest='enable_reset_password_router', action='store_false', help='disable reset password router')
    start_parser.add_argument('--disable_users_router', dest='enable_users_router', action='store_false', help='disable users router')
    start_parser.add_argument('--disable_jwt_auth', dest='enable_jwt_auth', action='store_false', help='disable jwt authentication')
    start_parser.add_argument('--disable_cookie_auth', dest='enable_cookie_auth', action='store_false', help='disable cookie authentication')
    start_parser.add_argument('--secret_key', type=str, default='MSDSS_USERS_SECRET', help='env var name for secret phrase')
    start_parser.add_argument('--jwt_secret_key', type=str, default='MSDSS_USERS_JWT_SECRET', help='env var name for jwt secret')
    start_parser.add_argument('--cookie_secret_key', type=str, default='MSDSS_USERS_COOKIE_SECRET', help='env var name for cookie secret')
    start_parser.add_argument('--reset_password_token_secret_key', type=str, default='MSDSS_USERS_RESET_PASSWORD_TOKEN_SECRET', help='env var name for reset password secret')
    start_parser.add_argument('--verification_token_secret_key', type=str, default='MSDSS_USERS_VERIFICATION_TOKEN_SECRET', help='env var name for verify token secret')
    start_parser.add_argument('--driver_key', type=str, default='MSDSS_DATABASE_DRIVER', help='env var name for db driver')
    start_parser.add_argument('--user_key', type=str, default='MSDSS_DATABASE_USER', help='env var name for db user')
    start_parser.add_argument('--password_key', type=str, default='MSDSS_DATABASE_PASSWORD', help='env var name for db user password')
    start_parser.add_argument('--host_key', type=str, default='MSDSS_DATABASE_HOST', help='env var name for db host')
    start_parser.add_argument('--port_key', type=str, default='MSDSS_DATABASE_PORT', help='env var name for db port')
    start_parser.add_argument('--database_key', type=str, default='MSDSS_DATABASE_NAME', help='env var name for db name')
    start_parser.set_defaults(
        register_router_superuser=True,
        enable_auth_router=True,
        enable_register_router=True,
        enable_verify_router=True,
        enable_reset_password_router=True,
        enable_users_router=True,
        enable_jwt_auth=True,
        enable_cookie_auth=True
    )

    # (_get_parser_file_key) Add file and key arguments to all commands
    for p in [parser, register_parser, delete_parser, update_parser, get_parser, reset_parser, start_parser]:
        p.add_argument('--env_file', type=str, default='./.env', help='path of .env file')
        p.add_argument('--key_path', type=str, default=None, help='path of key file')
    
    # (_get_parser_out) Return the parser
    out = parser
    return out

def _prompt_password():
    """
    Prompts the user for a password.

    Returns
    -------
    str
        Password provided by user input.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    .. code:: python

        from msdss_users_api.cli import _prompt_password
        _prompt_password()
    """
    password = getpass()
    verify = getpass('Verify password: ')
    if not password == verify:
        raise ValueError('Passwords do not match')
    return password

def run():
    """
    Runs the ``msdss-users`` command.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    >>> msdss-users --help

    .. jupyter-execute::
        :hide-code:

        from msdss_users_api.cli import _get_parser

        parser = _get_parser()
        parser.print_help()

    Create a user interactively:

    >>> msdss-users register

    Get user attributes:

    >>> msdss-users get test@example.com

    Update user attributes:

    >>> msdss-users update test@example.com --is_verified True

    Reset user password:

    >>> msdss-users reset test@example.com

    Delete a user:

    >>> msdss-users delete test@example.com

    Start an API server:

    >>> msdss-users start
    """

    # (run_kwargs) Get arguments and command
    parser = _get_parser()
    kwargs = vars(parser.parse_args())
    command = kwargs.pop('command')

    # (run_env) Get env files and paths
    env_kwargs = dict(
        env_file=kwargs.pop('env_file'),
        key_path=kwargs.pop('key_path')
    )

    # (run_command) Run commands
    if command == 'register':

        # (run_command_register) Execute user register
        kwargs['email'] = kwargs['email'] if kwargs['email'] else input('Email: ')
        kwargs['password'] = kwargs['password'] if kwargs['password'] else _prompt_password()
        asyncio.run(register_user(
            create_user_db_context_kwargs=env_kwargs,
            create_user_manager_context_kwargs=env_kwargs,
            **kwargs
        ))

    elif command == 'get':

        # (run_command_get) Execute user get
        asyncio.run(get_user(
            show=True,
            create_user_db_context_kwargs=env_kwargs,
            create_user_manager_context_kwargs=env_kwargs,
            **kwargs
        ))

    elif command == 'delete':

        # (run_command_delete) Execute user delete
        asyncio.run(delete_user(
            create_user_db_context_kwargs=env_kwargs,
            create_user_manager_context_kwargs=env_kwargs,
            **kwargs
        ))

    elif command == 'reset':

        # (run_command_reset) Reset password for user
        kwargs['password'] = kwargs['password'] if kwargs['password'] else _prompt_password()
        asyncio.run(reset_user_password(
            create_user_db_context_kwargs=env_kwargs,
            create_user_manager_context_kwargs=env_kwargs,
            **kwargs
        ))

    elif command == 'update':

        # (run_command_update) Execute user update
        kwargs = {k:v for k, v in kwargs.items() if v}
        asyncio.run(update_user(
            create_user_db_context_kwargs=env_kwargs,
            create_user_manager_context_kwargs=env_kwargs,
            **kwargs
        ))

    elif command == 'start':

        # (run_command_start_env) Merge env args into standard args
        kwargs.update(env_kwargs)
        
        # (run_command_start_route) Extract route args
        auth_prefix = kwargs.pop('auth_prefix')
        users_prefix = kwargs.pop('users_prefix')
        auth_lifetime = kwargs.pop('auth_lifetime')

        # (run_command_start_serve) Extract server args
        app_kwargs = dict(
            host=kwargs.pop('host'),
            port=kwargs.pop('port'),
            log_level=kwargs.pop('log_level')
        )

        # (run_command_start_defaults) Get default parameters
        defaults = inspect.signature(UsersAPI).parameters
        for k, v in defaults.items():
            is_not_empty = v.default is not inspect.Parameter.empty 
            if k not in kwargs and is_not_empty:
                kwargs[k] = defaults[k].default

        # (run_command_start_route_merge) Merge route args to standard args
        kwargs['auth_router_jwt_include_kwargs']['prefix'] = auth_prefix + '/jwt'
        kwargs['auth_router_cookie_include_kwargs']['prefix'] = auth_prefix
        kwargs['register_router_include_kwargs']['prefix'] = auth_prefix
        kwargs['verify_router_include_kwargs']['prefix'] = auth_prefix
        kwargs['reset_password_router_include_kwargs']['prefix'] = auth_prefix
        kwargs['users_router_include_kwargs']['prefix'] = users_prefix
        kwargs['cookie_kwargs']['lifetime_seconds'] = auth_lifetime
        kwargs['jwt_kwargs'].update(dict(
            lifetime_seconds=auth_lifetime,
            tokenUrl=auth_prefix[1:] + '/jwt/login'
        ))

        # (run_command_start) Execute users api server
        app = UsersAPI(**kwargs)
        app.start(**app_kwargs)