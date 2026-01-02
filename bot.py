#!/usr/bin/env python3
"""
بوت عروض تيليجرام - للسعودية
"""

import logging
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from config import BOT_TOKEN, CHANNEL_ID, ADMIN_IDS, RSS_FEEDS, MESSAGES
from database import init_db, save_offer, mark_as_sent, get_unsent_offers, get_stats, clear_database

# Setup logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# ============== COMMANDS ==============

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البداية"""
    await update.message.reply_text(MESSAGES["welcome"], parse_mode='Markdown')


async def offers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض آخر العروض"""
    offers = get_unsent_offers(5)
    if not offers:
        await update.message.reply_text(MESSAGES["no_offers"])
        return
    
    for offer in offers:
        await send_offer_message(update.message, dict(offer))


async def refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تحديث العروض"""
    await update.message.reply_text(MESSAGES["updating"])
    
    try:
        from scrapers import fetch_all_rss_feeds
        offers = fetch_all_rss_feeds(RSS_FEEDS)
        
        count = 0
        for offer in offers:
            if save_offer(offer['title'], offer['link'], offer.get('price'), offer.get('category'), offer.get('source'), offer.get('image_url'), offer.get('description')):
                count += 1
        
        if count > 0:
            await update.message.reply_text(MESSAGES["found_offers"].format(count=count))
            await post_to_channel(context.application)
        else:
            await update.message.reply_text(MESSAGES["no_new"])
    except Exception as e:
        logger.error(f"Refresh error: {e}")
        await update.message.reply_text(f"❌ خطأ: {e}")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إحصائيات البوت"""
    stats = get_stats()
    msg = f"""
📊 *إحصائيات البوت*

📦 إجمالي العروض: {stats['total']}
✅ تم نشرها: {stats['sent']}
⏳ في الانتظار: {stats['pending']}

🕐 آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    await update.message.reply_text(msg, parse_mode='Markdown')


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مسح العروض القديمة"""
    clear_database()
    await update.message.reply_text(MESSAGES["cleared"])


async def add_offer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إضافة عرض يدوياً"""
    user_id = update.effective_user.id
    
    if ADMIN_IDS and user_id not in ADMIN_IDS:
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    text = update.message.text
    # Remove command part
    for cmd in ['/اضافة', '/add', 'اضافة', 'add']:
        if text.startswith(cmd):
            text = text[len(cmd):].strip()
            break
    
    if not text:
        await update.message.reply_text(MESSAGES["add_format"], parse_mode='Markdown')
        return
    
    # Parse the offer
    lines = text.split('\n')
    if len(lines) < 2:
        await update.message.reply_text("❌ الرجاء إدخال العنوان والرابط على الأقل")
        return
    
    title = lines[0].strip()
    link = lines[1].strip() if len(lines) > 1 else ""
    category = lines[2].strip() if len(lines) > 2 else "عروض متنوعة"
    
    # Save the offer
    if save_offer(title, link, "", category, "يدوي"):
        await update.message.reply_text(MESSAGES["offer_added"])
        
        # Post to channel
        offer = {"title": title, "link": link, "category": category, "source": "يدوي"}
        await send_offer_to_chat(context.bot, CHANNEL_ID, offer)
        mark_as_sent(link)
        await update.message.reply_text(MESSAGES["posted"])
    else:
        await update.message.reply_text("❌ العرض موجود مسبقاً")


# ============== FORMATTING & SENDING ==============

def format_caption(offer: dict) -> str:
    """تنسيق نص العرض (Caption)"""
    title = offer.get('title', 'عرض جديد')[:100]
    link = offer.get('link', '')
    category = offer.get('category', 'عروض')
    source = offer.get('source', '')
    price = offer.get('price', '')
    description = offer.get('description', '')
    
    # Choose emoji
    emoji = "🎁"
    if 'مطاعم' in category or 'مطعم' in category: emoji = "🍔"
    elif 'بنك' in category or 'بطاق' in category: emoji = "💳"
    elif 'متجر' in category or 'تسوق' in category: emoji = "🛒"
    elif 'إلكترونيات' in category: emoji = "📱"
    if 'خصومات' in category: emoji = "🏷️"
    
    msg = f"{emoji} *{title}*\n\n"
    
    if description:
        msg += f"{description}\n\n"
        
    if price:
        msg += f"💰 السعر: {price}\n"
    
    msg += f"📂 التصنيف: {category}\n"
    if source:
        msg += f"📍 المصدر: {source}\n"
    
    msg += f"\n🔗 [اضغط الرابط للعرض]({link})\n"
    msg += f"\n{CHANNEL_ID}"
    
    return msg


async def send_offer_message(message_object, offer: dict):
    """إرسال العرض كرد على رسالة"""
    caption = format_caption(offer)
    image_url = offer.get('image_url')
    
    try:
        if image_url:
            await message_object.reply_photo(photo=image_url, caption=caption, parse_mode='Markdown')
        else:
            await message_object.reply_text(text=caption, parse_mode='Markdown', disable_web_page_preview=False)
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        await message_object.reply_text(text=caption, parse_mode='Markdown')


async def send_offer_to_chat(bot, chat_id, offer: dict):
    """إرسال العرض إلى شات محدد"""
    caption = format_caption(offer)
    image_url = offer.get('image_url')
    
    try:
        if image_url:
            await bot.send_photo(chat_id=chat_id, photo=image_url, caption=caption, parse_mode='Markdown')
        else:
            await bot.send_message(chat_id=chat_id, text=caption, parse_mode='Markdown', disable_web_page_preview=False)
    except Exception as e:
        logger.error(f"Error sending to chat: {e}")
        await bot.send_message(chat_id=chat_id, text=caption, parse_mode='Markdown')


async def post_to_channel(app: Application):
    """نشر العروض في القناة"""
    offers = get_unsent_offers(5)
    for offer in offers:
        try:
            await send_offer_to_chat(app.bot, CHANNEL_ID, dict(offer))
            mark_as_sent(offer['link'])
            logger.info(f"Posted: {offer['title'][:30]}...")
        except Exception as e:
            logger.error(f"Post error: {e}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة كافة النصوص"""
    text = update.message.text
    if not text: return

    # Check matches (with or without /)
    # Using 'in' is risky for "add" vs "added", so we check startsWith or equality
    t = text.lower().strip()
    
    if t.startswith('/'):
        t = t[1:]
        
    if t in ['عروض', 'latest', 'sh']:
        await offers_command(update, context)
    elif t in ['تحديث', 'refresh', 'update']:
        await refresh_command(update, context)
    elif t in ['احصائيات', 'stats']:
        await stats_command(update, context)
    elif t in ['مسح', 'clear']:
        await clear_command(update, context)
    elif t in ['مساعدة', 'help', 'start']:
        await start_command(update, context)
    elif t.startswith('اضافة') or t.startswith('add'):
        await add_offer_command(update, context)


# ============== MAIN ==============

def main():
    print("🚀 بوت العروض يعمل...")
    init_db()
    
    # Create App
    app = Application.builder().token(BOT_TOKEN).build()
    
    # 1. Add specific CommandHandlers for English (Standard)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", start_command))
    app.add_handler(CommandHandler("latest", offers_command))
    app.add_handler(CommandHandler("refresh", refresh_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("add", add_offer_command))

    # 2. Add Catch-All Text Handler (Handles everything else: Arabic, /Arabic, Typos, mixed)
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    
    print("✅ البوت جاهز!")
    app.run_polling()


if __name__ == "__main__":
    main()
