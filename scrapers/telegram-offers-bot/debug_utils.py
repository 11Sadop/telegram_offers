
async def debug_scrape_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Debug command to test scrapers one by one"""
    await update.message.reply_text("🕵️ جاري فحص المصادر... انتظر")
    
    results = []
    
    # Test 1: Ilofo
    try:
        from scrapers.rss_scraper import scrape_ilofo_deals
        ilofo = scrape_ilofo_deals()
        results.append(f"✅ Ilofo: Found {len(ilofo)}")
    except Exception as e:
        results.append(f"❌ Ilofo Error: {e}")

    # Test 2: Cobone
    try:
        from scrapers.rss_scraper import scrape_cobone_deals
        cobone = scrape_cobone_deals()
        results.append(f"✅ Cobone: Found {len(cobone)}")
    except Exception as e:
        results.append(f"❌ Cobone Error: {e}")

    await update.message.reply_text("\n".join(results))
