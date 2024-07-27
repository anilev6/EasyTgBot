from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

# from uuid import uuid1
from datetime import datetime


from ..text_handler import text_handler
from ..send import mute_last_active_keyboard, send_text
from ..mylogging import logger


# Info utils
def get_user_open_tg_info(user) -> dict:
    # Gather user info from telegram user object
    user_info = {
        # "uuid": uuid1(),  # additional anonimization
        "added_on": str(datetime.now()),
        "tg_username": f"@{user.username}",
        "tg_first_name": user.first_name,
        "tg_last_name": user.last_name,
    }
    return user_info


def get_user_hidden_tg_info(contact) -> dict:
    # Gather user info from telegram message.contact object when shared
    user_info = {
        "tg_phone_number": contact.phone_number,
        "tg_vcard": contact.vcard,
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
            # Answer
            await query.answer()

            # Get data
            query_data = query.data
            return query_data.replace(f"{prefix}_", "")
    logger.warning("get_info_from_query got no Update")


# Conversation utils
def clear_cache(context: CallbackContext):
    """
    Cached items to clean always have prefix "current" and are stored in chat_data
    """
    try:
        for k in list(context.chat_data.keys()):
            if k.startswith("current"):
                context.chat_data.pop(k)

    except Exception as e:
        logger.warning(f"Error in clear_cache: {str(e)}")


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
