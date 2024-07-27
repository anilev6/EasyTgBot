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

from .text_handler import text_handler
from .validate_text_file import DEFAULT_NOT_FOUND_TEXT
from .user import is_user_registered, register_user
from .send import send_keyboard, send_text
from .utils.utils import (
    get_info_from_query,
    get_keyboard,
    get_full_info,
)

from .put_intro_video_conv import put_intro_video_file_conv

from .app import application
from .mylogging import time_log_decorator, logger

# remove the annoying warning
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)


# Constants
END_CALLBACK = None # Put your start function here
LANGUAGE_CHOICE, DATA_CONSENT = range(2)


async def send_intro_video(update, context):
    # TODO
    # If there is no caption, there is no intro video
    caption, parse_mode = text_handler.get_text_and_parse_mode(context, "intro_video_caption")
    if caption == DEFAULT_NOT_FOUND_TEXT:
        # caption = None
        return

    vid_id = put_intro_video_file_conv.get_video_id(context)
    if vid_id:
        try:
            return await context.bot.send_video(
                chat_id=update.effective_chat.id, video=vid_id, caption = caption, parse_mode = parse_mode
            )
        except Exception as e:
            logger.warning(f"Error sending the intro video from file_id: {e}")

    vid_path = put_intro_video_file_conv.get_video_path(context)
    if vid_path:
        try:
            with open(vid_path, 'rb') as video_file:
                message = await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_file,
                    caption=caption,
                    parse_mode=parse_mode
                )
            # Store the file_id for future use
            if message and message.video:
                id_iterabl = put_intro_video_file_conv.get_lan_to_video_id_dict(context)
                id_iterabl[text_handler.get_user_language(context)] = message.video.file_id
                context.bot_data[put_intro_video_file_conv.video_id_dict_key] = id_iterabl
            return message
        except Exception as e:
            logger.error(f"Error sending the intro video from file: {e}")
    return None


async def end(update: Update, context: CallbackContext, intro_vid = False):
    # keyboard = get_initial_keyboard(update, context)
    # await send_keyboard(
    #     update, context, keyboard, "start_confirm_text", clear_after=False
    # )
    await send_text(update, context, "start_confirm_text", reply_markup=ReplyKeyboardRemove())
    
    if intro_vid:
        await send_intro_video(update, context)
    
    if END_CALLBACK is not None:
        await END_CALLBACK(update, context)
        return ConversationHandler.END


async def start(update: Update, context: CallbackContext):
    if update.effective_user.is_bot:  # TODO allowed users
        return ConversationHandler.END

    # refresh keyboards
    await send_text(update, context, "welcome_text", reply_markup=ReplyKeyboardRemove())  
    return await send_lan_choice_keyboard(update, context)


async def send_lan_choice_keyboard(update: Update, context: CallbackContext):
    languages = text_handler.get_languages(context)
    keyboard = get_keyboard(context, options=languages, prefix="lan")
    await send_keyboard(update, context, keyboard, "language_choice")
    return LANGUAGE_CHOICE


async def language_choice(update: Update, context: CallbackContext):
    lan = await get_info_from_query(update, "lan")
    text_handler.assign_language_to_user(context, lan)
    if is_user_registered(update, context):
        return await end(update, context)
    return await send_data_consent_keyboard(update, context)


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


@time_log_decorator
async def data_consent(update: Update, context: CallbackContext):
    # register user
    register_user(update, context)
    # collect data
    info_dict = get_full_info(update)
    for k, v in info_dict.items():
        context.user_data[k] = v
    return await end(update, context, intro_vid=True)


@time_log_decorator
async def not_data_consent(update: Update, context: CallbackContext):
    CONFIRM_BUTTON = text_handler.get_text(context, "start_confirm_button")
    if update.message.text != CONFIRM_BUTTON and not is_user_registered(update, context):
        await send_text(
            update, context, "not_confirm_text", reply_markup=ReplyKeyboardRemove()
        )
    else:
        logger.error("Error in not_data_consent")
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
)
application.add_handler(start_conv_handler)
