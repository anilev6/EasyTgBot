import contextlib
import asyncio
import json
import os

from telegram.ext import Application, ApplicationBuilder, PicklePersistence
from telegram import Update

from . import settings
from .utils.init_templates import initialize_file_from_draft
from .mylogging import time_log_decorator, logger

# add handlers just with decorators throughout the code
from .decorators import add_handlers


# -------------------------------------------TELEGRAM BOT DB------------------------------
class MyApplication(Application):
    # Disagreeing with the user/chat_data read-only policy
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.user_data = self._user_data
        self.chat_data = self._chat_data

    async def stop(self):
        # TODO handle urgent shutdown
        # Ensure all user data and chat data are saved
        if self.persistence:
            for user_id, data in self.user_data.items():
                await self.persistence.update_user_data(user_id, data)
            for chat_id, data in self.chat_data.items():
                await self.persistence.update_chat_data(chat_id, data)

        # Call the original stop method
        await super().stop()


# --------------------------------------------TELEGRAM APP---------------------------------
@time_log_decorator
def prepare_app(debug):
    root_dir = settings.FILE_FOLDER_PATH or os.getcwd() 
    initialize_file_from_draft("text.xlsx", root_dir)
    persistence = PicklePersistence(
        filepath=f"{settings.FILE_FOLDER_PATH}{settings.BOT_NAME}Persistence", on_flush=True
    )
    application = (
        ApplicationBuilder()
        .application_class(MyApplication)
        .token(settings.TG_BOT_TOKEN)
        .persistence(persistence)
        .build()
    )
    # Add handlers; needs to be called at the end for the decorators reason
    add_handlers(application, debug)
    return application


@time_log_decorator
def telegram_bot_polling(debug = False):
    application = prepare_app(debug)
    # Ignore exception when Ctrl-C is pressed
    with contextlib.suppress(KeyboardInterrupt):  
        application.run_polling()


@time_log_decorator
async def process_update(event, context):
    application = prepare_app(False)
    try:
        await application.initialize()
        await application.process_update(
            Update.de_json(json.loads(event["body"]), application.bot)
        )
        await application.stop()
        return {"statusCode": 200, "body": "Success"}

    except Exception as e:
        logger.error(f"Error in process_update: {e}")
        return {"statusCode": 500, "body": "Failure"}


def lambda_handler(event, context):
    return asyncio.get_event_loop().run_until_complete(process_update(event, context))
