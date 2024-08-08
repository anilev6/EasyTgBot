from functools import wraps
from telegram.ext import ConversationHandler

from .utils.context_logic import put_user_data, get_user_data
from .utils.utils import get_user_data_essential
from .settings import get_default_role


DEFAULT_ALLOWED_ROLES = ("superadmin", "admin", "user")
DEFAULT_ADMIN_ROLES = ("superadmin", "admin")


# Basic
def add_role(context, role, user_id = None):
    put_user_data(context, "role", role, user_id)
    return get_role(context, user_id)

def get_role(context, user_id = None):
    user_data = get_user_data(context, user_id)
    return user_data.get("role")

def check_role(context, allowed_roles, user_id=None):
    role = get_role(context, user_id)
    if not role:
        return
    if role == "banned":
        return
    return role in allowed_roles

def role_required(allowed_roles = DEFAULT_ALLOWED_ROLES):
    """A role decorator for the bot handlers that take update, context.
    A user has to start with /start to get a role and thus access."""
    def decorator(func):

        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            if not check_role(context, allowed_roles):
                return ConversationHandler.END
            return await func(update, context, *args, **kwargs)

        return wrapper
    return decorator

# Ban
def ban_user(context, user_id=None):
    current_role = get_role(context, user_id)
    if current_role not in ("admin", "superadmin"):
        add_role(context, "banned", user_id)
        return True

def unban_user(context, user_id=None):
    current_role = get_role(context, user_id)
    if current_role == "banned":
        add_role(context, "user", user_id)
        return True

# /start
def add_a_role_on_start(update, context):
    user_id = update.effective_user.id
    role = get_default_role(user_id)
    add_role(context, role)
    return role

def start_permission(update, context):
    current_role = get_role(context)
    if current_role == "banned":
        return False
    if update.effective_user.is_bot:
        # TODO ban
        return False
    if not current_role:
        if is_bot_closed(context):
            return False
        role = add_a_role_on_start(update, context)
        if role == "banned":
            return False
    return True

# Open/Close bot; open by default
def is_bot_closed(context):
    return context.bot_data.get("is_closed")

def close_bot_for_users(context):
    context.bot_data["is_closed"] = True
    return is_bot_closed(context)

def open_bot_for_users(context):
    return context.bot_data.pop("is_closed", None)

# Info
def get_people(context, role) -> list:
    general_user_data = context.application.user_data
    return [
        str(user_id)
        for user_id in general_user_data
        if general_user_data.get(user_id, {}).get("role", "") == role
    ]

def get_people_layout(context, role):
    people_ids = get_people(context, role)
    info_lines = [
        f"{i+1}. {user_id}\n{get_user_data_essential(context, user_id)}"
        for i, user_id in enumerate(people_ids)
    ]
    return f"{role}".upper() + "\n\n" + "\n\n".join(info_lines)


def get_all_people(context) -> list:
    general_user_data = context.application.user_data
    return [
        str(user_id)
        for user_id in general_user_data
        if general_user_data.get(user_id, {}).get("role", "") != "banned"
    ]
