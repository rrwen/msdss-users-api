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
    parser = argparse.ArgumentParser(description='Manages encrypted .env files')
    subparsers = parser.add_subparsers(title='commands', dest='command')

    # (_get_parser_init) Add init command
    init_parser = subparsers.add_parser('init', help='create env file and key')
    
    # (_get_parser_set) Add set command
    set_parser = subparsers.add_parser('set', help='set an env var')
    set_parser.add_argument('name', type=str, help='env var name to set')
    set_parser.add_argument('value', type=str, help='env var value to set')

    # (_get_parser_del) Add del command
    del_parser = subparsers.add_parser('del', help='delete an env var')
    del_parser.add_argument('name', type=str, help='env var name to delete')

    # (_get_parser_clear) Add clear command
    clear_parser = subparsers.add_parser('clear', help='clear env file and key')

    # (_get_parser_file_key) Add file and key arguments to all commands
    for p in [parser, init_parser, set_parser, del_parser, clear_parser]:
        p.add_argument('--file_path', type=str, default='./.env', help='path of .env file')
        p.add_argument('--key_path', type=str, default=None, help='path of key file')
    
    # (_get_parser_out) Return the parser
    out = parser
    return out


async def create_user(email, password, is_superuser=False, users_api_kwargs={}, *args, **kwargs):
    
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
                        is_superuser=is_superuser,
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