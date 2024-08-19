import contextlib
import asyncio
import json
import os

from telegram.ext import Application, ApplicationBuilder, PicklePersistence
from telegram import Update

from fastapi import FastAPI, Request, Response
from http import HTTPStatus
import uvicorn
from pyngrok import ngrok

# Suppress uvicorn logger
import logging
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.setLevel(logging.ERROR)

# Suppress pyngrok and fastapi loggers
pyngrok_logger = logging.getLogger("pyngrok")
pyngrok_logger.setLevel(logging.ERROR)

fastapi_logger = logging.getLogger("fastapi")
fastapi_logger.setLevel(logging.ERROR)

from .utils.init_templates import initialize_file_from_draft
from .mylogging import time_log_decorator, logger
from . import settings

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
                # Sanitize for unpickable objects: convention
                for k in list(data.keys()):
                    if k.endswith("_func"):
                        data.pop(k)
                await self.persistence.update_chat_data(chat_id, data)

        # Call the original stop method
        await super().stop()


# --------------------------------------------TELEGRAM APP---------------------------------
def prepare_app():
    root_dir = settings.TG_FILE_FOLDER_PATH or os.getcwd() 
    initialize_file_from_draft("text.xlsx", root_dir)
    persistence = PicklePersistence(
        filepath=f"{settings.TG_FILE_FOLDER_PATH}{settings.TG_BOT_NAME}Persistence", on_flush=True
    )
    application = (
        ApplicationBuilder()
        .application_class(MyApplication)
        .token(settings.TG_BOT_TOKEN)
        .persistence(persistence)
        .build()
    )

    return application

# App instance
application = prepare_app()

# Operations
@time_log_decorator
def telegram_bot_polling(debug = False):
    # Add handlers; needs to be called at the end for the decorators reason
    add_handlers(application, debug)
    # Ignore exception when Ctrl-C is pressed
    with contextlib.suppress(KeyboardInterrupt):  
        application.run_polling()


# AWS
@time_log_decorator
async def process_update(event, context):
    # Add handlers; needs to be called at the end for the decorators reason
    add_handlers(application)
    try:
        await application.initialize() # .start() ?
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


# Vultr and others
def ptb_for_webhook():
    persistence = PicklePersistence(
        filepath=f"{settings.TG_FILE_FOLDER_PATH}{settings.TG_BOT_NAME}Persistence",
        on_flush=True,
    )
    ptb = (
        ApplicationBuilder()
        .application_class(MyApplication)
        .updater(None)
        .token(settings.TG_BOT_TOKEN)
        .persistence(persistence)
        .read_timeout(7)
        .get_updates_read_timeout(42)
        .build()
    )
    add_handlers(ptb)
    return ptb

def app_for_webhook(url):
    root_dir = settings.TG_FILE_FOLDER_PATH or os.getcwd()
    initialize_file_from_draft("text.xlsx", root_dir)

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        await app.ptb.bot.setWebhook(url)
        async with app.ptb as ptb:
            await ptb.start()
            yield
            await ptb.stop()

    # Initialize FastAPI app (similar to Flask)
    app = FastAPI(lifespan=lifespan)
    # TODO Limiter
    app.ptb = ptb_for_webhook()

    @app.post("/")
    async def process_update(request: Request):
        req = await request.json()
        update = Update.de_json(req, app.ptb.bot)
        try:
            await app.ptb.process_update(update)
            return Response(status_code=HTTPStatus.OK)
        except Exception as e:
            logger.error(f"Error in process_update: {e}")
            return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    return app

def run_webhook_app():
    host = settings.TG_WEBHOOK_HOST
    port = settings.TG_WEBHOOK_PORT
    token = settings.TG_BOT_TOKEN
    url = settings.TG_WEBHOOK_URL
    if not url:
        logger.info("No url found, setting up ngrok...")
        url = ngrok.connect(port).public_url
    if not all([host, port, token]):
        raise ValueError("Please fill all the necessary settings in settings.py")
    if not url:
        raise ValueError("Please check your ngrok connection")
    app = app_for_webhook(url)
    uvicorn.run(app, host=host, port=port, access_log=False)
