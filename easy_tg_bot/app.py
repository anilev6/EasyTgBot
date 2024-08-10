import contextlib
import asyncio
import json

from telegram.ext import Application, ApplicationBuilder, PicklePersistence
from telegram import Update

from . import settings
from .mylogging import time_log_decorator

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
def telegram_bot_polling(debug = False):
    persistence = PicklePersistence(
        filepath=f"{settings.BOT_NAME}Persistence", on_flush=True
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

    # Ignore exception when Ctrl-C is pressed
    with contextlib.suppress(KeyboardInterrupt):  
        application.run_polling()


@time_log_decorator
async def telegram_webhook(event, context):
    persistence = PicklePersistence(
        filepath=f"{settings.BOT_NAME}Persistence", on_flush=True
    )
    application = (
        ApplicationBuilder()
        .application_class(MyApplication)
        .token(settings.TG_BOT_TOKEN)
        .persistence(persistence)
        .build()
    )
    add_handlers(application)
    try:
        await application.initialize()
        await application.process_update(
            Update.de_json(json.loads(event["body"]), application.bot)
        )
        return {"statusCode": 200, "body": "Success"}

    except Exception as exc:
        return {"statusCode": 500, "body": "Failure"}


def lambda_handler(event, context):
    return asyncio.get_event_loop().run_until_complete(telegram_webhook(event, context))
