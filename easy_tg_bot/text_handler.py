from telegram.ext import (
    CallbackContext,
)

from .file_handler import FileHandler
from .validate_text_file import (
    get_text_dictionary,
    get_text_from_dict,
    get_text_and_parse_mode_from_dict,
    get_languages_from_dict,
    get_main_language_from_dict,
    validate_text_file,
)


# Const
TEXT_PREFIX = "text"


class TextFileHandler(FileHandler):
    def __init__(self):
        super().__init__(TEXT_PREFIX, get_text_dictionary, validate_text_file)

    # Language logic
    def get_languages(self, context: CallbackContext):
        return get_languages_from_dict(self.get_file_iterable(context))

    def get_main_language(self, context: CallbackContext):
        return get_main_language_from_dict(self.get_file_iterable(context))

    # User Language logic
    def assign_language_to_user(self, context, lan):
        context.user_data["lan"] = lan

    def get_user_language(self, context, user_id=None):
        if user_id is None:
            user_data = context.user_data
        else:
            user_data = context.application.user_data.get(int(user_id), {})

        return user_data.get("lan", self.get_main_language(context))

    # Get Text
    def get_text(self, context: CallbackContext, text_string_index: str, user_id=None):
        language = self.get_user_language(context, user_id)
        dic = self.get_file_iterable(context)
        return get_text_from_dict(language, dic, text_string_index)

    def get_text_and_parse_mode(self, context, text_string_index: str, user_id=None):
        language = self.get_user_language(context, user_id)
        dic = self.get_file_iterable(context)
        return get_text_and_parse_mode_from_dict(language, dic, text_string_index)


text_handler = TextFileHandler()
