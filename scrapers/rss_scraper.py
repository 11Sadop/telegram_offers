import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re


def clean_title(title: str) -> str:
    if not title:
        return ""
    title = re.sub(r'<[^>]+>', '', title)
    title = title.replace('*', '').replace('_', '').replace('[', '').replace(']', '')
    title = ' '.join(title.split())
    return title[:100] if title else ""


# ============================================
# 1. عروض المطاعم والكوفيهات
# ============================================

def scrape_restaurant_offers():
    """سحب عروض المطاعم والكوفيهات"""
    offers = []
    print("🍔 جاري سحب عروض المطاعم...")
    
    # مصدر 1: كوبون
    try:
        urls = [
            "https://www.cobone.com/ar/deals/riyadh/food-dining",
            "https://www.cobone.com/ar/deals/jeddah/food-dining"
        ]
        for url in urls:
            response = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                deals = soup.select('.deal-box, .deal_item, .card')[:8]
                for deal in deals:
                    title_el = deal.select_one('.title, h3, h2, h4')
                    img_el = deal.select_one('img')
                    link_el = deal.select_one('a')
                    if title_el:
                        offers.append({
                            'title': clean_title(title_el.get_text(strip=True)),
                            'link': link_el.get('href', '') if link_el else url,
                            'price': 'عرض مطاعم',
                            'category': 'مطاعم',
                            'source': 'كوبون',
                            'image_url': img_el.get('src', '') if img_el else '',
                            'description': 'عرض مطاعم مميز من كوبون',
                            'date': datetime.now().isoformat()
                        })
    except Exception as e:
        print(f"خطأ كوبون: {e}")
    
    print(f"✅ عروض المطاعم: {len(offers)}")
    return offers


# ============================================
# 2. عروض تطبيقات التوصيل
# ============================================

def scrape_delivery_apps():
    """كوبونات تطبيقات التوصيل"""
    offers = []
    print("🛵 جاري سحب كوبونات التوصيل...")
    
    apps = [
        ("هنقرستيشن", "hungerstation"),
        ("تويو", "toyou"),
        ("جاهز", "jahez"),
        ("مرسول", "mrsool"),
        ("نون فود", "noon-food"),
        ("طلبات", "talabat"),
    ]
    
    for app_name, app_slug in apps:
        try:
            url = f"https://almowafir.com/ar/stores/{app_slug}/"
            resp = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # البحث عن أي كوبون
                codes = soup.select('[class*="coupon"], [class*="code"], .offer-card')[:2]
                for code in codes:
                    text = code.get_text(strip=True)[:80]
                    offers.append({
                        'title': f'كوبون {app_name}: {text}',
                        'link': url,
                        'price': 'كود خصم',
                        'category': 'توصيل',
                        'source': app_name,
                        'image_url': '',
                        'description': f'استخدم هذا الكوبون للحصول على خصم في تطبيق {app_name}',
                        'date': datetime.now().isoformat()
                    })
        except:
            continue
    
    print(f"✅ كوبونات التوصيل: {len(offers)}")
    return offers


# ============================================
# 3. عروض بطاقات البنوك
# ============================================

def scrape_bank_offers():
    """عروض البطاقات البنكية"""
    offers = []
    print("💳 جاري سحب عروض البنوك...")
    
    banks = [
        ("الراجحي", "alrajhi-bank"),
        ("الأهلي", "ncb"),
        ("الإنماء", "alinma-bank"),
        ("STC Pay", "stc-pay"),
    ]
    
    for bank_name, bank_slug in banks:
        try:
            url = f"https://almowafir.com/ar/stores/{bank_slug}/"
            resp = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                deals = soup.select('[class*="offer"], [class*="deal"], .card')[:2]
                for deal in deals:
                    text = deal.get_text(strip=True)[:80]
                    if text:
                        offers.append({
                            'title': f'عرض {bank_name}: {text}',
                            'link': url,
                            'price': 'كاش باك',
                            'category': 'بنوك',
                            'source': bank_name,
                            'image_url': '',
                            'description': f'عرض خاص لحاملي بطاقات {bank_name}',
                            'date': datetime.now().isoformat()
                        })
        except:
            continue
    
    print(f"✅ عروض البنوك: {len(offers)}")
    return offers


# ============================================
# 4. عروض المواقع العالمية (أمازون، نون، علي اكسبرس)
# ============================================

def scrape_global_sites():
    """عروض المواقع العالمية"""
    offers = []
    print("🌍 جاري سحب عروض المواقع العالمية...")
    
    sites = [
        ("أمازون", "amazon-sa", "https://almowafir.com/ar/stores/amazon-sa/"),
        ("نون", "noon", "https://almowafir.com/ar/stores/noon/"),
        ("علي اكسبرس", "aliexpress", "https://almowafir.com/ar/stores/aliexpress/"),
        ("شي إن", "shein", "https://almowafir.com/ar/stores/shein/"),
        ("نمشي", "namshi", "https://almowafir.com/ar/stores/namshi/"),
    ]
    
    for site_name, site_slug, url in sites:
        try:
            resp = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # البحث عن الكوبونات والعروض
                items = soup.select('[class*="coupon"], [class*="offer"], [class*="deal"]')[:3]
                for item in items:
                    text = item.get_text(strip=True)[:80]
                    # البحث عن نسبة الخصم
                    percent = re.search(r'(\d+)\s*%', text)
                    price = f"{percent.group(1)}%" if percent else "خصم"
                    
                    if text and len(text) > 5:
                        offers.append({
                            'title': f'{site_name}: {text}',
                            'link': url,
                            'price': price,
                            'category': 'تسوق',
                            'source': site_name,
                            'image_url': '',
                            'description': f'كوبون خصم فعال على موقع {site_name}',
                            'date': datetime.now().isoformat()
                        })
        except:
            continue
    
    print(f"✅ عروض المواقع العالمية: {len(offers)}")
    return offers


# ============================================
# 5. عروض الموفر العامة
# ============================================

def scrape_almowafir_deals():
    """أفضل العروض من الموفر"""
    offers = []
    print("🏷️ جاري سحب عروض الموفر...")
    
    try:
        url = "https://almowafir.com/ar/coupons/"
        resp = requests.get(url, timeout=20, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept-Language': 'ar'
        })
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            items = soup.select('[class*="coupon"], [class*="deal"], .card')[:10]
            for item in items:
                title = item.get_text(strip=True)[:80]
                link = item.select_one('a')
                img = item.select_one('img')
                percent = re.search(r'(\d+)\s*%', title)
                
                if title and len(title) > 10:
                    offers.append({
                        'title': clean_title(title),
                        'link': link.get('href', '') if link else url,
                        'price': f"{percent.group(1)}%" if percent else "خصم",
                        'category': 'كوبونات',
                        'source': 'الموفر',
                        'image_url': img.get('src', '') if img else '',
                        'description': 'كوبون خصم فعال من الموفر',
                        'date': datetime.now().isoformat()
                    })
    except Exception as e:
        print(f"خطأ الموفر: {e}")
    
    print(f"✅ عروض الموفر: {len(offers)}")
    return offers


# ============================================
# الدالة الرئيسية
# ============================================

def fetch_all_rss_feeds(feeds: list):
    """سحب كل العروض"""
    all_offers = []
    
    print("=" * 50)
    print("🚀 بدء سحب العروض الشاملة...")
    print("=" * 50)
    
    # 1. مطاعم وكوفيهات
    try:
        all_offers.extend(scrape_restaurant_offers())
    except: pass
    
    # 2. تطبيقات التوصيل
    try:
        all_offers.extend(scrape_delivery_apps())
    except: pass
    
    # 3. عروض البنوك
    try:
        all_offers.extend(scrape_bank_offers())
    except: pass
    
    # 4. المواقع العالمية
    try:
        all_offers.extend(scrape_global_sites())
    except: pass
    
    # 5. الموفر
    try:
        all_offers.extend(scrape_almowafir_deals())
    except: pass
    
    print("=" * 50)
    print(f"✅ إجمالي العروض: {len(all_offers)}")
    print("=" * 50)
    
    return all_offers


# دوال مطلوبة للتوافق
def fetch_rss_offers(feed_url: str, feed_name: str, category: str):
    return []

def fetch_webpage_offers(url: str, selectors: dict):
    return []
