import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
import json


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', str(text))
    text = ' '.join(text.split())
    return text[:200]


def fetch_all_rss_feeds(feeds: list):
    """سحب كل العروض الحقيقية"""
    all_offers = []
    
    print("=" * 50)
    print("🚀 سحب الكوبونات الحقيقية...")
    print("=" * 50)
    
    # 1. كوبونات الموفر
    try:
        offers = scrape_almowafir()
        all_offers.extend(offers)
        print(f"✅ الموفر: {len(offers)}")
    except Exception as e:
        print(f"❌ الموفر: {e}")
    
    # 2. كوبون سعودي
    try:
        offers = scrape_couponsaudi()
        all_offers.extend(offers)
        print(f"✅ كوبون سعودي: {len(offers)}")
    except Exception as e:
        print(f"❌ كوبون سعودي: {e}")
    
    # 3. كوبون عربي
    try:
        offers = scrape_couponarabi()
        all_offers.extend(offers)
        print(f"✅ كوبون عربي: {len(offers)}")
    except Exception as e:
        print(f"❌ كوبون عربي: {e}")
    
    print("=" * 50)
    print(f"✅ إجمالي: {len(all_offers)}")
    
    return all_offers


def scrape_almowafir():
    """سحب كوبونات حقيقية من الموفر"""
    offers = []
    
    # صفحات المتاجر المشهورة
    stores = [
        ("noon", "نون"),
        ("amazon-sa", "أمازون"),
        ("shein", "شي إن"),
        ("namshi", "نمشي"),
        ("hungerstation", "هنقرستيشن"),
        ("jahez", "جاهز"),
        ("talabat", "طلبات"),
        ("aliexpress", "علي اكسبرس"),
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
        'Accept-Language': 'ar-SA,ar;q=0.9',
        'Accept': 'text/html,application/xhtml+xml'
    }
    
    for slug, name in stores:
        try:
            url = f"https://almowafir.com/ar/stores/{slug}/"
            resp = requests.get(url, headers=headers, timeout=15)
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # البحث عن الكوبونات
                # الموفر يستخدم data attributes للكودات
                coupons = soup.find_all(['div', 'section'], class_=lambda x: x and ('coupon' in x.lower() or 'offer' in x.lower()))
                
                for coupon in coupons[:3]:
                    # محاولة استخراج الكود
                    code = None
                    
                    # 1. من data attribute
                    code = coupon.get('data-code') or coupon.get('data-coupon')
                    
                    # 2. من عنصر داخلي
                    if not code:
                        code_el = coupon.find(class_=lambda x: x and 'code' in x.lower())
                        if code_el:
                            code = code_el.get_text(strip=True)
                    
                    # 3. من input
                    if not code:
                        code_input = coupon.find('input', {'type': 'text'})
                        if code_input:
                            code = code_input.get('value')
                    
                    # استخراج الوصف
                    desc_el = coupon.find(['h3', 'h4', 'p', 'span'], class_=lambda x: x and ('title' in str(x).lower() or 'desc' in str(x).lower()))
                    desc = desc_el.get_text(strip=True) if desc_el else ""
                    
                    # استخراج نسبة الخصم
                    text = coupon.get_text()
                    percent = re.search(r'(\d+)\s*%', text)
                    discount = f"{percent.group(1)}%" if percent else "خصم"
                    
                    if code or desc:
                        offers.append({
                            'title': f"كوبون {name}: {clean_text(desc)[:50]}" if desc else f"كوبون {name}",
                            'link': url,
                            'price': code if code else discount,
                            'category': 'كوبونات',
                            'source': name,
                            'image_url': '',
                            'description': f"""🎫 *كوبون {name}*

💰 الكود: *{code if code else 'اضغط للحصول على الكود'}*
📊 الخصم: {discount}

✅ طريقة الاستخدام:
1. انسخ الكود
2. اذهب للموقع
3. الصق الكود عند الدفع

🔗 رابط الموقع: {url}""",
                            'date': datetime.now().isoformat()
                        })
                        
        except Exception as e:
            print(f"  خطأ {name}: {e}")
            continue
    
    return offers


def scrape_couponsaudi():
    """سحب من موقع كوبون سعودي"""
    offers = []
    
    try:
        url = "https://www.couponsaudi.com/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # البحث عن بطاقات الكوبونات
            cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(k in str(x).lower() for k in ['coupon', 'deal', 'offer', 'card']))
            
            for card in cards[:10]:
                title = card.find(['h2', 'h3', 'h4'])
                link = card.find('a')
                
                # البحث عن الكود
                code_el = card.find(class_=lambda x: x and 'code' in str(x).lower())
                code = code_el.get_text(strip=True) if code_el else None
                
                # البحث عن الخصم
                text = card.get_text()
                percent = re.search(r'(\d+)\s*%', text)
                
                if title:
                    title_text = clean_text(title.get_text())
                    offers.append({
                        'title': title_text,
                        'link': link.get('href', url) if link else url,
                        'price': code if code else (f"{percent.group(1)}%" if percent else "خصم"),
                        'category': 'كوبونات',
                        'source': 'كوبون سعودي',
                        'image_url': '',
                        'description': f"🎫 {title_text}\n\n{'📋 الكود: ' + code if code else ''}\n\n✅ كوبون فعال من كوبون سعودي",
                        'date': datetime.now().isoformat()
                    })
    except Exception as e:
        print(f"خطأ كوبون سعودي: {e}")
    
    return offers


def scrape_couponarabi():
    """سحب من مواقع الكوبونات العربية"""
    offers = []
    
    sites = [
        "https://www.coupon.ae/ar/",
        "https://www.alcoupon.com/ar/",
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ar'}
    
    for site_url in sites:
        try:
            resp = requests.get(site_url, headers=headers, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # البطاقات
                cards = soup.find_all(['div', 'article'], limit=20)
                
                for card in cards:
                    # فلترة البطاقات ذات الصلة
                    text = card.get_text().lower()
                    if not any(k in text for k in ['خصم', 'كوبون', 'كود', '%', 'offer', 'discount']):
                        continue
                    
                    title = card.find(['h2', 'h3', 'h4', 'a'])
                    if not title:
                        continue
                        
                    title_text = clean_text(title.get_text())
                    if len(title_text) < 5:
                        continue
                    
                    # الخصم
                    percent = re.search(r'(\d+)\s*%', card.get_text())
                    
                    # الكود
                    code = None
                    code_el = card.find(attrs={'data-clipboard-text': True})
                    if code_el:
                        code = code_el.get('data-clipboard-text')
                    
                    link = card.find('a')
                    
                    offers.append({
                        'title': title_text[:60],
                        'link': link.get('href', site_url) if link else site_url,
                        'price': code if code else (f"{percent.group(1)}%" if percent else "خصم"),
                        'category': 'كوبونات',
                        'source': 'كوبون عربي',
                        'image_url': '',
                        'description': f"🎫 {title_text}\n\n✅ كوبون فعال",
                        'date': datetime.now().isoformat()
                    })
                    
                    if len(offers) >= 5:
                        break
                        
        except Exception as e:
            print(f"خطأ {site_url}: {e}")
            continue
    
    return offers


def fetch_rss_offers(feed_url: str, feed_name: str, category: str):
    return []

def fetch_webpage_offers(url: str, selectors: dict):
    return []
