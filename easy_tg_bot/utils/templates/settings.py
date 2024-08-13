from easy_tg_bot import get_secret_by_name, settings

# Convention
# ! easy_tg_bot run --upd-env clears the env variables that start with "TG_"

# Telegram IDs of (super)admins
# https://t.me/getmyid_bot
TG_MY_ID = str(get_secret_by_name("TG_MY_ID"))

# Default roles
ROLES = {
    TG_MY_ID: "superadmin"
}

settings.DEFAULT_ROLES.update(ROLES)
