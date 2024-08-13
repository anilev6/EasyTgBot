from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)

from .roles import DEFAULT_ADMIN_ROLES, check_role, add_role, is_bot_closed, close_bot_for_users, open_bot_for_users, get_people_layout
from .admin import admin
from .text_handler import text_handler
from .utils.utils import get_keyboard, get_info_from_query
from .send import send_keyboard, send_text
from .send_with_navigation import send_page_with_navigation
from .mylogging import logger
from .decorators import register_conversation_handler, button_callback


class ManageRoleConverstion:
    def __init__(
        self, prefix, role, main_func = lambda context, user_id: None):
        self.prefix = prefix
        self.role = role
        self.main_func = main_func
        self.restrict_function = lambda u, c: check_role(c, DEFAULT_ADMIN_ROLES)
        self.ADD_ID = 0
        self.entry_point = f"{prefix}_{role}"
        self.bot_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(self.start_conversation, pattern=fr"^{self.entry_point}$")
        ],
        states={
            self.ADD_ID: [
                MessageHandler(filters.TEXT, self.handle_message),
            ]
        },
        fallbacks=[
            CallbackQueryHandler(
                self.cancel, pattern=r"^cancel$"
            ),
        ],
        name=self.entry_point,
        persistent=True
    )

    async def cancel(self, update: Update, context: CallbackContext):
        # Answer callback
        if update:
            query = update.callback_query
            if query:
                await query.answer()

        # Check role
        if not self.restrict_function(update, context):
            return ConversationHandler.END

        await admin_manage_users_button(update, context)
        return ConversationHandler.END

    async def start_conversation(self, update: Update, context: CallbackContext):
        # Answer callback
        if update:
            query = update.callback_query
            if query:
                await query.answer()

        # Check role
        if not self.restrict_function(update, context):
            return ConversationHandler.END

        keyboard = get_keyboard(context, back_button_callback="cancel")
        await send_keyboard(update, context, keyboard, f"{self.entry_point}_text")

        return self.ADD_ID

    async def handle_message(self, update: Update, context: CallbackContext) -> int:
        if not self.restrict_function(update, context):
            return ConversationHandler.END

        message = update.message.text
        ids = [i.strip() for i in message.split(",")]

        # validate id
        try:
            validation_result = [int(user_id) for user_id in ids]
        except Exception:
            await send_text(update, context, "id_must_be_a_number")
            return await self.start_conversation(update, context)

        results = []
        for user_id in ids:
            # can't change superadmins role
            if check_role(context, ("superadmin",), user_id):
                pass

            else:
                try:
                    result = self.main_func(context, user_id)
                    results.append(result)
                    logger.info(f"Success {self.entry_point}")
                except Exception as e:
                    results.append(None)
                    logger.error(f"Fail {self.entry_point}")

        if not all(results):
            await send_text(update, context, f"{self.entry_point}_fail")
            return await self.start_conversation(update, context)
        else:
            await send_text(update, context, f"{self.entry_point}_success")
            return await self.cancel(update, context)


admin_convo_handlers = [
    ManageRoleConverstion("add", "admin", lambda c, u_id: add_role(c, "admin", u_id)),
    ManageRoleConverstion("add", "user", lambda c, u_id: add_role(c, "user", u_id)),
    ManageRoleConverstion("del", "user", lambda c, u_id: add_role(c, "banned", u_id)),
]
for h in admin_convo_handlers:
    register_conversation_handler(h.bot_handler)


@button_callback(allowed_roles = DEFAULT_ADMIN_ROLES)
async def admin_manage_users_button(update, context):
    # menu
    buttons = []

    # Open/close bot
    if is_bot_closed(context):
        b_text = text_handler.get_text(context, "open_bot")
    else:
        b_text = text_handler.get_text(context, "close_bot")

    buttons += [
        [
            InlineKeyboardButton(
                b_text,
                callback_data="open_close_bot",
            )
        ]
    ]

    # Get users
    buttons += [
        [
            InlineKeyboardButton(
                text_handler.get_text(context, "get_users_by_role_menu"),
                callback_data="get_users_by_role_menu",
            )
        ]
    ]

    # crud users
    options = {
        text_handler.get_text(context, h.entry_point): h.entry_point
        for h in admin_convo_handlers
    }
    buttons += [
        [
            InlineKeyboardButton(
                option_name,
                callback_data=option,
            )
        ]
        for option_name, option in options.items()
    ]

    # TODO forget users

    # back
    buttons += [
        [
            InlineKeyboardButton(
                text_handler.get_text(context, "back_button"),
                callback_data="admin_cancel",
            )
        ]
    ]

    keyboard = InlineKeyboardMarkup(buttons)
    return await send_keyboard(update, context, keyboard, "admin_manage_users_header")


@button_callback(allowed_roles=DEFAULT_ADMIN_ROLES)
async def admin_cancel(update, context):
    return await admin(update, context)


@button_callback(allowed_roles = DEFAULT_ADMIN_ROLES)
async def open_close_bot(update, context):
    if is_bot_closed(context):
        open_bot_for_users(context)
        await send_text(update, context, "bot_opened")
        logger.info("Bot has been opened")
    else:
        close_bot_for_users(context)
        await send_text(update, context, "bot_closed")
        logger.info("Bot has been closed")

    return await admin_manage_users_button(update, context)


@button_callback(allowed_roles = DEFAULT_ADMIN_ROLES)
async def get_users_by_role_menu(update, context):
    prefix = "admin_get_users"
    options = ("admin", "user", "banned")
    buttons = []

    # List options
    buttons += [
        [
            InlineKeyboardButton(
                text_handler.get_text(context, f"{prefix}_{option}"),
                callback_data=f"{prefix}_{option}",
            )
        ]
        for option in options
    ]

    # Go back
    buttons += [
        [
            InlineKeyboardButton(
                text_handler.get_text(
                    context,
                    text_string_index="back_button",
                ),
                callback_data="admin_manage_users_button",
            )
        ]
    ]
    return await send_keyboard(
        update, context, InlineKeyboardMarkup(buttons), "admin_get_users_header"
    )


@button_callback(allowed_roles = DEFAULT_ADMIN_ROLES)
async def admin_get_users(update, context):
    role = await get_info_from_query(update, "admin_get_users")
    return await send_page_with_navigation(
        update,
        context,
        lines_header=f"admin_get_users_header_{role}",
        get_lines_func=lambda context: get_people_layout(context, role),
        lines_to_text_func=lambda l: "\n\n".join(l),
        callback_func=get_users_by_role_menu,
        clear_cache = True
    )
