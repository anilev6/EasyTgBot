from telegram import Update
from telegram.ext import CallbackContext

from .utils.context_logic import put_user_data, get_user_data


def register_user(update: Update, context: CallbackContext):
    put_user_data(context, "data_consent", True)


def is_user_registered(update: Update, context: CallbackContext):
    user_data = get_user_data(context)
    return user_data.get("data_consent")
