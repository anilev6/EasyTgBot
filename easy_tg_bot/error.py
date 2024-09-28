import hashlib
from datetime import timedelta
from .mylogging import logger, get_time
from .superadmin import send_to_superadmin

# Whithin Telegram
async def error(update, context, cache={}, max_cache_size = 30, cooldown_minutes = 30) -> None:
    error_msg = "General error handler - "
    try:
        # No internet during polling or a webhook issue
        if not update:
            error_msg += f"no Update found"
        # For callback queries
        elif update.callback_query:
            error_msg += f"a callback error occurred: {context.error}"
            # await update.callback_query.answer(msg, show_alert=True)
        # For regular messages
        elif update.message:
            error_msg += f"a message error occurred: {context.error}"
            # await update.message.reply_text(msg)
        else:
            error_msg += f"Update\n'{update}'\n...caused error\n'{context.error}'"
    except Exception as e:
        error_msg += f"error in the bot: {e}"

    logger.error(error_msg)

    # Clear cache
    current_time = get_time()
    cooldown = timedelta(minutes=cooldown_minutes)
    cache = {
        key: timestamp
        for key, timestamp in cache.items()
        if current_time - timestamp <= cooldown
    }

    # If the cache becomes too large
    if len(cache) >= max_cache_size:
        logger.info(f"General error handler - the cache if full: {max_cache_size} errors")
        return

    error_hash = hashlib.md5(error_msg.encode()).hexdigest()
    if error_hash not in cache:
        cache[error_hash] = current_time  # Update the cache
        await maybe_notify_superadmin(update, context, error_msg)
        return
    else:
        return 

async def maybe_notify_superadmin(update, context, error_msg):
    try:
        await send_to_superadmin(update, context, error_msg[:2000])
    except Exception as e:
        logger.error(f"General error handler - error notifying superadmin about the error:\n{e}")
    return 
