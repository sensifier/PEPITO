import requests
import logging
from datetime import datetime, timezone
from database import DatabaseManager
from utils import get_random_image, get_random_gif, format_duration, get_status_text
from bot_handlers import (
    is_authorized, is_admin, is_group_chat, is_group_admin,
    send_telegram_photo_with_caption, send_btc_chart, get_menu_keyboard
)

def register_handlers(bot):
    """Register all command handlers with the bot"""

    # Basic Commands
    @bot.message_handler(commands=["start", "start_pepito"])
    def start(message):
        if not is_authorized(message):
            return
        
        if is_group_chat(message):
            welcome_msg = (
                "🐱 Pépito Bot is now active in this group!\n\n"
                "Available commands (view more in /help):\n"
                "• /status - Check Pépito's current status\n"
                "• /last_seen - Check Pépito's last activity\n"
                "• /help - Show available commands"
            )
        else:
            welcome_msg = (
                "Welcome to Pépito Bot! 🐱\n\n"
                "Available commands (view more in /help):\n"
                "• /status - Check Pépito's status\n"
                "• /last_seen - Check Pépito's last activity\n"
                "• /help - Show all commands\n\n"
                "You can also use the menu button below!"
            )
        
        markup = get_menu_keyboard() if not is_group_chat(message) else None
        bot.send_message(message.chat.id, welcome_msg, reply_markup=markup)

    @bot.message_handler(commands=["help", "help_pepito"])
    def help_command(message):
        if not is_authorized(message):
            return
        
        if is_group_chat(message):
            help_text = (
                "📋 <b>Group Commands</b>\n\n"
                "• /status - Check Pépito's current status\n"
                "• /last_seen - Pépito's last activity\n"
                "• /meme - Get a random Pépito meme\n"
                "• /pepito - Status with a Pepito meme\n"
                "• /satoshi - Bitcoin price chart\n"
                "• /PEPILLIONS | $PEPILLIONS\n"
                "• /PepitoTheGreat\n"
                "• /pepitoissatoshi\n"
                "• /PEPITO_IS_SATOSHI\n"
                "• $PEPITO_IS_SATOSHI\n"
                "• /SweetPepito | $SweetPepito\n"
                "• ... and more!\n\n"
                "• /help - Show this help message"
            )
        else:
            help_text = (
                "📋 <b>Available Commands</b>\n\n"
                "• /status - Check Pépito's status\n"
                "• /last_seen - Pépito's last activity\n"
                "• /meme - Get a random Pépito meme\n"
                "• /pepito - Status with a Pepito meme\n"
                "• /satoshi - Bitcoin price chart\n"
                "• /PEPILLIONS | $PEPILLIONS\n"
                "• /PepitoTheGreat\n"
                "• /pepitoissatoshi\n"
                "• /PEPITO_IS_SATOSHI\n"
                "• $PEPITO_IS_SATOSHI\n"
                "• /SweetPepito | $SweetPepito\n"
                "• ... and more!\n\n"
                "• /help - Show this help message"
            )
            
            if is_admin(message.from_user.id):
                help_text += (
                    "\n🔧 <b>Admin Commands</b>\n"
                    "• /addgroup [id] - Authorize a group\n"
                    "• /removegroup [id] - Remove group authorization\n"
                    "• /listgroups - List authorized groups\n"
                    "• /gif - Send random GIF\n"
                    "• /announce - Send announcement\n"
                )
        
        bot.send_message(message.chat.id, help_text, parse_mode='HTML')

    @bot.message_handler(commands=["status"])
    def status_command(message):
        if not is_authorized(message):
            return
        
        try:
            last_in = DatabaseManager.get_last_event("in")
            last_out = DatabaseManager.get_last_event("out")
            
            if not last_in and not last_out:
                bot.reply_to(message, "No recorded activity for Pépito yet.")
                return

            last_event = last_in if not last_out or (last_in and last_in[2] > last_out[2]) else last_out
            event_type = "in" if last_event == last_in else "out"
            time_str = datetime.fromtimestamp(last_event[2]).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            caption = (
                f"😸 <b>Pépito Status Update:</b>\n"
                f"🐈‍⬛🐈‍⬛🐈‍⬛   🐈‍⬛🐈‍⬛🐈‍⬛   🐈‍⬛🐈‍⬛🐈‍⬛\n\n"
                f"Currently: <b>{'Inside 🏠' if event_type == 'in' else 'Outside 🌳'}</b>\n\n"
                f"Since: {time_str}"
            )
            
            send_telegram_photo_with_caption(bot, message.chat.id, last_event[3], caption)
        except Exception as e:
            logging.error(f"Error in status command: {e}")
            bot.reply_to(message, "Failed to get status.")

    # Stats and Bitcoin Commands
    @bot.message_handler(commands=["stats", "statistics"])
    def stats_command(message):
        if not is_authorized(message):
            return
            
        try:
            stats = DatabaseManager.get_location_stats()
            stats_text = get_status_text(
                stats.get('current_location'),
                stats.get('current_duration'),
                stats.get('last_transition_duration')
            )
            
            caption = (
                f"🐾 <b>Pépito's Recent Activity</b> 🐾\n\n"
                f"🐈‍⬛🐈‍⬛🐈‍⬛   🐈‍⬛🐈‍⬛🐈‍⬛   🐈‍⬛🐈‍⬛🐈‍⬛\n\n"
                f"{stats_text}"
            )
            
            last_event = DatabaseManager.get_last_event(stats.get('current_location'))
            if last_event:
                send_telegram_photo_with_caption(bot, message.chat.id, last_event[3], caption)
            else:
                bot.send_message(message.chat.id, caption, parse_mode='HTML')
        except Exception as e:
            logging.error(f"Error in stats command: {e}")
            bot.reply_to(message, "Failed to get statistics.")

    @bot.message_handler(commands=["satoshi", "SATOSHI", "btc", "BTC"])
    def satoshi_command(message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        if not is_admin(user_id) and not is_group_admin(user_id, chat_id):
            return

        try:
            last_event = DatabaseManager.get_last_event(None)  # Get most recent event
            if not last_event:
                bot.reply_to(message, "No recorded activity for Pépito yet.")
                return
            
            current_time = int(datetime.now(timezone.utc).timestamp())
            duration = current_time - last_event[2]
            duration_str = f"{duration // 3600}h {(duration % 3600) // 60}m"
            
            loading_msg = bot.reply_to(
                message,
                "🔄 Generating Bitcoin price chart..."
            )
            
            try:
                send_btc_chart(bot, message.chat.id, last_event[2], current_time, 
                             duration_str, last_event[1])
            except Exception as e:
                bot.reply_to(message, "Failed to generate chart.")
            finally:
                try:
                    bot.delete_message(message.chat.id, loading_msg.message_id)
                except:
                    pass
                    
        except Exception as e:
            logging.error(f"Error in satoshi command: {e}")
            bot.reply_to(message, "Failed to process request.")

    # Meme and GIF Commands
    @bot.message_handler(commands=["meme", "pepito", "PEPITO", "Pepito"])
    def meme_command(message):
        if not is_authorized(message):
            return
            
        image_path = get_random_image()
        if not image_path:
            bot.reply_to(message, "😿 No images available.")
            return
            
        try:
            stats = DatabaseManager.get_location_stats()
            current_location = stats.get('current_location', 'unknown')
            time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            
            caption = (
                f"😸 <b>Pépito's Current Situation:</b>\n\n"
                f"🐾🐾🐾  🐾🐾🐾  🐾🐾🐾\n\n"
                f"Status: <b>{'Inside 🏠' if current_location == 'in' else 'Outside 🌳'}</b>\n\n"
                f"Time: {time_str}\n\n"
            )
            
            with open(image_path, 'rb') as photo:
                if image_path.lower().endswith('.gif'):
                    bot.send_animation(
                        message.chat.id,
                        photo,
                        caption=caption,
                        parse_mode='HTML'
                    )
                else:
                    bot.send_photo(
                        message.chat.id,
                        photo,
                        caption=caption,
                        parse_mode='HTML'
                    )
        except Exception as e:
            logging.error(f"Error in meme command: {e}")
            bot.reply_to(message, "Failed to send meme.")

    @bot.message_handler(commands=["gif", "GIF"])
    def gif_command(message):
        if not is_admin(message.from_user.id):
            return
            
        image_path = get_random_gif()
        if not image_path:
            bot.reply_to(message, "😿 No GIFs available.")
            return
            
        try:
            with open(image_path, 'rb') as gif:
                bot.send_animation(
                    message.chat.id,
                    gif,
                    caption="🐱 Pépito GIF!",
                    parse_mode='HTML'
                )
        except Exception as e:
            logging.error(f"Error in gif command: {e}")
            bot.reply_to(message, "Failed to send GIF.")

    # Menu Button Handlers
    @bot.message_handler(func=lambda message: message.text == '🐱 Check Status')
    def menu_status(message):
        status_command(message)

    @bot.message_handler(func=lambda message: message.text == '🏠 Start')
    def menu_start(message):
        start(message)

    @bot.message_handler(func=lambda message: message.text == '❓ Help')
    def menu_help(message):
        help_command(message)

    return bot
