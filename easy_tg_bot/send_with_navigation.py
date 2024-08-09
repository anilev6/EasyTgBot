from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import math

from .roles import role_required
from .decorators import button_callback
from .utils.context_logic import put_chat_data, get_chat_data
from .utils.utils import clear_cache
from .text_handler import text_handler
from .send import send_keyboard_raw


@role_required()
async def send_page_with_navigation(
    update,
    context,
    user_id=None,
    **kwargs,
):
    """
    GENERAL
    {
        "page": kwargs.get("start_page", 0),
        "per_page": kwargs.get("per_page", 5),
        "lines_header": kwargs.get("lines_header", ""),
        "get_lines_func": kwargs.get("get_lines_func", None),
        "callback_func": kwargs.get("callback_func", None),
        "clear_cache": kwargs.get("clear_cache", False)
    }

    TEXT
    {
        "lines_to_text_func": kwargs.get("lines_to_text_func"),
    }
    """
    prepare_navigation(context, **kwargs, user_id=user_id)
    return await send_page_nav(update, context, user_id)


def prepare_navigation(context, **kwargs):
    user_id = kwargs.pop("user_id", None)
    for key, value in kwargs.items():
        put_chat_data(context, f"current_{key}", value, user_id)


@role_required()
async def send_page_nav(update, context, user_id=None):
    """Triggers simple page refresh"""
    chat_data = get_chat_data(context, user_id)
    page = chat_data.get("current_page", 0)
    per_page = chat_data.get("current_per_page", 5)
    lines_header_index = chat_data.get("current_lines_header", "")
    lines = chat_data.get("current_get_lines_func", lambda c: [])(context)
    # TODO if not lines
    max_page = math.ceil(len(lines)/per_page)
    count = f"{page+1}/{max_page}" if max_page else "0/0"
    header = (
        text_handler.get_text(context, lines_header_index)
        + " "
        + count
    )

    start = page * per_page
    end = start + per_page

    small_list = [header] + lines[start:end]

    text_func = chat_data.get("current_lines_to_text_func")
    if text_func:
        text = text_func(small_list)
        buttons = get_navigation_buttons(context, page, per_page, lines)
        return await send_keyboard_raw(
            update, context, InlineKeyboardMarkup(buttons), text, user_id=user_id
        )
    # TODO else


# Navigation buttons
def get_navigation_buttons(context, page, per_page, lines):
    amount_items = len(lines)

    # general
    buttons = []

    # navigation
    navigation_buttons = []

    if page >= 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                "◀️",
                callback_data="previous_page",
            )
        )

    max_page = math.ceil(amount_items / per_page)
    if page + 1 < max_page:
        navigation_buttons.append(
            InlineKeyboardButton(
                "▶️",
                callback_data="next_page",
            )
        )

    if navigation_buttons:
        buttons.append(navigation_buttons)

    # back
    buttons.append(
        [
            InlineKeyboardButton(
                text_handler.get_text(context, "back_button"),
                callback_data="exit_navigation",
            )
        ]
    )
    return buttons


@button_callback()
async def next_page(update, context):
    chat_data = get_chat_data(context)
    page = chat_data.get("current_page", 0)
    put_chat_data(context, "current_page", page + 1)
    return await send_page_nav(update, context)


@button_callback()
async def previous_page(update, context):
    chat_data = get_chat_data(context)
    page = chat_data.get("current_page", 1)
    put_chat_data(context, "current_page", page - 1)
    return await send_page_nav(update, context)


@button_callback()
async def exit_navigation(update, context, user_id=None):
    chat_data = get_chat_data(context, user_id)
    callback_func = chat_data.pop("current_callback_func", None)
    clear_cache_flag = chat_data.pop("current_clear_cache", False)
    if clear_cache_flag:
        clear_cache(context)
    if callback_func:
        return await callback_func(update, context)
    # TODO else
