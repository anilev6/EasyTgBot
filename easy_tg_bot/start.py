from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from asyncio import sleep

from .roles import start_permission, role_required
from .text_handler import text_handler
from .send import send_keyboard, send_text
from .utils.utils import (
    get_info_from_query,
    get_keyboard,
    put_info_to_user_data,
    is_info_in_user_data
)

from .put_intro_video_conv import put_intro_video_file_conv

from .decorators import register_conversation_handler
from .mylogging import logger

# remove the annoying warning
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)


# Constants
START_DONE_CALLBACK = None  # Put your start function here; preferably it involves send_keyboard
LANGUAGE_CHOICE, DATA_CONSENT = range(2)


async def start(update: Update, context: CallbackContext):
    if not start_permission(update, context):  # TODO allowed users
        return ConversationHandler.END

    # refresh keyboards
    await send_text(
        update, context, "welcome_text", reply_markup=ReplyKeyboardRemove()
    )  # just in case
    return await send_lan_choice_keyboard(update, context)


@role_required()
async def send_lan_choice_keyboard(update: Update, context: CallbackContext):
    languages = text_handler.get_languages(context)
    keyboard = get_keyboard(context, options=languages, prefix="lan")
    await send_keyboard(update, context, keyboard, "language_choice")
    return LANGUAGE_CHOICE


@role_required()
async def language_choice(update: Update, context: CallbackContext):
    lan = await get_info_from_query(update, "lan")
    text_handler.assign_language_to_user(context, lan)
    if is_info_in_user_data(update, context):
        return await end(update, context)
    return await send_data_consent_keyboard(update, context)


@role_required()
async def send_data_consent_keyboard(update: Update, context: CallbackContext):
    CONFIRM_BUTTON = text_handler.get_text(context, "start_confirm_button")
    EXIT_BUTTON = text_handler.get_text(context, "back_button")
    buttons = [
        [KeyboardButton(CONFIRM_BUTTON, request_contact=True)],
        [KeyboardButton(EXIT_BUTTON)],
    ]
    keyboard = ReplyKeyboardMarkup(
        buttons, one_time_keyboard=True, resize_keyboard=True
    )
    await send_keyboard(update, context, keyboard, "data_policy", clear_after = False)
    return DATA_CONSENT


@role_required()
async def data_consent(update: Update, context: CallbackContext):
    put_info_to_user_data(update, context)
    logger.info("New user!")
    return await end(update, context, intro_vid=True)


@role_required()
async def not_data_consent(update: Update, context: CallbackContext):
    CONFIRM_BUTTON = text_handler.get_text(context, "start_confirm_button")
    if update.message.text != CONFIRM_BUTTON:
        await send_text(
            update, context, "not_confirm_text", reply_markup=ReplyKeyboardRemove()
        )
    else:
        logger.error("Error in not_data_consent")
    return ConversationHandler.END


@role_required()
async def end(update: Update, context: CallbackContext, intro_vid=False):
    # remove keyboard
    await send_text(
        update, context, "start_confirm_text", reply_markup=ReplyKeyboardRemove()
    )

    if intro_vid:
        await put_intro_video_file_conv.send_intro_video(update, context)
        await sleep(2)

    if START_DONE_CALLBACK is not None:
        await START_DONE_CALLBACK(update, context)  # <- has to use
    
    return ConversationHandler.END


# objects
start_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        LANGUAGE_CHOICE: [
            CallbackQueryHandler(language_choice, pattern=r"^lan_.*"),
        ],
        DATA_CONSENT: [
            MessageHandler(filters.CONTACT, data_consent),
        ],
    },
    fallbacks=[
        MessageHandler(filters.ALL, not_data_consent),
    ],
    name = "start_command",
    persistent = True
)

register_conversation_handler(start_conv_handler)
