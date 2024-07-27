from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from .settings import ADMIN_GROUP, SUPERADMIN_GROUP # can't remove superadmins from the admin group
from .decorators import command

from .text_handler import text_handler
from .send import send_keyboard


# List of buttons; must be unique and present in the text.xlsx;
# callbacks are the same as the button names
ADMIN_MAIN_MENU_HEADER = "admin_menu_header" # text.xlsx
PUT_TEXT_BUTTON = "add_text_button"  # text.xlsx
PUT_INTRO_VIDEO_BUTTON = "add_intro_video_button"  # text.xlsx

ADMIN_MENU = [
    PUT_TEXT_BUTTON,
    PUT_INTRO_VIDEO_BUTTON,
]


def get_admins(context: CallbackContext) -> list:
    if context.bot_data.get("admin_ids") is None:
        context.bot_data["admin_ids"] = ADMIN_GROUP + SUPERADMIN_GROUP
    return context.bot_data["admin_ids"]


def is_user_admin(update: Update, context: CallbackContext): # important function for other modules
    user_id = str(update.effective_user.id)
    return user_id in get_admins(context)


# TODO conversations:
def add_admin(context: CallbackContext, user_id: str):
    admins = get_admins(context)
    user_id = user_id.strip()
    if user_id not in admins:
        admins.append(user_id)
        return True
    return False # such admin already exists


def remove_admin(context: CallbackContext, user_id: str):
    admins = get_admins(context)
    if user_id in admins:
        # can't remove superadmins from the admin group
        if user_id in SUPERADMIN_GROUP:
            return None 
        admins.remove(user_id)
        return True
    return False


@command()
async def admin(update: Update, context: CallbackContext):
    if not is_user_admin(update, context):
        return

    # each represent a conversation handler, for example add_text_conv.py,
    # which is then connected at main.py
    options = {
        text_handler.get_text(context, option): option for option in ADMIN_MENU
    }

    buttons = [
        [
            InlineKeyboardButton(
                option_name,
                callback_data=f"{option}",
            )
        ]
        for option_name, option in options.items()
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    return await send_keyboard(update, context, keyboard, ADMIN_MAIN_MENU_HEADER)
