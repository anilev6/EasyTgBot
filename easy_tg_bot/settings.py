import os
from dotenv import load_dotenv

from .utils.init_templates import initialize_file_from_draft


# Get sectret
def get_secret_by_name(name: str, default=None):
    result = os.getenv(name)
    if not result and default is None: 
        if not os.path.exists(os.path.join(os.getcwd(), ".env")):
            initialize_file_from_draft(".env", os.getcwd())
            raise Exception("No .env file found in the current working directory. Please fill .env file.")
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"), override=True)
    return result or default

# TG creds
TG_BOT_NAME = get_secret_by_name("TG_BOT_NAME")
TG_BOT_TOKEN = get_secret_by_name("TG_BOT_TOKEN")

# Tg IDs
TG_MY_ID = str(get_secret_by_name("TG_MY_ID"))

# Optional
TG_TIME_ZONE = get_secret_by_name("TG_TIME_ZONE", "")
TG_WEBHOOK_URL = get_secret_by_name("TG_WEBHOOK_URL", "")
TG_FILE_FOLDER_PATH = get_secret_by_name("TG_FILE_FOLDER_PATH", "")

DEFAULT_ROLES = {TG_MY_ID: "superadmin"}

def get_default_role(user_id):
    return DEFAULT_ROLES.get(str(user_id), "user")
