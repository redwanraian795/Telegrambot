"""
Null safety utilities for the Telegram bot
Provides safe wrappers for common operations that might encounter None values
"""

from typing import Optional, Any, Dict, List
from telegram import Update
from telegram.ext import ContextTypes

def safe_get_user_id(update: Update) -> Optional[str]:
    """Safely get user ID from update"""
    if not update or not update.effective_user:
        return None
    return str(update.effective_user.id)

def safe_get_username(update: Update) -> str:
    """Safely get username with fallback"""
    if not update or not update.effective_user:
        return "unknown"
    return update.effective_user.username or "unknown"

def safe_get_first_name(update: Update) -> str:
    """Safely get first name with fallback"""
    if not update or not update.effective_user:
        return "User"
    return update.effective_user.first_name or "User"

def safe_get_message_text(update: Update) -> str:
    """Safely get message text with fallback"""
    if not update or not update.message or not update.message.text:
        return ""
    return update.message.text

def safe_reply_text(update: Update, text: str, **kwargs):
    """Safely reply to message"""
    if not update or not update.message:
        return None
    try:
        return update.message.reply_text(text, **kwargs)
    except Exception:
        return None

def safe_get_chat_id(update: Update) -> Optional[str]:
    """Safely get chat ID from update"""
    if not update or not update.effective_chat:
        return None
    return str(update.effective_chat.id)

def safe_get_photo(update: Update) -> Optional[Any]:
    """Safely get photo from message"""
    if not update or not update.message or not update.message.photo:
        return None
    return update.message.photo

def safe_get_video(update: Update) -> Optional[Any]:
    """Safely get video from message"""
    if not update or not update.message or not update.message.video:
        return None
    return update.message.video

def safe_get_document(update: Update) -> Optional[Any]:
    """Safely get document from message"""
    if not update or not update.message or not update.message.document:
        return None
    return update.message.document

def safe_get_audio(update: Update) -> Optional[Any]:
    """Safely get audio from message"""
    if not update or not update.message:
        return None
    return update.message.audio or update.message.voice

def safe_get_context_args(context: ContextTypes.DEFAULT_TYPE) -> List[str]:
    """Safely get context args with fallback"""
    if not context or not context.args:
        return []
    return context.args

def safe_dict_get(dictionary: Optional[Dict], key: str, default: Any = None) -> Any:
    """Safely get value from potentially None dictionary"""
    if not dictionary:
        return default
    return dictionary.get(key, default)

def safe_list_length(lst: Optional[List]) -> int:
    """Safely get length of potentially None list"""
    if not lst:
        return 0
    return len(lst)

def safe_list_access(lst: Optional[List], index: int, default: Any = None) -> Any:
    """Safely access list element by index"""
    if not lst or index >= len(lst) or index < 0:
        return default
    return lst[index]

def validate_update_and_user(update: Update) -> bool:
    """Validate that update and user are present"""
    return update is not None and update.effective_user is not None

# Export commonly used functions for easier import
safe_get = safe_dict_get
safe_user_info = safe_get_user_id
safe_message_text = safe_get_message_text

def validate_update_and_message(update: Update) -> bool:
    """Validate that update and message are present"""
    return update is not None and update.message is not None