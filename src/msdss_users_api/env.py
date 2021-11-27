from msdss_base_dotenv import DotEnv

from .defaults import DEFAULT_DOTENV_KWARGS

class UsersDotEnv(DotEnv):
    """
    Class to manage user environment variables.

    * Extends :class:`msdss_base_dotenv:msdss_base_dotenv.core.DotEnv`

    Parameters
    ----------
    cookie_secret : str
        The environmental variable name for ``cookie_secret``.
    jwt_secret : str
        The environmental variable name for ``jwt_secret``.
    reset_password_token_secret : str
        The environmental variable name for ``reset_password_token_secret``.
    verification_token_secret : str
        The environmental variable name for ``verification_token_secret``.
    defaults : dict
        Default values for above parameters if they are not set.
    env_file : str
        The path of the file with environmental variables.
    key_path : str
        The path of the key file for the ``env_file``.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------
    .. jupyter-execute::

        from msdss_users_api.env import UsersDotEnv
        
        # Get default env vars
        env = UsersDotEnv()
        env.save() # save to .env file
        env.load() # load the same file
        
        # Print defaults
        print('default_env:\\n')
        for k, name in env.mappings.items():
            value = str(env.get(k))
            print(f'{name}: {value}')

        # Remove saved .env file
        env.clear()

        # Create users env with diff var names for secrets
        alt_env = UsersDotEnv(
            cookie_secret='MSDSS_USERS_SECRET_B',
            reset_password_token_secret='MSDSS_USERS_RESET_PASSWORD_TOKEN_SECRET_B',
            verification_token_secret='MSDSS_USERS_VERIFICATION_TOKEN_SECRET_B'
        )

        # Set secret
        alt_env.set('cookie_secret', 'some-secret-phrase')

        # Set verification token secret and delete
        alt_env.set('verification_token_secret', 'to-be-deleted')
        alt_env.delete('verification_token_secret')

        # Check if reset password token is set
        reset_password_is_set = alt_env.is_set('reset_password_token_secret')

        # Print custom env
        # See new env
        print('\\nalt_env:\\n')
        for k, name in alt_env.mappings.items():
            value = str(alt_env.get(k))
            print(f'{name}: {value}')
        print('reset_password_is_set: ' + str(reset_password_is_set))

        # Clear alt env files
        alt_env.clear()
    """
    def __init__(
        self,
        jwt_secret=DEFAULT_DOTENV_KWARGS['jwt_secret'],
        cookie_secret=DEFAULT_DOTENV_KWARGS['cookie_secret'],
        reset_password_token_secret=DEFAULT_DOTENV_KWARGS['reset_password_token_secret'],
        verification_token_secret=DEFAULT_DOTENV_KWARGS['verification_token_secret'],
        defaults=DEFAULT_DOTENV_KWARGS.get('defaults', {}),
        env_file=DEFAULT_DOTENV_KWARGS['env_file'],
        key_path=DEFAULT_DOTENV_KWARGS['key_path']):
        kwargs = locals()
        del kwargs['self']
        del kwargs['__class__']
        super().__init__(**kwargs)