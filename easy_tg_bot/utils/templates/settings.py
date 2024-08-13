from easy_tg_bot import get_secret_by_name, default_roles

# Convention
# ! easy_tg_bot run --upd-env clears the env variables that start with "TG_"

# Telegram IDs of (super)admins
# https://t.me/getmyid_bot
TG_MY_ID = str(get_secret_by_name("TG_MY_ID"))

# Default roles
# Possible keys: stuff in you .env or env variable with the name 
# Possible values: superadmin, admin, user, banned
ROLES = {
    "TG_MY_ID": "superadmin"
}

# Add default roles 
default_roles(ROLES)
