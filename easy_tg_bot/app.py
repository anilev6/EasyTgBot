import contextlib
from telegram.ext import ApplicationBuilder, PicklePersistence

from .settings import TG_BOT_TOKEN, BOT_NAME
from .mylogging import time_log_decorator

# add handlers just with decorators throughout the code
from .decorators import add_handlers


# -------------------------------------------TELEGRAM BOT DB------------------------------
persistence = PicklePersistence(filepath=f"{BOT_NAME}Persistence", on_flush=True)


# --------------------------------------------TELEGRAM APP---------------------------------
application = ApplicationBuilder().token(TG_BOT_TOKEN).persistence(persistence).build()


# --------------------------------------------TELEGRAM APP---------------------------------
@time_log_decorator
def telegram_bot_polling(debug = False):
    # Add handlers; needs to be called at the end for the decorators reason
    add_handlers(application, debug)

    # Ignore exception when Ctrl-C is pressed
    with contextlib.suppress(KeyboardInterrupt):  
        application.run_polling()
