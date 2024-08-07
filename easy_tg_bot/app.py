import contextlib
from telegram.ext import Application, ApplicationBuilder, PicklePersistence

from .settings import TG_BOT_TOKEN, BOT_NAME
from .mylogging import time_log_decorator

# add handlers just with decorators throughout the code
from .decorators import add_handlers


# -------------------------------------------TELEGRAM BOT DB------------------------------
persistence = PicklePersistence(filepath=f"{BOT_NAME}Persistence", on_flush=True)


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
        # TODO urgent shutdown
        # Ensure all user data and chat data are saved
        if self.persistence:
            for user_id, data in self.user_data.items():
                await self.persistence.update_user_data(user_id, data)
            for chat_id, data in self.chat_data.items():
                await self.persistence.update_chat_data(chat_id, data)

        # Call the original stop method
        await super().stop()


# --------------------------------------------TELEGRAM APP---------------------------------
application = (
    ApplicationBuilder()
    .application_class(MyApplication)
    .token(TG_BOT_TOKEN)
    .persistence(persistence)
    .build()
)


# --------------------------------------------TELEGRAM APP---------------------------------
@time_log_decorator
def telegram_bot_polling(debug = False):
    # Add handlers; needs to be called at the end for the decorators reason
    add_handlers(application, debug)

    # Ignore exception when Ctrl-C is pressed
    with contextlib.suppress(KeyboardInterrupt):  
        application.run_polling()
