from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)
import asyncio
from random import randint

from .mylogging import logger
from .roles import DEFAULT_ADMIN_ROLES, role_required, get_all_people, get_people, get_people_role_group
from .decorators import register_conversation_handler
from .text_handler import text_handler
from .send import send_message
from .utils.context_logic import get_chat_data, put_chat_data
from .utils.utils import clear_cache, get_keyboard, get_info_from_query
from .admin import admin, MAILING_BUTTON


# remove the annoying warning
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)


# Constants
INPUT_MESSAGE, DELIVERY_OPTIONS, INPUT_IDS, CONFIRM = range(4)
MESSAGE_KEY = "current_message_func" # convention for clearing up


@role_required(DEFAULT_ADMIN_ROLES)
async def cancel(update: Update, context: CallbackContext):
    clear_cache(context)
    await admin(update, context)
    return ConversationHandler.END


@role_required(DEFAULT_ADMIN_ROLES)
async def start_conversation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = get_keyboard(context, back_button_callback="mailing_cancel")
    await send_message(update, context, keyboard=keyboard, text_string_index="mailing_input_message")
    return INPUT_MESSAGE


@role_required(DEFAULT_ADMIN_ROLES)
async def handle_message(update: Update, context: CallbackContext) -> int:
    message = update.message
    if message:
        put_chat_data(context, MESSAGE_KEY, message)
        return await send_delivery_options(update, context)
    logger.error("Error in handle_message in mailing.")
    return await cancel(update, context)


async def send_delivery_options(update: Update, context: CallbackContext):
    txt_ids_buttons = [
        "all_users",
        "only_users",
        "only_admins",
        "input_ids",
    ]
    buttons = [
        [
            InlineKeyboardButton(
                text_handler.get_text(context, txt_id),
                callback_data=f"mailing_deliv_choice_{txt_id}",
            )
        ] for txt_id in txt_ids_buttons
    ]
    buttons.append(
        [
            InlineKeyboardButton(
                text_handler.get_text(context, "back_button"),
                callback_data="mailing_cancel",
            )
        ]
    )
    keyboard = InlineKeyboardMarkup(buttons)
    await send_message(update, context, keyboard=keyboard, text_string_index="mailing_deliv_choice_message")
    return DELIVERY_OPTIONS


@role_required(DEFAULT_ADMIN_ROLES)
async def handle_delivery_options_choice(update: Update, context: CallbackContext):
    deliv_choice = await get_info_from_query(update, "mailing_deliv_choice")
    put_chat_data(context, "current_deliv_choice", deliv_choice)

    if deliv_choice == "input_ids":
        keyboard = get_keyboard(
            context, back_button_callback="mailing_cancel"
        )
        await send_message(
            update, context, keyboard=keyboard, text_string_index="mailing_input_ids_message"
        )
        return INPUT_IDS
    else:
        return await send_confirm(update, context)

async def send_confirm(update: Update, context: CallbackContext):
    txt_ids_buttons = ["mailing_confirm"]
    buttons = [
        [
            InlineKeyboardButton(
                text_handler.get_text(context, txt_id),
                callback_data=txt_id,
            )
        ]
        for txt_id in txt_ids_buttons
    ]
    buttons.append(
        [
            InlineKeyboardButton(
                text_handler.get_text(context, "back_button"),
                callback_data="mailing_cancel",
            )
        ]
    )
    keyboard = InlineKeyboardMarkup(buttons)
    await send_message(
        update, context, keyboard=keyboard, text_string_index="mailing_confirm_message"
    )
    return CONFIRM


@role_required(DEFAULT_ADMIN_ROLES)
async def handle_input_ids(update: Update, context: CallbackContext) -> int:
    text = update.message.text.strip()
    try:
        user_ids = [i.strip() for i in text.split(",")]
    except Exception as e:
        msg = f"Error handling ids: {e}"
        logger.error(msg)
        await send_message(update, context, text=msg, replace=False)
        return await cancel(update, context)
    put_chat_data(context, "current_user_ids", user_ids)
    return await send_confirm(update, context)


@role_required(DEFAULT_ADMIN_ROLES)
async def handle_confirm(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    if query.data.startswith("mailing_confirm"):
        chat_data = get_chat_data(context)
        current_deliv_choice = chat_data.pop("current_deliv_choice", "")
        GET_DELIV_FUNC = {
            "all_users": get_all_people,
            "only_users": lambda c: get_people(c, "user"),
            "only_admins": lambda c: get_people_role_group(c, DEFAULT_ADMIN_ROLES),
            "input_ids": lambda c: get_chat_data(c).pop("current_user_ids", []),
        }
        get_ids_func = GET_DELIV_FUNC.get(current_deliv_choice)
        if get_ids_func:
            return await send_message_to_users(update, context, get_ids_func)
        else:
            logger.error(f"Error in mailing: unable to find ids - {query.data}")

    logger.error(f"Error in mailing: confirm callback not found - {query.data}")
    return await cancel(update, context)


# Utils
async def send_message_to_users(update: Update, context: CallbackContext, get_current_user_group_ids_func):
    chat_data = get_chat_data(context)
    message = chat_data.pop(MESSAGE_KEY, None)
    if not message:
        logger.error("Error in mailing: message not found")
        return await cancel(update, context)

    bot = context.bot
    if message.photo:
        func = bot.send_photo
        kwargs = {
            "photo": message.photo[-1].file_id,
            "caption": message.caption
        }

    elif message.video:
        func = bot.send_video
        kwargs = {
            "video": message.video.file_id,
            "caption": message.caption
        }

    elif message.document:
        func = bot.send_document
        kwargs = {
            "document": message.document.file_id,
            "caption": message.caption
        }

    elif message.text:
        func = bot.send_message
        kwargs = {
            "text": message.text
        }

    else:
        logger.error(f"Error mailing message to all users: {message}")
        await send_message(update, context, text_string_index="mailing_wrong_format_message", replace=False)
        return INPUT_MESSAGE

    await send_something_to_users(update, context, get_current_user_group_ids_func, func, **kwargs)
    return await cancel(update, context)


async def send_something_to_users(update, context, get_current_user_group_ids_func, function, *args, **kwargs):
    await send_message(update, context, text_string_index="admin_mailing_in_progress")
    for user_id in get_current_user_group_ids_func(context):
        await asyncio.sleep(randint(1, 5))  # sleep to repsect api rates
        try:
            await function(*args, chat_id=int(user_id), **kwargs)
        except Exception as e:
            msg = f"{user_id}: {str(e)}"
            logger.error("Error in mailing - "+ msg)
            full_msg = (
                text_handler.get_text(context, "admin_mailing_error") + "\n" + msg
            )
            await send_message(update, context,text=full_msg, replace=False)
    return await send_message(update, context, text_string_index="admin_mailing_done")


# Object
message_mailing_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_conversation, pattern=f"^{MAILING_BUTTON}$")
    ],
    states={
        INPUT_MESSAGE: [
            MessageHandler(filters.ALL, handle_message),
        ],
        CONFIRM: [
            CallbackQueryHandler(handle_confirm, pattern=r"^mailing_confirm.*"),
        ],
        INPUT_IDS: [
            MessageHandler(filters.TEXT, handle_input_ids),
        ],
        DELIVERY_OPTIONS: [
            CallbackQueryHandler(
                handle_delivery_options_choice, pattern=r"^mailing_deliv_choice_.*"
            ),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel, pattern="^mailing_cancel$"),
    ],
    name="mailing",
    persistent=True,
    allow_reentry=True,
)
register_conversation_handler(message_mailing_conv_handler)
