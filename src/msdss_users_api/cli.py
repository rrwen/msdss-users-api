import argparse
import asyncio
import contextlib

from fastapi_users.manager import UserAlreadyExists

from .core import UsersAPI
from .models import UserCreate

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

        from msdss_base_dotenv.cli import _get_parser

        parser = _get_parser()
        parser.print_help()

    """

    # (_get_parser_parsers) Create main parser and sub parsers
    parser = argparse.ArgumentParser(description='Manages users with a database')
    subparsers = parser.add_subparsers(title='commands', dest='command')
    
    # (_get_parser_register) Add register command
    register_parser = subparsers.add_parser('register', help='register a user')
    register_parser.add_argument('email', type=str, help='email for user')
    register_parser.add_argument('password', type=str, help='password for user')
    register_parser.add_argument('superuser', type=str, default=False, help='whether user is a superuser or not')

    # (_get_parser_get) Add get command
    get_parser = subparsers.add_parser('get', help='get user attributes')
    get_parser.add_argument('email', type=str, help='email for user')

    # (_get_parser_delete) Add delete command
    delete_parser = subparsers.add_parser('delete', help='delete a user')
    delete_parser.add_argument('email', type=str, help='email of user to delete')

    # (_get_parser_update) Add update command
    update_parser = subparsers.add_parser('update', help='update a user\'s attribute')
    update_parser.add_argument('email', type=str, help='email of user')
    update_parser.add_argument('attribute', type=str, help='attribute of user')
    update_parser.add_argument('value', type=str, help='value to update attribute with')

    # (_get_parser_file_key) Add file and key arguments to all commands
    for p in [parser, register_parser, delete_parser, update_parser, get_parser]:
        p.add_argument('--file_path', type=str, default='./.env', help='path of .env file')
        p.add_argument('--key_path', type=str, default=None, help='path of key file')
    
    # (_get_parser_out) Return the parser
    out = parser
    return out


async def create_user(email, password, superuser=False, users_api_kwargs={}, *args, **kwargs):
    
    # (create_user_func) Get db and manager funcs
    app = UsersAPI(**users_api_kwargs)
    get_user_db = app._users_functions['get_user_db']
    get_user_manager = app._users_functions['get_user_manager']

    # (create_user_context) Get db and manager context functions
    get_user_db_context = contextlib.asynccontextmanager(get_user_db)
    get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

    # (create_user_run) Run create user function
    try:
        async with get_user_db_context() as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                user = await user_manager.create(
                    UserCreate(
                        email=email,
                        password=password,
                        is_superuser=superuser,
                        *args, **kwargs
                    )
                )
                print(f"User created {user}")
    except UserAlreadyExists:
        print(f"User {email} already exists")

def run():

    # (run_kwargs) Get arguments and command
    parser = _get_parser()
    kwargs = vars(parser.parse_args())
    command = kwargs.pop('command')

    # (run_command) Run commands
    if command == 'register':
        create_user(**kwargs)