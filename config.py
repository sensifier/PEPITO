import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
AUTHORIZED_USERS = [int(id) for id in os.getenv('AUTHORIZED_USERS', '').split(',') if id]
AUTHORIZED_GROUPS = [int(id) for id in os.getenv('AUTHORIZED_GROUPS', '').split(',') if id]
GROUP_ADMINS = [int(id) for id in os.getenv('GROUP_ADMINS', '').split(',') if id]
MAIN_DEV = [int(id) for id in os.getenv('MAIN_DEV', '').split(',') if id]

# API Endpoints
SSE_URL = os.getenv('SSE_URL', 'https://api.thecatdoor.com/sse/v1/events')

# File Paths
DB_FILE = os.getenv('DB_FILE', 'pepito_bot.db')
IMAGES_DIR = os.getenv('IMAGES_DIR', 'images')

# Feature Flags
SHOW_NEGATIVE_PRICE_CHARTS = os.getenv('SHOW_NEGATIVE_PRICE_CHARTS', 'True').lower() == 'true'
SHOW_BTC_CHARTS = os.getenv('SHOW_BTC_CHARTS', 'True').lower() == 'true'

# Connection Settings
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '5'))
BACKOFF_FACTOR = float(os.getenv('BACKOFF_FACTOR', '0.2'))
RETRY_STATUSES = [500, 502, 503, 504]
STREAM_TIMEOUT = int(os.getenv('STREAM_TIMEOUT', '30'))
POLLING_TIMEOUT = int(os.getenv('POLLING_TIMEOUT', '20'))

# Chart Colors
CHART_COLORS = {
    'background': '#131722',
    'text': '#E0E3EB',
    'up': '#26A69A',
    'down': '#EF5350',
    'annotation': '#9598A1'
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'handlers': ['file', 'console']
}