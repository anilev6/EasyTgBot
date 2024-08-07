# Convention: user_id = None means the user modifies their data themselves,
# otherwise it requires user telegram id and happens from the outside (admin banning a user, etc)

from ..mylogging import logger


def get_user_data(context, user_id = None):
    if user_id is None:
        return context.user_data
    else:
        return context.application.user_data.setdefault(int(user_id), {})

def put_user_data(context, key, value, user_id = None):
    user_data = get_user_data(context, user_id)
    user_data[key] = value

def get_chat_data(context, chat_id = None):
    if chat_id is None:
        return context.chat_data
    else:
        return context.application.chat_data.setdefault(int(chat_id), {})

def put_chat_data(context, key, value, chat_id = None):
    chat_data = get_chat_data(context, chat_id)
    chat_data[key] = value

# Conversation util
def clear_cache(context):
    """
    Cached items to clean always have prefix "current" and are stored in chat_data
    """
    try:
        chat_data = get_chat_data(context)
        for k in chat_data.keys():
            if k.startswith("current"):
                chat_data.pop(k)

    except Exception as e:
        logger.warning(f"Error in clear_cache: {str(e)}")
