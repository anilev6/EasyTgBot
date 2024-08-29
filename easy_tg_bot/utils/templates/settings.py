from easy_tg_bot import get_secret, default_roles


# Telegram IDs of (super)admins
# https://t.me/getmyid_bot
MY_ID = get_secret("MY_ID")

# Default roles
# Possible keys: stuff in you .env or env variable with the name 
# Possible values: superadmin, admin, user, banned
ROLES = {
    "MY_ID": "superadmin"
}

# Add default roles 
default_roles(ROLES)
