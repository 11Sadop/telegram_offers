# Telegram Offers Bot - Configuration
import os

# ===== TELEGRAM SETTINGS =====
# Get from environment variables (for deployment) or use defaults (for local)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8576745210:AAFbIHw4OGVRHfzpRlxw0qXpVsf5_uu4eGA")

# Your channel username (with @) or channel ID
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@QQXQQ8")

# Admin user IDs (can manage the bot)
ADMIN_IDS = [123456789]  # Replace with your Telegram user ID


# ===== SCRAPING SETTINGS =====
# How often to check for new deals (in minutes)
SCRAPE_INTERVAL = 60

# RSS Feed Sources
RSS_FEEDS = [
    {
        "name": "Slickdeals",
        "url": "https://slickdeals.net/newsearch.php?mode=frontpage&searcharea=deals&searchin=first&rss=1",
        "category": "Global Deals"
    },
    {
        "name": "HotUKDeals",
        "url": "https://www.hotukdeals.com/rss/hot",
        "category": "Hot Deals"
    }
]


# ===== DATABASE =====
DATABASE_FILE = "offers.db"


# ===== MESSAGE TEMPLATE =====
MESSAGE_TEMPLATE = """
*{title}*

Price: {price}
Category: {category}
Date: {date}

[View Offer]({link})

{CHANNEL_ID}
"""
