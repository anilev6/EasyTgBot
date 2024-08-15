from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from .utils.context_logic import get_chat_data, put_chat_data
from .text_handler import text_handler
from .mylogging import logger, time_log_decorator


# TODO list of reserved keys for the bot
LAST_MESSAGE_ID = "lkmid"


# Caching logic
async def kb_cache_logic(
    update, context, sent_message_id, user_id=None
):
    if sent_message_id:
        # Mute a previous active window so only one active window can be in a chat
        await mute_last_active_msg(update, context, user_id)
        # Store the message ID of the new start menu message
        await register_last_active_msg(context, sent_message_id, user_id)


async def register_last_active_msg(context: CallbackContext, message_id, user_id=None):
    put_chat_data(context, LAST_MESSAGE_ID, message_id, user_id)


async def mute_last_active_msg(update: Update, context: CallbackContext, user_id=None):
    chat_data = get_chat_data(context, user_id)
    message_id = chat_data.get(LAST_MESSAGE_ID)
    chat_id = user_id or update.effective_chat.id
    if message_id:
        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
            )
            chat_data.pop(LAST_MESSAGE_ID)
        except Exception as e:
            logger.warning(f"Error muting last active keyboard {chat_id}: {str(e)}") # TODO remove user/chat_id from the logs


# Send raw
async def edit_message_no_cache(
    update: Update,
    context: CallbackContext,
    text=None,
    parse_mode=None,
    disable_web_page_preview=None,
    keyboard=None,
    user_id=None,
):
    if user_id is None:
        query = update.callback_query
        if query:
            return await query.message.edit_text(
            # doesn't fucking work:
            #return await context.bot.edit_message_text(
            #chat_id=chat_id,
            #message_id=message_id,
            reply_markup=keyboard,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
        )
        raise ValueError("Query not found")
    else:
        raise ValueError("Can't edit query for a user")


async def send_message_no_cache(
    update: Update,
    context: CallbackContext,
    text,
    keyboard=None,
    user_id=None,
    **kwargs,
):
    chat_id = user_id or update.effective_chat.id
    try:
        sent_message = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard, **kwargs)
        return sent_message.message_id
    except Exception as e:
        logger.error(f"Error sending a keyboard - {chat_id}: {e}")
        return 0

async def send_message(
    update,
    context,
    text= None,
    parse_mode=None,
    text_string_index=None,
    keyboard = None,
    user_id=None,
    replace=True,
    new=False,
    disable_web_page_preview=True,
    **kwargs,
):
    """
    - either text, parse mode kwargs, or text_string_index,
    in the latter case it will take text, parse_mode from the text.xlsx;
    - user_id = None for sending within user context;
    - replace = False for ignoring caching last message id logic;
    - new = True means no editing, but sending using caching logic;
    """
    # TODO validate kwargs usage
    # Send
    if text_string_index:
        text, parse_mode = text_handler.get_text_and_parse_mode(
            context, text_string_index, user_id
        )

    if replace and not new:
        try: 
            return await edit_message_no_cache(
                update,
                context,
                text=text,
                keyboard=keyboard,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                user_id=user_id,
            )
        except Exception as e:
            # logger.warning(f"Error editing a message: {e}")
            pass # TODO

    sent_message_id = await send_message_no_cache(
        update,
        context,
        text,
        keyboard=keyboard,
        parse_mode=parse_mode,
        disable_web_page_preview=disable_web_page_preview,
        user_id=user_id,
        **kwargs,
    )

    if replace:
        await kb_cache_logic(update, context, sent_message_id, user_id)

    return sent_message_id


# Utils + old name convention
async def send_video_from_file_id_raw(
    update, context, keyboard, file_id, caption, parse_mode, user_id=None
):
    if user_id is None:
        user_id = update.effective_chat.id

    sent_message = await context.bot.send_video(
        chat_id=user_id,
        reply_markup=keyboard,
        video=file_id,
        caption=caption,
        parse_mode=parse_mode,
    )
    return sent_message.message_id


async def send_video_from_file_id(
    update,
    context,
    keyboard,
    file_id,
    new = True,
    user_id=None,
    caption=None,
    parse_mode=None,
):
    """Sends video as a keyboard"""
    # Send
    # TODO edit video
    sent_message_id = await send_video_from_file_id_raw(
        update, context, keyboard, file_id, caption, parse_mode
    )
    if new: 
        await kb_cache_logic(
            update, context, sent_message_id, user_id
        )


# Competability with other versions
# send_text, send_keyboard, send_text_raw, send_keyboard_raw - deprecated
async def send_keyboard_raw(
    update: Update,
    context: CallbackContext,
    keyboard: InlineKeyboardMarkup,
    text: str,
    clear_after=True,
    clear_before=True,
    user_id=None,
    parse_mode=None,
    disable_web_page_preview=True,
    **kwargs,
):
    if clear_before and clear_after:
        replace, new = True, False
    else:
        replace, new = False, False

    return await send_message(
        update,
        context,
        text=text,
        parse_mode=parse_mode,
        keyboard=keyboard,
        user_id=user_id,
        replace=replace,
        new=new,
        disable_web_page_preview=disable_web_page_preview,
        **kwargs,
    )


async def send_text_raw(
    update: Update, context: CallbackContext, text: str, user_id=None, **kwargs
):
    sent_message = await context.bot.send_message(
        chat_id=user_id or update.effective_chat.id, text=text, **kwargs
    )
    return sent_message.message_id


async def send_text(
    update: Update,
    context: CallbackContext,
    text_string_index: str,
    user_id=None,
    **kwargs,
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
