# Stuff to use
__version__ = "0.1.0"
from .app import telegram_bot_polling
from .mylogging import time_log_decorator, logger, get_time
from .decorators import command, button_callback, register_conversation_handler
from .admin import admin, ADMIN_MENU
from .text_handler import text_handler
from .send import send_text, send_keyboard, send_text_raw, send_keyboard_raw
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
from .utils.context_logic import (
    get_chat_data,
    put_chat_data,
    get_user_data,
    put_user_data,
    clear_cache,
)
from .send import send_video_from_file_id
from .roles import (
    role_required,
    check_role,
    DEFAULT_ADMIN_ROLES,
    DEFAULT_ALLOWED_ROLES,
    get_people_layout,
    get_people_role_group,
)
from .send_with_navigation import send_page_with_navigation, send_page_nav
# for adding the handlers on init automatically
from .manage_role_conv import ManageRoleConverstion
# Serverless lambda
from .app import lambda_handler
__version__ = "0.1.3"
from .decorators import message_handler
__version__ = "0.1.4"
from .app import application
from .settings import get_secret_by_name, default_roles
__version__ = "0.1.5"
# for adding the handlers on init automatically
from .mail_users_conv import message_mailing_conv_handler
from . import superadmin  # INFO_LINES for superadmin menu
from . import error
__version__ = "0.1.9"
from .send import send_message
__version__ = "0.2.1"  # bug fix
from .app import run_webhook_app
# TODO
# - limiter;
# - Forget user /forget_me; Delete user;
# - Hung convo bug - test
# - Connection error handler
# - Limiter
# - Replace 'nan' with None
# - Small Bug fix: Error in not_data_consent ?
# - Bug fix: None.log occasionally on run
# - /restart_me
# - optional number share
# - cache errors; cache messages;
