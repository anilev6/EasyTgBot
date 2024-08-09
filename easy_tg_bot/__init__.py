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
from .roles import role_required, check_role, DEFAULT_ADMIN_ROLES, DEFAULT_ALLOWED_ROLES, get_people_layout
# for adding the handlers on init automatically
from .manage_role_conv import ManageRoleConverstion
from .send_with_navigation import send_page_with_navigation, send_page_nav

# TODO
# - Test adding a language (only to a user for example)

# - Dockerfile, .dockerignore
# - update the version without stopping (/superadmin command?)
# - Web-hooks
# - Deploy ?
# - update the deployed version without stopping (/superadmin command?)

# - Mailing service
# - Forget user /forget_me; Delete user;
# - /superadmin /get_bd
# - Error handling
# - Log errors and warnings to superadmin
# - Superadmin commands
# - Replace 'nan' with None
# - Small Bug fix: Error in not_data_consent ?
# - Validate text file more
