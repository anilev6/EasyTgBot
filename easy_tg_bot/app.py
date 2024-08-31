import contextlib
import asyncio
import json
import os

from telegram.ext import Application, ApplicationBuilder, PicklePersistence
from telegram import Update

from fastapi import FastAPI, Request, Response
from http import HTTPStatus
import uvicorn

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
from .error import error


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
    root_dir = "./data"
    initialize_file_from_draft("text.xlsx", root_dir)
    persistence = PicklePersistence(
        filepath=os.path.join(root_dir, f"{settings.BOT_NAME}Persistence"),
        on_flush=True,
    )
    application = (
        ApplicationBuilder()
        .application_class(MyApplication)
        .token(settings.BOT_TOKEN)
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
    # Universal eror handler 
    # TODO custom or this one
    application.add_error_handler(error)
    # Ignore exception when Ctrl-C is pressed
    with contextlib.suppress(KeyboardInterrupt):  
        application.run_polling()


# AWS
@time_log_decorator
async def process_update(event, context):
    # Add handlers; needs to be called at the end for the decorators reason
    add_handlers(application)
    # Universal eror handler 
    # TODO custom or this one
    application.add_error_handler(error)
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
    root_dir = "./data"
    persistence = PicklePersistence(
        filepath=os.path.join(root_dir, f"{settings.BOT_NAME}Persistence"),
        on_flush=True,
    )
    ptb = (
        ApplicationBuilder()
        .application_class(MyApplication)
        .updater(None)
        .token(settings.BOT_TOKEN)
        .persistence(persistence)
        .read_timeout(7)
        .get_updates_read_timeout(42)
        .build()
    )
    add_handlers(ptb)
    # Universal eror handler 
    # TODO custom or this one
    application.add_error_handler(error)
    return ptb


def app_for_webhook(url, cert_file_location=None, secret_token=None, on_startup_func=None):
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        # On startup - run a simple function on start
        on_startup_func = app.on_startup_func
        if callable(on_startup_func):
            on_startup_func()

        # Set webhook
        if cert_file_location is None:
            await app.ptb.bot.setWebhook(url=url, secret_token=secret_token)
        else:
            with open(cert_file_location, "r") as cert_file:
                await app.ptb.bot.setWebhook(
                    url=url, certificate=cert_file, secret_token=secret_token
                )
        
        # On shutdown stop the bot
        async with app.ptb as ptb:
            await ptb.start()
            yield
            await ptb.stop()

    # Initialize FastAPI app (similar to Flask)
    # TODO Limiter ? or nginx set up
    app = FastAPI(lifespan=lifespan)
    app.ptb = ptb_for_webhook()
    app.on_startup_func = on_startup_func

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

# Launch
@time_log_decorator
def run_webhook_uvicorn(access_log=True, on_startup_func=None):
    """
    - requires ssl folder;

    - env:
        WEBHOOK_URL
        CERT_FILE_PATH
        LISTEN
        PORT
        SECRET_TOKEN (optional)

    - Nginx set up if there is a secret token:
        # nginx.conf
        location / {
            proxy_pass http://testbot:88;
            proxy_set_header X-Telegram-Bot-Api-Secret-Token your_secret_token;
        }

    - Check webhook status
        https://api.telegram.org/bot<your_bot_token>/getWebhookInfo
    """
    # secrets
    webhook_url = settings.get_secret("WEBHOOK_URL")
    cert_file_path = settings.get_secret("CERT_FILE_PATH", "") or None
    # optional
    listen = settings.get_secret("LISTEN", "0.0.0.0")  # we're in a docker container
    port = settings.get_secret("PORT", "80")
    secret_token = settings.get_secret("SECRET_TOKEN", "") or None

    # run
    app = app_for_webhook(webhook_url, cert_file_path, secret_token, on_startup_func=on_startup_func)
    uvicorn.run(app, host=listen, port=int(port), access_log=access_log)


# TODO big load solution
def run_webhook_gunicorn(env_file=False, on_startup_func=None):
    """This might interfere with the convrsation handlers and spawn separate contexts."""
    webhook_url = settings.get_secret("WEBHOOK_URL", env_file=env_file)
    cert_file_path = settings.get_secret("CERT_FILE_PATH", env_file=env_file)
    listen = settings.get_secret(
        "LISTEN", env_file=env_file
    )  # we're in a docker container
    port = settings.get_secret("PORT", env_file=env_file)
    # optional
    secret_token = settings.get_secret("SECRET_TOKEN", env_file=env_file)  # or None

    global app
    app = app_for_webhook(webhook_url, cert_file_path, secret_token, on_startup_func=on_startup_func)

    file_name = __file__.split("/")[-1].split(".")[0]
    command = " ".join(
        [
            "gunicorn",
            "-w",
            "4",
            "-k",
            "uvicorn.workers.UvicornWorker",
            "-b",
            f"{listen}:{port}",
            f"{file_name}:app",
        ]
    )
    os.system(command)
