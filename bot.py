#!/usr/bin/env python3
"""
Telegram Offers Bot
"""

import logging
import os
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

from config import BOT_TOKEN, CHANNEL_ID, ADMIN_IDS, SCRAPE_INTERVAL, RSS_FEEDS
from database import init_db, save_offer, mark_as_sent, get_unsent_offers, get_stats, clear_database
from scrapers import fetch_all_rss_feeds

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = """
*Welcome to Offers Bot!*

Commands:
/latest - Show latest offers
/refresh - Update offers now
/stats - Statistics
/clear - Clear old offers
/help - Help
"""
    await update.message.reply_text(welcome, parse_mode='Markdown')


async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    offers = get_unsent_offers(5)
    if not offers:
        await update.message.reply_text("No offers available. Try /refresh first!")
        return
    for offer in offers:
        msg = format_offer(dict(offer))
        await update.message.reply_text(msg, parse_mode='Markdown', disable_web_page_preview=True)


async def refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fetching new offers...")
    
    try:
        new_count = scrape_and_save()
        await update.message.reply_text(f"Found {new_count} new offers!")
        
        if new_count > 0:
            await post_to_channel(context.application)
            await update.message.reply_text("Posted to channel!")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        logger.error(f"Refresh error: {e}")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_stats()
    msg = f"""
*Statistics*
Total: {stats['total']}
Posted: {stats['sent']}
Pending: {stats['pending']}
"""
    await update.message.reply_text(msg, parse_mode='Markdown')


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_database()
    await update.message.reply_text("Database cleared! Run /refresh to get new offers.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot fetches deals from various sources and posts them to your channel.")


def format_offer(offer: dict) -> str:
    title = offer.get('title', 'Deal')[:100]
    link = offer.get('link', '')
    source = offer.get('source', '')
    
    return f"""
*{title}*

Source: {source}
[View Deal]({link})
"""


def scrape_and_save() -> int:
    logger.info("Starting scrape...")
    offers = fetch_all_rss_feeds(RSS_FEEDS)
    logger.info(f"Got {len(offers)} offers from feeds")
    
    count = 0
    for offer in offers:
        if save_offer(offer['title'], offer['link'], offer.get('price'), offer.get('category'), offer.get('source')):
            count += 1
            logger.info(f"Saved: {offer['title'][:50]}...")
    
    logger.info(f"Saved {count} new offers")
    return count


async def post_to_channel(app: Application):
    offers = get_unsent_offers(5)
    for offer in offers:
        try:
            msg = format_offer(dict(offer))
            await app.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode='Markdown')
            mark_as_sent(offer['link'])
            logger.info(f"Posted: {offer['title'][:30]}...")
        except Exception as e:
            logger.error(f"Post error: {e}")


def main():
    print("Starting bot...")
    
    # Init DB
    init_db()
    
    # Initial scrape
    count = scrape_and_save()
    print(f"Initial scrape: {count} offers")
    
    # Create app
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("latest", latest_command))
    app.add_handler(CommandHandler("refresh", refresh_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("help", help_command))
    
    print("Bot running!")
    app.run_polling()


if __name__ == "__main__":
    main()
