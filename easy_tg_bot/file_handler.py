from telegram import Update
from telegram.ext import CallbackContext
import aiofiles.os

from .mylogging import logger, get_time


class FileHandler:
    def __init__(
        self,
        prefix,
        read_file_function=lambda file_path: {},
        validate_function=lambda file_path: (200, "validate_200"),     
    ):
        self.prefix = prefix
        self.default_path = f"{prefix}.xlsx"
        self.file_key = f"{prefix}_file"
        self.key_to_iter = f"{prefix}_iterable"
        # To call inside the class; to call outside, put extra arg in
        self.read_file = lambda self, *args: read_file_function(*args)  # into something iterable
        self.validate_file = lambda self, *args: validate_function(*args)

    # Basics
    async def download_file(self, update: Update):
        file_extension = update.message.effective_attachment.file_name.split(".")[-1]
        file_name = self.prefix + "_from_" + get_time(string=True)
        file_path = f"{file_name}.{file_extension}"
        new_file = await update.message.effective_attachment.get_file()
        await new_file.download_to_drive(file_path)
        return file_path

    async def delete_file(self, file_path):
        if file_path == self.default_path:
            return  # deleting of the example file does nothing
        try:
            await aiofiles.os.remove(file_path)
            logger.info(f"Successfully deleted file: {file_path}")
        except OSError as e:
            logger.error(f"Error deleting file {file_path}: {e.strerror}")

    # Send file
    async def send_file_general(
        self, update: Update, context: CallbackContext, file_path
    ):  
        try:
            with open(file_path, "rb") as file:
                message = await context.bot.send_document(
                    chat_id=update.effective_chat.id, document=file, filename=file_path
                )
            if update:
                query = update.callback_query
                if query:
                    await query.answer()

            return message.id if message else None

        except Exception as e:
            logger.error(f"Error sending a {self.prefix} file: {e}")
            return

    async def send_file(self, update: Update, context: CallbackContext):
        path = self.get_path(context)
        return await self.send_file_general(update, context, path)

    # Storing path of the file
    def get_path(self, context: CallbackContext) -> str:
        return context.bot_data.get(self.file_key, self.default_path)

    async def add_path(self, context: CallbackContext, new_path: str):
        """use only after validation"""
        path = self.get_path(context)
        await self.delete_file(path)
        context.bot_data[self.file_key] = new_path

    # Storing proccessed version of the file
    def put_file_iterable(self, context: CallbackContext):
        """use only after refreshing path"""
        path = self.get_path(context)
        context.bot_data[self.key_to_iter] = self.read_file(None, path)

    def get_file_iterable(self, context: CallbackContext):
        if not context.bot_data.get(self.key_to_iter):
            self.put_file_iterable(context)
        return context.bot_data.get(self.key_to_iter)
