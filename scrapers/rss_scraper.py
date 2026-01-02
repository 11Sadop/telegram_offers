import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re


def scrape_almowafir_deals():
    """سحب العروض الفعلية من الموفر"""
    offers = []
    try:
        print("جاري السحب من الموفر...")
        # صفحة العروض والكوبونات
        url = "https://almowafir.com/ar/coupons/"
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'Accept-Language': 'ar,en;q=0.9'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن الكوبونات الفعلية
            coupons = soup.select('.coupon-card, .deal-card, .offer-box, [class*="coupon"], [class*="deal"]')[:20]
            
            for coupon in coupons:
                # البحث عن نص الخصم
                discount_el = coupon.select_one('[class*="discount"], [class*="percent"], .badge, .off')
                title_el = coupon.select_one('h3, h4, .title, .description, p')
                link_el = coupon.select_one('a[href*="coupon"], a[href*="deal"], a.btn')
                store_el = coupon.select_one('.store-name, .brand, img[alt]')
                
                discount = ""
                if discount_el:
                    discount = discount_el.get_text(strip=True)
                
                # استخراج النسبة من أي مكان
                all_text = coupon.get_text()
                percent_match = re.search(r'(\d+)\s*%', all_text)
                if percent_match:
                    discount = f"{percent_match.group(1)}%"
                
                if discount and '%' in discount:
                    store = ""
                    if store_el:
                        store = store_el.get('alt', '') or store_el.get_text(strip=True)
                    
                    title = f"خصم {discount}"
                    if store:
                        title = f"خصم {discount} من {store}"
                    
                    link = ""
                    if link_el:
                        link = link_el.get('href', '')
                    
                    if title:
                        offers.append({
                            'title': clean_title(title),
                            'link': link if link.startswith('http') else f"https://almowafir.com{link}",
                            'price': discount,
                            'category': 'خصومات',
                            'source': 'الموفر',
                            'date': datetime.now().isoformat()
                        })
            
            print(f"تم استخراج {len(offers)} عرض من الموفر")
    except Exception as e:
        print(f"خطأ الموفر: {e}")
    return offers


def scrape_noon_deals():
    """سحب عروض نون السعودية"""
    offers = []
    try:
        print("جاري السحب من نون...")
        url = "https://www.noon.com/saudi-ar/offers/"
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن المنتجات
            products = soup.select('[class*="product"], [class*="item"], article')[:15]
            
            for prod in products:
                title_el = prod.select_one('[class*="title"], [class*="name"], h3, h4')
                price_el = prod.select_one('[class*="price"], [class*="now"]')
                old_price = prod.select_one('[class*="was"], [class*="old"], del, s')
                link_el = prod.select_one('a[href]')
                
                if title_el and old_price:
                    title = clean_title(title_el.get_text(strip=True))
                    price = price_el.get_text(strip=True) if price_el else ""
                    link = link_el.get('href', '') if link_el else ""
                    
                    if title and len(title) > 5:
                        offers.append({
                            'title': f"عرض نون: {title[:60]}",
                            'link': link if link.startswith('http') else f"https://noon.com{link}",
                            'price': price,
                            'category': 'تخفيضات',
                            'source': 'نون',
                            'date': datetime.now().isoformat()
                        })
            
            print(f"تم استخراج {len(offers)} من نون")
    except Exception as e:
        print(f"خطأ نون: {e}")
    return offers


def scrape_extra_deals():
    """سحب عروض اكسترا"""
    offers = []
    try:
        print("جاري السحب من اكسترا...")
        url = "https://www.extra.com/ar-sa/offers"
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            products = soup.select('.product, .item, article, [class*="product"]')[:15]
            
            for prod in products:
                title_el = prod.select_one('.title, .name, h3, h4, a[title]')
                price_el = prod.select_one('.price, [class*="price"]')
                link_el = prod.select_one('a[href]')
                
                if title_el:
                    title = title_el.get('title') or title_el.get_text(strip=True)
                    title = clean_title(title)
                    price = price_el.get_text(strip=True) if price_el else ""
                    link = link_el.get('href', '') if link_el else ""
                    
                    if title and len(title) > 5:
                        offers.append({
                            'title': f"عرض اكسترا: {title[:60]}",
                            'link': link if link.startswith('http') else f"https://extra.com{link}",
                            'price': price,
                            'category': 'إلكترونيات',
                            'source': 'اكسترا',
                            'date': datetime.now().isoformat()
                        })
            
            print(f"تم استخراج {len(offers)} من اكسترا")
    except Exception as e:
        print(f"خطأ اكسترا: {e}")
    return offers


def scrape_sample_offers():
    """عروض تجريبية للتأكد من عمل البوت"""
    print("إضافة عروض تجريبية...")
    return [
        {
            'title': 'خصم 30% على جميع المشروبات من ستاربكس',
            'link': 'https://starbucks.sa/',
            'price': '30%',
            'category': 'مطاعم',
            'source': 'ستاربكس',
            'date': datetime.now().isoformat()
        },
        {
            'title': 'كاش باك 15% مع بطاقات الراجحي على أمازون',
            'link': 'https://amazon.sa/',
            'price': '15%',
            'category': 'بنوك',
            'source': 'الراجحي',
            'date': datetime.now().isoformat()
        },
        {
            'title': 'خصم 50% على الوجبات من هنقرستيشن',
            'link': 'https://hungerstation.com/',
            'price': '50%',
            'category': 'توصيل',
            'source': 'هنقرستيشن',
            'date': datetime.now().isoformat()
        },
        {
            'title': 'توصيل مجاني من نون على الطلبات فوق 100 ريال',
            'link': 'https://noon.com/',
            'price': 'مجاني',
            'category': 'تسوق',
            'source': 'نون',
            'date': datetime.now().isoformat()
        },
        {
            'title': 'عرض الجمعة: خصم 40% على الأزياء من شي ان',
            'link': 'https://shein.com/',
            'price': '40%',
            'category': 'أزياء',
            'source': 'شي ان',
            'date': datetime.now().isoformat()
        }
    ]


def clean_title(title: str) -> str:
    if not title:
        return ""
    title = re.sub(r'<[^>]+>', '', title)
    title = title.replace('*', '').replace('_', '').replace('[', '').replace(']', '')
    title = ' '.join(title.split())
    return title[:100] if title else ""


def extract_price(text: str) -> str:
    if not text:
        return ""
    patterns = [r'\d+%', r'\d+\s*(?:ريال|ر\.س|SAR)']
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()
    return ""


def fetch_rss_offers(feed_url: str, feed_name: str, category: str):
    return []


def fetch_all_rss_feeds(feeds: list):
    """سحب كل العروض"""
    all_offers = []
    
    print("=" * 40)
    print("🔍 بدء سحب العروض...")
    print("=" * 40)
    
    # سحب من المواقع
    try:
        all_offers.extend(scrape_almowafir_deals())
    except:
        pass
    
    try:
        all_offers.extend(scrape_noon_deals())
    except:
        pass
    
    try:
        all_offers.extend(scrape_extra_deals())
    except:
        pass
    
    # إذا ما فيه عروض، نضيف عروض تجريبية
    if len(all_offers) < 3:
        print("⚠️ عروض قليلة، إضافة عروض تجريبية...")
        all_offers.extend(scrape_sample_offers())
    
    print("=" * 40)
    print(f"✅ إجمالي العروض: {len(all_offers)}")
    print("=" * 40)
    
    return all_offers


def fetch_webpage_offers(url: str, selectors: dict):
    return []
