import json
import threading
import requests
import logging
import time
import queue
from telebot import TeleBot
from config import (
    BOT_TOKEN, MAX_RETRIES, BACKOFF_FACTOR, 
    STREAM_TIMEOUT, POLLING_TIMEOUT, SSE_URL
)
from database import DatabaseManager
from utils import setup_logging, ensure_image_directory
from bot_handlers import create_session
from command_handlers import register_handlers

def listen_to_sse(event_queue, session):
    """Enhanced SSE listener with connection pooling"""
    while True:
        try:
            logging.info("Connecting to SSE stream...")
            with session.get(SSE_URL, stream=True, timeout=STREAM_TIMEOUT) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        try:
                            line = line.decode("utf-8").lstrip("data: ").strip()
                            data = json.loads(line)
                            
                            if data.get("event") == "pepito":
                                event_queue.put(data)
                        except json.JSONDecodeError as e:
                            logging.error(f"JSON parsing error: {e}")
                            continue
                            
        except Exception as e:
            logging.error(f"SSE connection error: {e}")
            time.sleep(BACKOFF_FACTOR * 2)

def process_events(bot, event_queue):
    """Process events from queue with Bitcoin chart integration"""
    while True:
        try:
            data = event_queue.get()
            event_type = data["type"]
            event_time = data["time"]
            img_url = data["img"]
            
            if DatabaseManager.log_event(event_type, event_time, img_url):
                # Get previous event for duration calculation
                prev_event = DatabaseManager.get_previous_opposite_event(event_type, event_time)
                
                time_str = datetime.utcfromtimestamp(event_time).strftime('%Y-%m-%d %H:%M:%S UTC')
                duration_str = None
                
                if prev_event:
                    duration = event_time - prev_event[2]
                    duration_str = f"{duration // 3600}h {(duration % 3600) // 60}m"
                
                for chat_id in AUTHORIZED_USERS + AUTHORIZED_GROUPS:
                    try:
                        # Send status update with duration info if available
                        caption = get_status_caption(chat_id, event_type, time_str, duration_str)
                        send_telegram_photo_with_caption(bot, chat_id, img_url, caption)
                        
                        # Send Bitcoin chart if we have duration data
                        if prev_event and SHOW_BTC_CHARTS:
                            send_btc_chart(
                                bot, chat_id,
                                prev_event[2],
                                event_time,
                                duration_str,
                                event_type
                            )
                    except Exception as e:
                        logging.error(f"Error sending update to {chat_id}: {e}")
        except Exception as e:
            logging.error(f"Error processing event: {e}")
        finally:
            event_queue.task_done()

def main():
    # Setup logging
    setup_logging()
    logging.info("Starting Pépito Bot...")
    
    # Ensure required directories exist
    if not ensure_image_directory():
        logging.critical("Failed to create images directory")
        return
    
    # Initialize database
    if not DatabaseManager.init_db():
        logging.critical("Failed to initialize database")
        return
    
    try:
        # Initialize bot
        bot = TeleBot(BOT_TOKEN)
        bot.timeout = POLLING_TIMEOUT
        
        # Register command handlers
        bot = register_handlers(bot)
        
        # Initialize event queue and session
        event_queue = queue.Queue()
        session = create_session()
        
        # Start SSE listener thread
        sse_thread = threading.Thread(
            target=listen_to_sse,
            args=(event_queue, session),
            daemon=True
        )
        sse_thread.start()
        logging.info("SSE listener started")
        
        # Start event processor thread
        processor_thread = threading.Thread(
            target=process_events,
            args=(bot, event_queue),
            daemon=True
        )
        processor_thread.start()
        logging.info("Event processor started")
        
        # Start bot with automatic restart
        logging.info("Bot is ready! Starting polling...")
        while True:
            try:
                bot.polling(non_stop=True, interval=1)
            except Exception as e:
                logging.error(f"Bot polling error: {e}")
                time.sleep(BACKOFF_FACTOR)
                continue
                
    except Exception as e:
        logging.critical(f"Critical error: {e}")
        return

if __name__ == "__main__":
    main()
