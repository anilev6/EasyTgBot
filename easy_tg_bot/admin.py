from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from .roles import DEFAULT_ADMIN_ROLES
from .decorators import command

from .text_handler import text_handler
from .send import send_keyboard


# List of buttons; must be unique and present in the text.xlsx;
# callbacks are the same as the button names
ADMIN_MAIN_MENU_HEADER = "admin_menu_header"
ADD_TEXT_BUTTON = "add_text_button"
ADD_INTRO_VID_BUTTON = "add_intro_video_button"
ADMIN_MENU = [
    ADD_TEXT_BUTTON,
    ADD_INTRO_VID_BUTTON,
]


@command(allowed_roles=DEFAULT_ADMIN_ROLES)
async def admin(update: Update, context: CallbackContext):
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
