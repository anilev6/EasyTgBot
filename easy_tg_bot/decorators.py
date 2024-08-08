from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler
from functools import wraps
from uuid import uuid1

from .roles import check_role, DEFAULT_ALLOWED_ROLES


COMMAND_HANDLERS = {}
CALLBACK_HANDLERS = {}
CONVERSATION_HANDLERS = {}


# Decorators
def command(name=None, allowed_roles = DEFAULT_ALLOWED_ROLES):
    def decorator(func):
        command_name = name or func.__name__

        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            if not check_role(context, allowed_roles):
                return ConversationHandler.END
            return await func(update, context, *args, **kwargs)

        COMMAND_HANDLERS[command_name] = wrapper
        return wrapper
    return decorator


def button_callback(prefix=None, allowed_roles = DEFAULT_ALLOWED_ROLES):
    def decorator(func):
        callback_name = prefix or func.__name__
        callback_name = rf"^{callback_name}"

        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            # Answer query
            if update:
                query = update.callback_query
                if query:
                    await query.answer()

            if not check_role(context, allowed_roles):
                return ConversationHandler.END

            return await func(update, context, *args, **kwargs)

        CALLBACK_HANDLERS[callback_name] = wrapper
        return wrapper
    return decorator


# Utils
def register_conversation_handler(handler):
    # required for persistence
    name = handler.name or str(uuid1())
    CONVERSATION_HANDLERS[name] = handler


def add_handlers(application, debug=False):
    for _, h in CONVERSATION_HANDLERS.items():
        application.add_handler(h)

    for k, v in COMMAND_HANDLERS.items():
        application.add_handler(CommandHandler(k, v))

    for k, v in CALLBACK_HANDLERS.items():
        application.add_handler(CallbackQueryHandler(v, k))

    if debug:
        info_lines = ["HANDLERS REGISTERED"]
        names = ["conversations", "commands", "button callbacks"]
        dicts = [CONVERSATION_HANDLERS, COMMAND_HANDLERS, CALLBACK_HANDLERS]
        
        for name, handler_dict in zip(names, dicts):
            if handler_dict:
                info_lines.append(f"{name}:")
                for k, v in handler_dict.items():
                    info_lines.append(f"  {k}: {v}")
        print("\n".join(info_lines))  # avoid logging module here to keep logs clean
