# Telegram Offers Bot - Configuration
import os

# ===== TELEGRAM SETTINGS =====
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8576745210:AAFbIHw4OGVRHfzpRlxw0qXpVsf5_uu4eGA")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@QQXQQ8")

# Admin user IDs
ADMIN_IDS = [123456789]

# ===== SCRAPING SETTINGS =====
SCRAPE_INTERVAL = 60

# RSS Feed Sources - using reliable feeds
RSS_FEEDS = [
    {
        "name": "DealNews",
        "url": "https://www.dealnews.com/rss/todays-edition/",
        "category": "Top Deals"
    },
    {
        "name": "Slickdeals FP",
        "url": "https://slickdeals.net/newsearch.php?mode=frontpage&searcharea=deals&searchin=first&rss=1",
        "category": "Hot Deals"
    }
]

# ===== DATABASE =====
DATABASE_FILE = "offers.db"
