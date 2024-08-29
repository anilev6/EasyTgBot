import os

from .utils.init_templates import initialize_file_from_draft


# Get sectret
def read_env(file: bool):
    """Load environment variables from a .env file or from the system."""
    if file:
        env_vars = {}
        path = os.path.join(os.getcwd(), ".env")
        with open(path, "r") as file:
            for line in file:
                if line.strip() and not line.startswith("#"):
                    k, v = line.strip().split("=")
                    env_vars[k] = v
        return env_vars
    return dict(os.environ)


def get_secret_by_name(name: str, default = None, env_file = False) -> str:
    """Leave default = None to raise an error if the variable is not found."""
    if env_file:
        if not os.path.exists(os.path.join(os.getcwd(), ".env")):
            initialize_file_from_draft(".env", os.getcwd())
            raise Exception(
                "No .env file found in the current working directory. Please fill .env file."
            )
    vars = read_env(env_file)
    result = vars.get(name, default)
    if result is None:
        raise ValueError(f"Error initializing env variable: {name}")
    return result


def get_secret(name: str, default=None):
    """Leave default = None to raise an error if the variable is not found."""
    try:
        result = get_secret_by_name(name, default, env_file = False)
    except ValueError:
        result = get_secret_by_name(name, default, env_file = True)
    return result


# TG creds
BOT_NAME = get_secret("BOT_NAME")
BOT_TOKEN = get_secret("BOT_TOKEN")

# Optional
# File storage/mount
TIME_ZONE = get_secret("TIME_ZONE", "")

# Roles
DEFAULT_ROLES_DICT = {}

# Possible values: superadmin, admin, user, banned
def default_roles(roles):
    DEFAULT_ROLES_DICT.update({str(get_secret(k)): v for k, v in roles.items()})

def get_default_role(user_id):
    return DEFAULT_ROLES_DICT.get(str(user_id), "user")
