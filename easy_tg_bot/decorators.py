from functools import wraps
from telegram.ext import CommandHandler


COMMAND_HANDLERS = {}


def command(name=None):
    def decorator(func):
        command_name = name or func.__name__

        @wraps(func)
        async def wrapper(update, context):
            return await func(update, context)

        COMMAND_HANDLERS[command_name] = wrapper
        return wrapper

    return decorator


def add_command_handlers(application):
    for k, v in COMMAND_HANDLERS.items():
        application.add_handler(CommandHandler(k, v))
