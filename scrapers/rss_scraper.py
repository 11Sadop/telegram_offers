import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re


def scrape_almowafir():
    """سحب من الموفر - أكبر موقع كوبونات سعودي"""
    offers = []
    try:
        print("جاري السحب من الموفر...")
        url = "https://almowafir.com/ar/"
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'ar,en;q=0.9'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن الكوبونات
            items = soup.select('article, .store-card, .coupon-box, .deal-item')[:15]
            
            for item in items:
                title_el = item.select_one('h2, h3, h4, .title, .store-name')
                link_el = item.select_one('a[href]')
                discount_el = item.select_one('.discount, .percent, .off, .badge')
                
                if title_el:
                    title = clean_title(title_el.get_text(strip=True))
                    discount = discount_el.get_text(strip=True) if discount_el else ''
                    link = link_el.get('href', '') if link_el else ''
                    
                    if title and len(title) > 3:
                        full_title = f"{title}"
                        if discount and '%' in discount:
                            full_title = f"خصم {discount} - {title}"
                        
                        offers.append({
                            'title': full_title[:100],
                            'link': link if link.startswith('http') else f"https://almowafir.com{link}",
                            'price': discount,
                            'category': 'كوبونات',
                            'source': 'الموفر',
                            'date': datetime.now().isoformat()
                        })
            
            print(f"تم استخراج {len(offers)} من الموفر")
    except Exception as e:
        print(f"خطأ الموفر: {e}")
    return offers


def scrape_couponsaudi():
    """سحب من كوبون سعودي"""
    offers = []
    try:
        print("جاري السحب من كوبون سعودي...")
        urls = [
            "https://coupon.sa/",
            "https://www.alcoupon.com/ar-sa/stores/",
        ]
        
        for url in urls:
            try:
                response = requests.get(url, timeout=20, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
                })
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    items = soup.select('article, .store, .card, .coupon, .offer-box')[:10]
                    
                    for item in items:
                        title_el = item.select_one('h2, h3, h4, .title, .name, a[title]')
                        link_el = item.select_one('a[href]')
                        
                        if title_el:
                            title = title_el.get('title') or title_el.get_text(strip=True)
                            title = clean_title(title)
                            link = link_el.get('href', '') if link_el else ''
                            
                            if title and len(title) > 3 and 'http' not in title:
                                offers.append({
                                    'title': f"عرض {title}"[:100],
                                    'link': link if link.startswith('http') else url.rstrip('/') + link,
                                    'price': extract_price(title),
                                    'category': 'كوبونات',
                                    'source': 'كوبون سعودي',
                                    'date': datetime.now().isoformat()
                                })
            except:
                continue
        
        print(f"تم استخراج {len(offers)} من كوبون سعودي")
    except Exception as e:
        print(f"خطأ: {e}")
    return offers


def scrape_waffarha():
    """سحب من وفرها"""
    offers = []
    try:
        print("جاري السحب من وفرها...")
        response = requests.get("https://waffarha.com/", timeout=20, headers={
            'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('article, .deal, .offer, .product, .card')[:10]
            
            for item in items:
                title_el = item.select_one('h2, h3, .title, .name')
                link_el = item.select_one('a[href]')
                
                if title_el:
                    title = clean_title(title_el.get_text(strip=True))
                    link = link_el.get('href', '') if link_el else ''
                    
                    if title and len(title) > 5:
                        offers.append({
                            'title': title[:100],
                            'link': link,
                            'price': extract_price(title),
                            'category': 'عروض',
                            'source': 'وفرها',
                            'date': datetime.now().isoformat()
                        })
            
            print(f"تم استخراج {len(offers)} من وفرها")
    except Exception as e:
        print(f"خطأ وفرها: {e}")
    return offers


def extract_price(text: str) -> str:
    if not text:
        return ""
    patterns = [r'\d+%', r'\d+\s*(?:ريال|ر\.س|SAR)']
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()
    return ""


def clean_title(title: str) -> str:
    if not title:
        return ""
    title = re.sub(r'<[^>]+>', '', title)
    title = title.replace('*', '').replace('_', '').replace('[', '').replace(']', '')
    title = ' '.join(title.split())
    return title[:100] if title else ""


def fetch_rss_offers(feed_url: str, feed_name: str, category: str):
    """للتوافق - فارغ"""
    return []


def fetch_all_rss_feeds(feeds: list):
    """سحب كل العروض السعودية"""
    all_offers = []
    
    print("=" * 40)
    print("بدء سحب العروض السعودية...")
    print("=" * 40)
    
    # سحب من المواقع السعودية
    try:
        offers = scrape_almowafir()
        all_offers.extend(offers)
    except Exception as e:
        print(f"خطأ الموفر: {e}")
    
    try:
        offers = scrape_couponsaudi()
        all_offers.extend(offers)
    except Exception as e:
        print(f"خطأ كوبون: {e}")
    
    try:
        offers = scrape_waffarha()
        all_offers.extend(offers)
    except Exception as e:
        print(f"خطأ وفرها: {e}")
    
    print("=" * 40)
    print(f"إجمالي العروض: {len(all_offers)}")
    print("=" * 40)
    
    return all_offers


def fetch_webpage_offers(url: str, selectors: dict):
    return []
