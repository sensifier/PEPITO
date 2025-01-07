import logging
import requests
from datetime import datetime
from telebot import types
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import (
    AUTHORIZED_USERS, AUTHORIZED_GROUPS, GROUP_ADMINS, 
    MAIN_DEV, SHOW_BTC_CHARTS,
    MAX_RETRIES, BACKOFF_FACTOR, RETRY_STATUSES
)

from utils import (
    get_random_image, get_random_gif, format_duration, 
    get_status_text
)

from chart_generator import BitcoinChartGenerator

# Menu Keyboard Creation
def get_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    status_button = types.KeyboardButton('🐱 Check Status')
    start_button = types.KeyboardButton('🏠 Start')
    help_button = types.KeyboardButton('❓ Help')
    keyboard.add(start_button, help_button)
    keyboard.add(status_button)
    return keyboard

# Authorization Functions
def is_authorized(message):
    is_auth = (
        message.chat.id in AUTHORIZED_GROUPS or 
        message.from_user.id in AUTHORIZED_USERS
    )
    
    if not is_auth:
        notify_admin_of_unauthorized_access(message)
        bot.reply_to(
            message,
            "⚠️  Pépito's Tracking bot is not authorized for this chat.\n\n"
            "The bot administrator will been notified of your request.\n\n"
            "For immediate access, join the Telegram Community @PepitoTheCatcto.\n\n"
            "🐾🐾🐾  🐾🐾🐾  🐾🐾🐾  🐾🐾🐾"
        )
    return is_auth

def is_admin(user_id):
    return user_id in GROUP_ADMINS

def is_group_chat(message):
    return message.chat.type in ['group', 'supergroup']

def is_group_admin(user_id, chat_id):
    if chat_id not in AUTHORIZED_GROUPS:
        return False
    
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except Exception as e:
        logging.error(f"Error checking group admin status: {e}")
        return False

# Message Sending Functions
def send_telegram_photo_with_caption(bot, chat_id, photo_url, caption):
    try:
        img_response = requests.get(photo_url, timeout=10)
        img_response.raise_for_status()
        
        bot.send_photo(
            chat_id=chat_id,
            photo=img_response.content,
            caption=caption,
            parse_mode='HTML'
        )
        logging.info(f"Successfully sent photo to chat {chat_id}")
    except Exception as e:
        logging.error(f"Error sending photo: {e}")
        bot.send_message(
            chat_id=chat_id,
            text=f"{caption}\n\n⚠️ Image unavailable",
            parse_mode='HTML'
        )

def send_btc_chart(bot, chat_id, start_time, end_time, duration_str, event_type):
    if not SHOW_BTC_CHARTS:
        return

    try:
        chart_gen = BitcoinChartGenerator()
        img_bytes = chart_gen.create_chart_for_period(
            start_time, end_time, duration_str, event_type
        )
        
        if img_bytes:
            caption = (
                f"📊 <b>Pépito is Satoshi</b>\n\n"
                f"🐾🐾🐾  🐾🐾🐾  🐾🐾🐾\n\n"
                f"During Pépito's {'Indoor' if event_type == 'out' else 'Outdoor'} Adventure\n"
                f"Duration: {duration_str}"
            )
            
            bot.send_photo(
                chat_id=chat_id,
                photo=img_bytes,
                caption=caption,
                parse_mode='HTML'
            )
    except Exception as e:
        logging.error(f"Error sending BTC chart: {e}")

def notify_admin_of_unauthorized_access(bot, message):
    try:
        user = message.from_user
        chat = message.chat
        
        notification = (
            f"🚨 <b>Unauthorized Access Attempt</b>\n\n"
            f"<b>User Information:</b>\n"
            f"• ID: <code>{user.id}</code>\n"
            f"• Username: @{user.username if user.username else 'None'}\n"
            f"• Name: {user.first_name}"
            f"{f' {user.last_name}' if user.last_name else ''}\n\n"
            f"<b>Chat Information:</b>\n"
            f"• Chat ID: <code>{chat.id}</code>\n"
            f"• Chat Type: {chat.type}\n"
            f"• Chat Title: {chat.title if chat.type != 'private' else 'Private Chat'}\n\n"
            f"<b>Command Used:</b> {message.text}\n"
            f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        
        for admin_id in MAIN_DEV:
            try:
                bot.send_message(
                    admin_id,
                    notification,
                    parse_mode='HTML'
                )
            except Exception as e:
                logging.error(f"Failed to notify admin {admin_id}: {e}")
                
    except Exception as e:
        logging.error(f"Error in admin notification system: {e}")

def create_session():
    """Create requests session with retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=RETRY_STATUSES
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
