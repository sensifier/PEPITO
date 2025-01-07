import requests
import os
import logging
from pathlib import Path
from datetime import datetime
from config import IMAGES_DIR

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pepito_bot.log'),
            logging.StreamHandler()
        ]
    )

def calculate_time_parts(seconds):
    """Calculate days, hours, minutes from seconds."""
    days = seconds // (24 * 3600)
    remaining = seconds % (24 * 3600)
    hours = remaining // 3600
    remaining %= 3600
    minutes = remaining // 60
    seconds = remaining % 60
    return days, hours, minutes, seconds

def format_duration(seconds):
    """Format duration with adaptive detail level."""
    if seconds < 0:
        return "just now"
        
    days, hours, minutes, secs = calculate_time_parts(seconds)
    parts = []
    
    if days > 0:
        parts.append(f"{int(days)} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{int(hours)} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{int(minutes)} minute{'s' if minutes != 1 else ''}")
    if secs > 0 and not parts:
        parts.append(f"{int(secs)} second{'s' if secs != 1 else ''}")
        
    if not parts:
        return "just now"
        
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    else:
        return f"{', '.join(parts[:-1])}, and {parts[-1]}"

def ensure_image_directory():
    """Ensure the images directory exists."""
    Path(IMAGES_DIR).mkdir(exist_ok=True)
    return os.path.isdir(IMAGES_DIR)


def get_random_image(gif_only=False):
    """Get a random image from the images directory."""
    try:
        logging.info(f"Checking images directory: {IMAGES_DIR}")
        
        if not os.path.exists(IMAGES_DIR):
            logging.error(f"Images directory {IMAGES_DIR} not found")
            return None

        if gif_only:
            extensions = ['.gif']
        else:
            extensions = ['.png', '.jpg', '.jpeg', '.gif']

        logging.info(f"Looking for images with extensions: {extensions}")

        images = [
            f for f in os.listdir(IMAGES_DIR) 
            if any(f.lower().endswith(ext) for ext in extensions)
        ]

        logging.info(f"Found {len(images)} images in directory")
        
        if not images:
            logging.error("No images found in images directory")
            return None

        selected_image = random.choice(images)
        logging.info(f"Selected image: {selected_image}")
        return os.path.join(IMAGES_DIR, selected_image)
    except Exception as e:
        logging.error(f"Error getting random image: {e}")
        return None


def get_random_gif():
    """Get a random GIF from the images directory"""
    try:
        if not os.path.exists(IMAGES_DIR):
            logging.error(f"Images directory {IMAGES_DIR} not found")
            return None

        images = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.gif',))]
        if not images:
            logging.error("No GIF images found in images directory")
            return None
            
        random_image = random.choice(images)
        return os.path.join(IMAGES_DIR, random_image)
    except Exception as e:
        logging.error(f"Error getting random GIF: {e}")
        return None

def get_status_text(current_location, current_duration, last_transition):
    """Generate formatted status text."""
    status = []
    
    if current_location == 'in':
        status.append("🏠 <strong>Pépito is currently INSIDE</strong>")
    else:
        status.append("🌳 <strong>Pépito is currently OUTSIDE</strong>")
        
    if current_duration:
        status.append(f"\n<b>Duration:</b> <i>{format_duration(current_duration)}</i>")
        
    if last_transition:
        status.append(
            f"\n<b>Last {'Outdoor' if current_location == 'in' else 'Indoor'} "
            f"duration:</b> <i>{format_duration(last_transition)}</i>"
        )
        
    return "\n".join(status)
