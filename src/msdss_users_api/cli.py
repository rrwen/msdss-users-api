import argparse
import ast
import asyncio

from getpass import getpass
from msdss_base_database import Database, DatabaseDotEnv

from .core import *
from .env import *
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
    start_parser.add_argument('--set', metavar=('ROUTE', 'KEY', 'VALUE'), nargs=3, action='append', help='set route settings, where ROUTE is the route name (jwt, cookie, register etc), KEY is the setting name (e.g. path, _enable, etc), and VALUE is value for the setting')
    start_parser.add_argument('--jwt_lifetime', type=int, default=15 * 60, help='expiry time in secs for JWTs')
    start_parser.add_argument('--cookie_lifetime', type=int, default=30 * 86400, help='expiry time in secs for cookies')

    # (_get_parser_file_key) Add file and key arguments to all commands
    for p in [parser, register_parser, delete_parser, update_parser, get_parser, reset_parser, start_parser]:
        p.add_argument('--env_file', type=str, default='./.env', help='path of .env file')
        p.add_argument('--key_path', type=str, default=None, help='path of key file')
    
    # (_get_parser_out) Return the parser
    out = parser
    return out

def _parse_route_settings(cli_route_settings):
    """
    Parses ``--set`` route settings for the ``msdss-users`` command line tool.
    
    Parameters
    ----------
    cli_route_settings : list(tuple)
        List of tuples of length 3, representing the route, key setting and value setting in order.
    
    Returns
    -------
    dict
        A dictionary that can be passed to parameter ``route_settings`` in :func:`msdss_users_api.routers.get_users_router`
    
    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>
    
    Example
    -------
    .. jupyter-execute::
        :hide-output:
        
        from msdss_data_api.cli import _parse_route_settings
        from pprint import pprint

        cli_route_settings = [
            ('jwt', '_enable', 'True'),
            ('jwt', '_enable_refresh', 'True'),
            ('register', '_get_user', '{"superuser": True}'),
            ('auth', 'prefix', '/auth'),
            ('users', 'tags', '["user"]')
        ]

        route_settings = _parse_route_settings(cli_route_settings)
        pprint(route_settings)
    """
    out = {route: {} for route, k, v in cli_route_settings}
    for route, key, value in cli_route_settings:
        if key in ('tags', '_restricted_tables', '_get_user', '_enable'):
            out[route][key] = ast.literal_eval(value)
        else:
            out[route][key] = value
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

    # (run_env_create) Create env objects
    users_env = UsersDotEnv(**env_kwargs)
    database = Database(env=DatabaseDotEnv(**env_kwargs))

    # (run_context) Create context args
    user_db_context_kwargs = dict(database=database)
    user_manager_context_kwargs = dict(env=users_env)

    # (run_command) Run commands
    if command == 'register':

        # (run_command_register) Execute user register
        kwargs['email'] = kwargs['email'] if kwargs['email'] else input('Email: ')
        kwargs['password'] = kwargs['password'] if kwargs['password'] else _prompt_password()
        asyncio.run(register_user(
            user_db_context_kwargs=user_db_context_kwargs,
            user_manager_context_kwargs=user_manager_context_kwargs,
            **kwargs
        ))

    elif command == 'get':

        # (run_command_get) Execute user get
        asyncio.run(get_user(
            show=True,
            user_db_context_kwargs=user_db_context_kwargs,
            user_manager_context_kwargs=user_manager_context_kwargs,
            **kwargs
        ))

    elif command == 'delete':

        # (run_command_delete) Execute user delete
        asyncio.run(delete_user(
            user_db_context_kwargs=user_db_context_kwargs,
            user_manager_context_kwargs=user_manager_context_kwargs,
            **kwargs
        ))

    elif command == 'reset':

        # (run_command_reset) Reset password for user
        kwargs['password'] = kwargs['password'] if kwargs['password'] else _prompt_password()
        asyncio.run(reset_user_password(
            user_db_context_kwargs=user_db_context_kwargs,
            user_manager_context_kwargs=user_manager_context_kwargs,
            **kwargs
        ))

    elif command == 'update':

        # (run_command_update) Execute user update
        kwargs = {k:v for k, v in kwargs.items() if v}
        asyncio.run(update_user(
            user_db_context_kwargs=user_db_context_kwargs,
            user_manager_context_kwargs=user_manager_context_kwargs,
            **kwargs
        ))

    elif command == 'start':

        # (run_command_start_env) Set env and database
        kwargs['env'] = users_env
        kwargs['database'] = database

        # (run_command_start_settings) Convert route settings
        cli_route_settings = kwargs.pop('set', None)
        kwargs['users_router_settings'] = dict(
            route_settings=_parse_route_settings(cli_route_settings) if cli_route_settings else {}
        )

        # (run_command_start_serve) Extract server args
        start_kwargs = dict(
            host=kwargs.pop('host'),
            port=kwargs.pop('port'),
            log_level=kwargs.pop('log_level')
        )

        # (run_command_start) Execute users api server
        app = UsersAPI(**kwargs)
        app.start(**start_kwargs)