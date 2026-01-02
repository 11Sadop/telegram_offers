#!/usr/bin/env python3
"""
Telegram Offers Bot - Automatically scrapes and posts deals
"""

import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue

from config import (
    BOT_TOKEN, CHANNEL_ID, ADMIN_IDS, 
    SCRAPE_INTERVAL, RSS_FEEDS
)
from database import init_db, save_offer, mark_as_sent, get_unsent_offers, get_stats
from scrapers import fetch_all_rss_feeds

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ============== BOT COMMANDS ==============

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
*Welcome to Offers Bot!*

I collect the best deals automatically from:
- Global stores (Amazon, Noon, AliExpress)
- Restaurants and cafes
- Games and apps

*Commands:*
/latest - Latest offers
/stats - Bot statistics
/refresh - Update offers now
/help - Help
"""
    
    keyboard = [[
        InlineKeyboardButton("Channel", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /latest command - show latest offers"""
    offers = get_unsent_offers(5)
    
    if not offers:
        await update.message.reply_text("No new offers available...")
        return
    
    for offer in offers:
        message = format_offer_message(dict(offer))
        await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - show bot statistics"""
    stats = get_stats()
    
    message = f"""
*Bot Statistics*

Total offers: {stats['total']}
Posted: {stats['sent']}
Pending: {stats['pending']}

Last update: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    await update.message.reply_text(message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
*How does the bot work?*

The bot:
1. Searches for offers every hour
2. Collects them from trusted sources
3. Posts them to the channel automatically

*Sources:*
- Slickdeals
- HotUKDeals  
- And more...
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /refresh command - manually trigger scraping"""
    await update.message.reply_text("Updating offers...")
    
    new_offers = scrape_and_save_offers()
    await post_offers_to_channel(context.application)
    
    await update.message.reply_text(f"Found {new_offers} new offers!")


# ============== SCRAPING & POSTING ==============

def format_offer_message(offer: dict) -> str:
    """Format an offer into a Telegram message"""
    title = offer.get('title', 'New Offer')[:100]
    title = title.replace('*', '').replace('_', '').replace('[', '').replace(']', '')
    
    return f"""
*{title}*

Price: {offer.get('price', 'See link') or 'See link'}
Category: {offer.get('category', 'Offers')}
Source: {offer.get('source', '')}

[Click for offer]({offer.get('link', '')})

{CHANNEL_ID}
"""


def scrape_and_save_offers() -> int:
    """Scrape offers from all sources and save to database"""
    logger.info("Starting to scrape offers...")
    
    offers = fetch_all_rss_feeds(RSS_FEEDS)
    
    new_count = 0
    for offer in offers:
        saved = save_offer(
            title=offer['title'],
            link=offer['link'],
            price=offer.get('price'),
            category=offer.get('category'),
            source=offer.get('source')
        )
        if saved:
            new_count += 1
    
    logger.info(f"Saved {new_count} new offers")
    return new_count


async def post_offers_to_channel(app: Application):
    """Post unsent offers to the channel"""
    offers = get_unsent_offers(5)
    
    if not offers:
        logger.info("No new offers to post")
        return
    
    for offer in offers:
        try:
            message = format_offer_message(dict(offer))
            await app.bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
            mark_as_sent(offer['link'])
            logger.info(f"Posted: {offer['title'][:50]}...")
        except Exception as e:
            logger.error(f"Error posting offer: {e}")


async def scheduled_scrape(context: ContextTypes.DEFAULT_TYPE):
    """Job that runs on schedule to scrape and post offers"""
    logger.info("Running scheduled scrape...")
    scrape_and_save_offers()
    await post_offers_to_channel(context.application)


# ============== MAIN ==============

def main():
    """Start the bot"""
    print("Telegram Offers Bot Starting...")
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Error: Please add bot token in config.py")
        return
    
    # Initialize database
    init_db()
    
    # Initial scrape
    logger.info("Running initial scrape...")
    scrape_and_save_offers()
    
    # Create application with job queue
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("latest", latest_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("refresh", refresh_command))
    
    # Schedule regular scraping if job_queue is available
    if app.job_queue:
        app.job_queue.run_repeating(
            scheduled_scrape,
            interval=SCRAPE_INTERVAL * 60,
            first=60
        )
        logger.info(f"Scheduled scraping every {SCRAPE_INTERVAL} minutes")
    else:
        logger.warning("Job queue not available, use /refresh to update manually")
    
    print("Bot is running!")
    
    # Run the bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
