import asyncio
import json
import io
from random import randint

from .send import send_text_raw, send_text
from .roles import get_all_people, get_people
from .decorators import command
from .mylogging import get_time
from . import app
from . import settings


# MENU
INFO_LINES = [
    " - /database",
    # " - /bot_restart", # TODO
    " - /bot_down",
    " - /start_notification",
]


# Admin utils
async def send_to_superadmin(update, context, info):
    for user_id in get_people(context, "superadmin"):
        await send_text(update, context, info, user_id)


async def send_notification(update, context, notification_txt_id):
    all_users = get_all_people(context)
    await send_text_raw(update, context, "Mailing users...")
    for user_id in all_users:
        await asyncio.sleep(randint(1, 3))
        await send_text(update, context, notification_txt_id, user_id)
    await send_text_raw(update, context, "Mailing users done.")


@command(allowed_roles=("superadmin",))
async def superadmin(u, c):
    lines = [
        "🍑  SUPERADMIN MENU",
    ]
    lines += reversed(INFO_LINES)
    return await send_text_raw(u, c, "\n".join(lines))


@command(allowed_roles=("superadmin",))
async def start_notification(update, context):
    text_id = "start_notification"
    return await send_notification(update, context, text_id)


@command(allowed_roles=("superadmin",))
async def bot_down(update, context):
    text_id = "stop_notification"
    await send_notification(update, context, text_id)
    return await context.application.stop()


# @command(allowed_roles=("superadmin",))
# async def bot_restart(update, context):
#     await send_text_raw(update, context, "Stopping...")
#     await context.application.stop()
#     await context.application.initialize()
#     await send_text_raw(update, context, "Starting...")
#     await context.application.start()
#     await send_text_raw(update, context, "Success.")


@command(allowed_roles=("superadmin",))
async def database(update, context):
    time = get_time(True)
    for name, data in zip(
        ["bot", "chat", "user"],
        [
            app.application.bot_data,
            app.application.chat_data,
            app.application.user_data,
        ],
    ):
        data = dict(data)
        data_buffer = io.BytesIO()
        data_buffer.write(json.dumps(data, indent=4, default=str).encode())
        data_buffer.seek(0)
        # Send the files via telegram
        doc_stem= f"{settings.TG_BOT_NAME}_{name}_data_{time}.json"[:50]
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=data_buffer,
            filename=f"{doc_stem}.json",
        )
        data_buffer.close()
