import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re


def fetch_rss_offers(feed_url: str, feed_name: str, category: str):
    """Fetch offers from RSS feed"""
    offers = []
    try:
        print(f"جاري السحب من {feed_name}...")
        response = requests.get(feed_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code != 200:
            print(f"فشل السحب من {feed_name}: {response.status_code}")
            return offers
        
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('item')
        print(f"وجدت {len(items)} عنصر")
        
        for item in items[:15]:
            title_tag = item.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ''
            
            link_tag = item.find('link')
            link = ''
            if link_tag:
                link = link_tag.get_text(strip=True)
                if not link and link_tag.next_sibling:
                    link = str(link_tag.next_sibling).strip()
            
            title = clean_title(title)
            if title and link:
                offers.append({
                    'title': title,
                    'link': link,
                    'price': extract_price(title),
                    'category': category,
                    'source': feed_name,
                    'date': datetime.now().isoformat()
                })
        
        print(f"تم استخراج {len(offers)} عرض من {feed_name}")
    except Exception as e:
        print(f"خطأ في {feed_name}: {e}")
    return offers


def scrape_alcoupon():
    """سحب العروض من موقع الكوبون السعودي"""
    offers = []
    try:
        print("جاري السحب من الكوبون...")
        url = "https://www.alcoupon.com/ar-sa/"
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'ar,en;q=0.9'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find coupon cards
            cards = soup.select('.coupon-card, .deal-card, .offer-item, article')[:20]
            
            for card in cards:
                title_el = card.select_one('h2, h3, .title, .coupon-title')
                link_el = card.select_one('a')
                discount_el = card.select_one('.discount, .percent, .off')
                
                if title_el:
                    title = clean_title(title_el.get_text(strip=True))
                    link = link_el.get('href', '') if link_el else ''
                    discount = discount_el.get_text(strip=True) if discount_el else ''
                    
                    if title and len(title) > 5:
                        offers.append({
                            'title': f"{title} {discount}".strip(),
                            'link': link if link.startswith('http') else f"https://www.alcoupon.com{link}",
                            'price': discount,
                            'category': 'كوبونات',
                            'source': 'الكوبون',
                            'date': datetime.now().isoformat()
                        })
            
            print(f"تم استخراج {len(offers)} عرض من الكوبون")
    except Exception as e:
        print(f"خطأ في الكوبون: {e}")
    return offers


def scrape_coupon_sa():
    """سحب العروض من coupon.sa"""
    offers = []
    try:
        print("جاري السحب من coupon.sa...")
        url = "https://coupon.sa/"
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find offers
            items = soup.select('.coupon, .deal, .offer, article, .card')[:20]
            
            for item in items:
                title_el = item.select_one('h2, h3, h4, .title')
                link_el = item.select_one('a')
                
                if title_el:
                    title = clean_title(title_el.get_text(strip=True))
                    link = link_el.get('href', '') if link_el else ''
                    
                    if title and len(title) > 5:
                        offers.append({
                            'title': title,
                            'link': link if link.startswith('http') else f"https://coupon.sa{link}",
                            'price': extract_price(title),
                            'category': 'تخفيضات',
                            'source': 'كوبون السعودية',
                            'date': datetime.now().isoformat()
                        })
            
            print(f"تم استخراج {len(offers)} عرض من coupon.sa")
    except Exception as e:
        print(f"خطأ في coupon.sa: {e}")
    return offers


def scrape_otlob_coupon():
    """سحب من أطلب كوبون"""
    offers = []
    try:
        print("جاري السحب من أطلب كوبون...")
        url = "https://otlobcoupon.com/"
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('.coupon-item, .offer, article, .post')[:15]
            
            for item in items:
                title_el = item.select_one('h2, h3, .title, .entry-title')
                link_el = item.select_one('a')
                
                if title_el:
                    title = clean_title(title_el.get_text(strip=True))
                    link = link_el.get('href', '') if link_el else ''
                    
                    if title and len(title) > 5:
                        offers.append({
                            'title': title,
                            'link': link,
                            'price': extract_price(title),
                            'category': 'كوبونات',
                            'source': 'أطلب كوبون',
                            'date': datetime.now().isoformat()
                        })
            
            print(f"تم استخراج {len(offers)} من أطلب كوبون")
    except Exception as e:
        print(f"خطأ في أطلب كوبون: {e}")
    return offers


def extract_price(text: str) -> str:
    """استخراج السعر أو نسبة الخصم"""
    if not text:
        return ""
    patterns = [
        r'\d+%',  # نسبة مئوية
        r'\d+\s*(?:ريال|ر\.س|SAR)',  # ريال
        r'\$\d+',  # دولار
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()
    return ""


def clean_title(title: str) -> str:
    """تنظيف العنوان"""
    if not title:
        return ""
    title = re.sub(r'<[^>]+>', '', title)
    for char in ['*', '_', '`', '[', ']']:
        title = title.replace(char, '')
    title = ' '.join(title.split())
    if len(title) > 120:
        title = title[:117] + "..."
    return title


def fetch_all_rss_feeds(feeds: list):
    """سحب كل العروض"""
    all_offers = []
    
    # RSS feeds
    for feed in feeds:
        try:
            offers = fetch_rss_offers(feed['url'], feed['name'], feed['category'])
            all_offers.extend(offers)
        except Exception as e:
            print(f"خطأ: {e}")
    
    # Saudi coupon sites
    try:
        all_offers.extend(scrape_alcoupon())
    except Exception as e:
        print(f"خطأ الكوبون: {e}")
    
    try:
        all_offers.extend(scrape_coupon_sa())
    except Exception as e:
        print(f"خطأ coupon.sa: {e}")
    
    try:
        all_offers.extend(scrape_otlob_coupon())
    except Exception as e:
        print(f"خطأ أطلب كوبون: {e}")
    
    print(f"إجمالي العروض: {len(all_offers)}")
    return all_offers


def fetch_webpage_offers(url: str, selectors: dict):
    return []
