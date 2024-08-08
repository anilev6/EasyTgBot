from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

# from uuid import uuid1
from datetime import datetime

from .context_logic import get_user_data, clear_cache
from ..text_handler import text_handler
from ..send import mute_last_active_keyboard, send_text
from ..mylogging import logger


# Info utils
ESSENTIAL_INFO_PREFIX = "tg"
def get_user_open_tg_info(user) -> dict:
    # Gather user info from telegram user object
    user_info = {
        # "uuid": uuid1(),  # additional anonimization
        "added_on": str(datetime.now()),
        f"{ESSENTIAL_INFO_PREFIX}_username": f"@{user.username}",
        f"{ESSENTIAL_INFO_PREFIX}_first_name": user.first_name,
        f"{ESSENTIAL_INFO_PREFIX}_last_name": user.last_name,
    }
    return user_info


def get_user_hidden_tg_info(contact) -> dict:
    # Gather user info from telegram message.contact object when shared
    user_info = {
        f"{ESSENTIAL_INFO_PREFIX}_phone_number": contact.phone_number,
        "vcard": contact.vcard,
    }
    return user_info


def get_full_info(update):
    user = update.effective_user
    user_info = get_user_open_tg_info(user)
    contact = update.message.contact
    if contact:
        contact_info = get_user_hidden_tg_info(contact)
        user_info.update(contact_info)
    return {k: v for k, v in user_info.items() if v is not None}


def put_info_to_user_data(update, context):
    info_dict = get_full_info(update)
    user_data = get_user_data(context)
    user_data.update(info_dict)


def is_info_in_user_data(update, context):
    user_data = get_user_data(context)
    for k in user_data:
        if k.startswith(ESSENTIAL_INFO_PREFIX):
            return True


def get_user_data_essential(context, user_id):
    user_data = get_user_data(context, user_id)
    info_lines = [f"{k}: {v}" for k, v in user_data.items() if k.startswith(ESSENTIAL_INFO_PREFIX)]
    return "\n".join(info_lines)


# Keyboard utils
def get_keyboard(
    context,
    options=[],
    prefix="",
    back_button_callback="",
    back_button_text_string_index="back_button", # text.xlsx
    user_id=None,
):

    buttons = []

    if prefix:
        buttons += [
            [
                InlineKeyboardButton(
                    option,
                    callback_data=f"{prefix}_{option}",
                )
            ]
            for option in options
        ]

    if back_button_callback:
        buttons += [
            [
                InlineKeyboardButton(
                    text_handler.get_text(
                        context,
                        text_string_index=back_button_text_string_index,
                        user_id=user_id,
                    ),
                    callback_data=back_button_callback,
                )
            ]
        ]

    return InlineKeyboardMarkup(buttons) if buttons else None


async def get_info_from_query(update, prefix):
    if update:
        query = update.callback_query
        if query:
            # Get data
            query_data = query.data
            return query_data.replace(f"{prefix}_", "")
    logger.warning("get_info_from_query got no Update")


# Conversation utils
async def end_conversation(
    update: Update,
    context: CallbackContext,
    clean_up=False,
    last_message_text_string_index=None,
    **kwargs,
):

    if last_message_text_string_index is not None:
        await send_text(
            update, context, text_string_index=last_message_text_string_index, **kwargs
        )

    if clean_up:
        clear_cache(context)

    await mute_last_active_keyboard(update, context)
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    return await end_conversation(
        update, context, clean_up=True, last_message_text_string_index="cancel_response"
    )  # text.xlsx
