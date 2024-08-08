from telegram import Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .put_file_conv import PutFileConversation
from .mylogging import logger
from .utils.context_logic import put_chat_data, get_chat_data
from .utils.utils import get_keyboard, get_info_from_query, end_conversation
from .send import send_keyboard
from .text_handler import text_handler
from .validate_text_file import DEFAULT_NOT_FOUND_TEXT

from .roles import check_role, DEFAULT_ALLOWED_ROLES
# entry point for the conversations
from .admin import ADD_INTRO_VID_BUTTON
from .video_handler import intro_video_handler

# annoying warning
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)


class PutVideoConversation(PutFileConversation):
    def __init__(self, file_handler, entry_point_query_pattern):
        super().__init__(file_handler, entry_point_query_pattern)

        self.put_file_message = f"put_{file_handler.prefix}_video_message"  # text.xlsx
        self.error_message = "error_processing_video"  # text.xlsx
        self.success_message = "success_adding_video"  # text.xlsx

        self.INPUT_LAN = 1
        self.lan_prefix = f"{file_handler.prefix}_vlan"
        self.cached_lan_key = f"current_{self.lan_prefix}"
        self.video_path_dict_key = f"{file_handler.prefix}_video_dict"
        self.video_id_dict_key = f"{file_handler.prefix}_video_id_dict"
        self.bot_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    self.start_conversation,
                    pattern=f"^{self.entry_point_query_pattern}$",
                )
            ],
            states={
                self.INPUT_LAN: [
                    CallbackQueryHandler(
                        self.language_choice, pattern=rf"^{self.lan_prefix}_"
                    )
                ],
                self.INPUT_FILE: [MessageHandler(filters.VIDEO, self.receive_file)],
            },
            fallbacks=[CallbackQueryHandler(self.end, pattern=r"^end$")],
            name=f"put_{self.file_handler.file_key}",
            persistent=True,
        )

    async def start_conversation(self, update: Update, context: CallbackContext):
        # Answer callback
        if update:
            query = update.callback_query
            if query:
                await query.answer()

        # Check role
        if not self.restrict_function(update, context):
            return ConversationHandler.END  # TODO decorators

        languages = text_handler.get_languages(context)
        keyboard = get_keyboard(
            context,
            options=languages,
            prefix=self.lan_prefix,
            back_button_callback="end",
        )
        await send_keyboard(update, context, keyboard, "intro_video_language_choice") # text.xlsx
        return self.INPUT_LAN

    async def language_choice(self, update: Update, context: CallbackContext):
        # Answer callback
        if update:
            query = update.callback_query
            if query:
                await query.answer()

        # Check role
        if not self.restrict_function(update, context):
            return ConversationHandler.END 

        info = await get_info_from_query(update, self.lan_prefix)
        put_chat_data(context, self.cached_lan_key, info)
        keyboard = get_keyboard(context, back_button_callback="end") 
        await send_keyboard(update, context, keyboard, self.put_file_message)
        return self.INPUT_FILE

    async def receive_file(self, update: Update, context: CallbackContext):
        if not self.restrict_function(update, context):
            return ConversationHandler.END  

        # This goes after the language choice
        chat_data = get_chat_data(context)
        current_lan = chat_data.get(self.cached_lan_key)
        if not current_lan:
            logger.error("Error regisreting the video: language missing")
            await end_conversation(
                update,
                context,
                last_message_text_string_index=self.error_message,
                clean_up=True,
            )
            return await self.end(update, context)

        try:
            file_path = await self.file_handler.download_file(update)
            # Save intro video
            iterabl = self.get_lan_to_video_path_dict(context)
            old_file_path = iterabl.pop(current_lan, None)
            if old_file_path:
                await self.file_handler.delete_file(old_file_path)
                id_iterabl = self.get_lan_to_video_id_dict(context)
                id_iterabl.pop(current_lan, None)

            iterabl[current_lan] = file_path
            context.bot_data[self.video_path_dict_key] = iterabl

            await end_conversation(
                update,
                context,
                last_message_text_string_index=self.success_message,
                clean_up=True
            )
            await self.send_intro_video(update, context)
            logger.info("Intro video added")
            return await self.end(update, context)

        except Exception as e:
            logger.error(f"Error recieving the file: {str(e)}")
            return await self.file_error_response(
                update, context, file_path, self.error_message
            )

    def get_lan_to_video_path_dict(self, context):
        return context.bot_data.get(self.video_path_dict_key, {})

    def get_lan_to_video_id_dict(self, context):
        return context.bot_data.get(self.video_id_dict_key, {})

    def get_video_path(self, context):
        lan = text_handler.get_user_language(context)
        dic = self.get_lan_to_video_path_dict(context)
        return dic.get(lan)

    def get_video_id(self, context):
        lan = text_handler.get_user_language(context)
        dic = self.get_lan_to_video_id_dict(context)
        return dic.get(lan)

    async def send_intro_video(self, update, context):
        if not check_role(context, DEFAULT_ALLOWED_ROLES):
            return ConversationHandler.END 

        # If there is no caption, there is no intro video
        caption, parse_mode = text_handler.get_text_and_parse_mode(
            context, "intro_video_caption"
        )
        if caption == DEFAULT_NOT_FOUND_TEXT:
            # caption = None
            return

        vid_id = self.get_video_id(context)
        if vid_id:
            try:
                return await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=vid_id,
                    caption=caption,
                    parse_mode=parse_mode,
                )
            except Exception as e:
                logger.warning(f"Sending the intro video from file_id: {e}")

        vid_path = self.get_video_path(context)
        if vid_path:
            try:
                with open(vid_path, "rb") as video_file:
                    message = await context.bot.send_video(
                        chat_id=update.effective_chat.id,
                        video=video_file,
                        caption=caption,
                        parse_mode=parse_mode,
                    )
                # Store the file_id for future use
                if message and message.video:
                    id_iterabl = self.get_lan_to_video_id_dict(context)
                    id_iterabl[text_handler.get_user_language(context)] = (
                        message.video.file_id
                    )
                    context.bot_data[self.video_id_dict_key] = (
                        id_iterabl
                    )
                return message
            except Exception as e:
                logger.error(f"Error sending the intro video from file: {e}")
        return None


put_intro_video_file_conv = PutVideoConversation(intro_video_handler, ADD_INTRO_VID_BUTTON)
put_intro_video_file_conv.register_handler()
