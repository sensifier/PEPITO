# Pépito Bot 🐈‍⬛ (REDACTED... 🐾🐾🐾)

## **Bot available for interaction at:**
 - **'[PepitoCTO Group on Telegram](https://t.me/PepitoTheCatcto)'**
 - **'[Pepito Bot on Telegram](https://t.me/Pepito_IO_Bot)'**

A Telegram bot that tracks Pépito's adventures, providing real-time updates about his comings and goings, along with Bitcoin price analysis during his adventures.

## Features
- 🏠 Real-time tracking of Pépito's location (indoor/outdoor)
- 📊 Bitcoin price analysis during Pépito's adventures
- 🖼️ Random memes and GIFs
- 📈 Duration statistics and activity tracking

## Setup

### Prerequisites
- Python 3.8 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Access to the Cat Door API @[Pepito-API-Repo](https://github.com/Clement87/Pepito-API)

### Installation (beta...)

1. Clone the repository:
```bash
git clone https://github.com/sensifier/PEPITO.git
cd pepito-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```env
BOT_TOKEN=your_bot_token_here
AUTHORIZED_USERS=user_id1,user_id2
.
.
.
SSE_URL=your_sse_url
```

5. Create an `images` directory for memes and GIFs:
```bash
mkdir images
```

### Running the Bot

```bash
python main.py
```

## Project Structure
```
pepito-bot/
├── main.py                # Main application entry point
├── config.py              # Configuration and constants
├── bot_handlers.py        # Core bot functionality
├── command_handlers.py    # Command implementations
├── database.py           # Database operations
├── utils.py              # Utility functions
├── chart_generator.py    # Bitcoin chart generation
├── requirements.txt      # Dependencies
├── .env                 # Environment variables (not in git)
├── .gitignore          # Git ignore file
├── images/             # Directory for memes/GIFs (not in git)
└── README.md           # This file
```

## Commands
- `/status` - Check Pépito's current location
- `/meme` - Get a random Pépito meme
- `/stats` - View activity statistics
- `/satoshi` - View Bitcoin price during Pépito's current adventure
- And many more!

## Admin Commands
...
- `/announce` - Send announcement
- `/gif` - Send random GIF

## Contributing
Feel free to submit issues and enhancement requests!

## License
[Apache 2.0 License](https://github.com/sensifier/PEPITO/blob/main/LICENSE)
