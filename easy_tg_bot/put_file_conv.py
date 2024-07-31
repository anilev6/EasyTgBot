from telegram import Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .mylogging import logger
from .utils.utils import get_keyboard, end_conversation
from .send import send_keyboard

from .file_handler import FileHandler
from .admin import is_user_admin, admin
# entry points for the conversations
from .admin import PUT_TEXT_BUTTON

# file handlers
from .text_handler import text_handler

# connect the handlers
from .decorators import register_conversation_handler

# annoying warning
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)


class PutFileConversation:
    def __init__(
        self, file_handler: FileHandler, entry_point_query_pattern: str
    ):
        self.file_handler = file_handler
        self.entry_point_query_pattern = entry_point_query_pattern
        self.restrict_function = is_user_admin
        self.conversation_done_callback_function = admin
        self.INPUT_FILE = 0

        self.put_file_message = f"put_{file_handler.prefix}_file_message"  # text.xlsx
        self.error_message = "error_processing_file"  # text.xlsx

        self.start_conversation_get_file_path = self.file_handler.get_path
        self.bot_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    self.start_conversation,
                    pattern=f"^{self.entry_point_query_pattern}$",
                )
            ],
            states={
                self.INPUT_FILE: [
                    MessageHandler(
                        filters.Document.FileExtension("xlsx"), self.receive_file
                    )
                ],
            },
            fallbacks=[CallbackQueryHandler(self.end, pattern=r"^end$")],
            name=f"put_{self.file_handler.file_key}_conversation",
            persistent=True
        )

    async def end(self, update: Update, context: CallbackContext):
        await self.conversation_done_callback_function(update, context)
        return ConversationHandler.END

    async def start_conversation(self, update: Update, context: CallbackContext):
        if not self.restrict_function(update, context):
            return ConversationHandler.END  # TODO decorators

        query = update.callback_query
        await query.answer()

        keyboard = get_keyboard(context, back_button_callback="end") 
        await send_keyboard(update, context, keyboard, self.put_file_message)

        file_path = self.start_conversation_get_file_path(context)
        await self.file_handler.send_file_general(update, context, file_path)

        return self.INPUT_FILE

    async def file_error_response(
        self, update: Update, context: CallbackContext, file_path, message_text_id
    ):
        await self.file_handler.delete_file(file_path)
        keyboard = get_keyboard(
            context,
            back_button_callback="end", 
        )
        await send_keyboard(update, context, keyboard, message_text_id)
        return self.INPUT_FILE

    async def receive_file(self, update: Update, context: CallbackContext):
        if not self.restrict_function(update, context):
            return

        try:
            file_path = await self.file_handler.download_file(update)
            result = self.file_handler.validate_file(file_path)
            code, message_text_id = (
                result[0],
                result[1],
            )  # there are more args sometimes
            if code != 200:
                return await self.file_error_response(
                    update, context, file_path, message_text_id
                )

            # Success
            await self.file_handler.add_path(context, file_path)
            self.file_handler.put_file_iterable(context)

            await end_conversation(
                    update,
                    context,
                    last_message_text_string_index=message_text_id,
                )
            return await self.end(update, context)

        except Exception as e:
            logger.error(f"Error recieving the file: {str(e)}")
            return await self.file_error_response(
                update, context, file_path, self.error_message
            )

    def register_handler(self):
        register_conversation_handler(self.bot_handler)


# My handlers
put_text_file_conv = PutFileConversation(text_handler, PUT_TEXT_BUTTON)
put_text_file_conv.register_handler()
