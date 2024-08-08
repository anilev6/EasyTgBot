# Stuff to use
__version__ = "0.1.0"
from .app import telegram_bot_polling
from .mylogging import time_log_decorator, logger
from .decorators import command, button_callback, register_conversation_handler
from .admin import admin, ADMIN_MENU
from .text_handler import text_handler
from .send import send_text, send_keyboard
from .utils.utils import (
    get_keyboard,
    get_info_from_query,
    end_conversation,
)
from .validate_text_file import clear_table_element
from .file_handler import FileHandler
from .video_handler import VideoFileHandler
# for adding the handlers on init automatically
from .start import start_conv_handler
from .put_file_conv import PutFileConversation
from .put_intro_video_conv import PutVideoConversation
__version__ = "0.1.1"
from .utils.context_logic import get_chat_data, put_chat_data, get_user_data, put_user_data, clear_cache
from .send import send_video_from_file_id

# TODO
# - add admin/user
# - mailing service
# - Dockerfile
# - Web-hooks
# - Replace 'nan' with None
# - in text.xlsx divide texts into sheets by the roles, where user is the most general
# - Small Bug fix: Error in not_data_consent ?
# - Validate text file more
