from telegram import Update
from telegram.ext import CallbackContext


def register_user(update: Update, context: CallbackContext):
    context.user_data["data_consent"] = True


def is_user_registered(update: Update, context: CallbackContext):
    return context.user_data.get("data_consent")
