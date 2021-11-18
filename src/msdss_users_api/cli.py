import argparse
import asyncio

from getpass import getpass

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

    # (_get_parser_file_key) Add file and key arguments to all commands
    for p in [parser, register_parser, delete_parser, update_parser, get_parser, reset_parser]:
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
        kwargs['email'] = kwargs['email'] if kwargs['email'] else input('Email: ')
        kwargs['password'] = kwargs['password'] if kwargs['password'] else _prompt_password()
        asyncio.run(register_user(
            create_user_db_context_kwargs=env_kwargs,
            create_user_manager_context_kwargs=env_kwargs,
            **kwargs
        ))
    elif command == 'get':
        asyncio.run(get_user(
            show=True,
            create_user_db_context_kwargs=env_kwargs,
            create_user_manager_context_kwargs=env_kwargs,
            **kwargs
        ))
    elif command == 'delete':
        asyncio.run(delete_user(
            create_user_db_context_kwargs=env_kwargs,
            create_user_manager_context_kwargs=env_kwargs,
            **kwargs
        ))
    elif command == 'reset':
        kwargs['password'] = kwargs['password'] if kwargs['password'] else _prompt_password()
        asyncio.run(reset_user_password(
            create_user_db_context_kwargs=env_kwargs,
            create_user_manager_context_kwargs=env_kwargs,
            **kwargs
        ))
    elif command == 'update':
        kwargs = {k:v for k, v in kwargs.items() if v}
        asyncio.run(update_user(
            create_user_db_context_kwargs=env_kwargs,
            create_user_manager_context_kwargs=env_kwargs,
            **kwargs
        ))