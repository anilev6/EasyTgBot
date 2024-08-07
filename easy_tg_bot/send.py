from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from .utils.context_logic import get_chat_data, put_chat_data
from .text_handler import text_handler
from .mylogging import logger


# Caching logic
async def register_last_active_keyboard(context: CallbackContext, message_id, user_id=None):
    put_chat_data(context, "last_keyboard_message_id", message_id, user_id)


async def mute_last_active_keyboard(update: Update, context: CallbackContext, user_id=None):
    chat_data = get_chat_data(context, user_id)
    message_id = chat_data.get("last_keyboard_message_id")
    if message_id:
        try:
            await context.bot.delete_message(
                chat_id=user_id or update.effective_chat.id,
                message_id=message_id,
            )
            chat_data.pop("last_keyboard_message_id")

        except Exception as e:
            logger.warning(f"Error muting last active keyboard {user_id}: {str(e)}")


# Send raw
async def send_text_raw(update: Update, context: CallbackContext, text: str, user_id = None, **kwargs):
    sent_message = await context.bot.send_message(chat_id=user_id or update.effective_chat.id, text=text, **kwargs)
    return sent_message.message_id


async def send_keyboard_raw(
    update: Update,
    context: CallbackContext,
    keyboard: InlineKeyboardMarkup,
    text: str,
    clear_after=True,
    clear_before = True,
    user_id=None,
    **kwargs,
):

    if clear_before:
        # Mute a previous active window so only one active window can be in a chat
        await mute_last_active_keyboard(update, context, user_id)

    # Send
    sent_message_id = await send_text_raw(
        update, context, text, user_id = user_id, reply_markup=keyboard, **kwargs
    )

    if clear_after:
        # Store the message ID of the new start menu message
        await register_last_active_keyboard(context, sent_message_id, user_id)


# text_string_index needed only
async def send_text(
    update: Update,
    context: CallbackContext,
    text_string_index: str,
    user_id = None,
    **kwargs
):
    TEXT, PARSE_MODE = text_handler.get_text_and_parse_mode(
        context, text_string_index, user_id
    )
    return await send_text_raw(
        update,
        context,
        TEXT,
        user_id=user_id,
        parse_mode=PARSE_MODE,
        # disable_web_page_preview=True,
        **kwargs,
    )


async def send_keyboard(
    update: Update,
    context: CallbackContext,
    keyboard: InlineKeyboardMarkup,
    text_string_index: str,
    user_id=None,
    clear_after=True,
    clear_before=True,
    **kwargs,
):
    TEXT, PARSE_MODE = text_handler.get_text_and_parse_mode(
        context, text_string_index, user_id
    )
    return await send_keyboard_raw(
        update,
        context,
        keyboard,
        TEXT,
        user_id=user_id,
        clear_after=clear_after,
        clear_before=clear_before,
        parse_mode=PARSE_MODE,
        disable_web_page_preview=True,
        **kwargs,
    )


async def send_video_from_file_id_raw(
    update, context, keyboard, file_id, caption, parse_mode, user_id=None, **kwargs
):
    if user_id is None:
        user_id = update.effective_chat.id

    sent_message = await context.bot.send_video(
        chat_id=user_id,
        reply_markup=keyboard,
        video=file_id,
        caption=caption,
        parse_mode=parse_mode,
        **kwargs
    )
    return sent_message.message_id


async def send_video_from_file_id(
    update,
    context,
    keyboard,
    file_id,
    caption=None,
    parse_mode=None,
    user_id=None,
    clear_after=True,
    clear_before=True,
    **kwargs,
):
    """Sends video as a keyboard"""
    # TODO the following structure as a decorator

    if clear_before:
        # Mute a previous active window so only one active window can be in a chat
        await mute_last_active_keyboard(update, context, user_id)

    # Send
    sent_message_id = await send_video_from_file_id_raw(
        update, context, keyboard, file_id, caption, parse_mode, **kwargs
    )

    if clear_after:
        # Store the message ID of the new start menu message
        await register_last_active_keyboard(context, sent_message_id, user_id)
