import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re


def scrape_almowafir_deals():
    """سحب العروض الفعلية من الموفر مع الصور"""
    offers = []
    try:
        print("جاري السحب من الموفر...")
        url = "https://almowafir.com/ar/coupons/"
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'Accept-Language': 'ar,en;q=0.9'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            coupons = soup.select('.coupon-card, .deal-card, .offer-box, [class*="coupon"], [class*="deal"]')[:20]
            
            for coupon in coupons:
                discount_el = coupon.select_one('[class*="discount"], [class*="percent"], .badge, .off')
                title_el = coupon.select_one('h3, h4, .title, .description, p')
                link_el = coupon.select_one('a[href*="coupon"], a[href*="deal"], a.btn')
                store_el = coupon.select_one('.store-name, .brand, img[alt]')
                image_el = coupon.select_one('img[src]')
                
                discount = ""
                if discount_el:
                    discount = discount_el.get_text(strip=True)
                
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
                    
                    image_url = ""
                    if image_el:
                        image_url = image_el.get('src', '')
                        if image_url and not image_url.startswith('http'):
                             image_url = f"https://almowafir.com{image_url}"

                    if title:
                        offers.append({
                            'title': clean_title(title),
                            'link': link if link.startswith('http') else f"https://almowafir.com{link}",
                            'price': discount,
                            'category': 'كوبونات',
                            'source': 'الموفر',
                            'image_url': image_url,
                            'description': f"كوبون خصم {discount} فعال على {store}. انسخ الكود واستخدمه عند الدفع.",
                            'date': datetime.now().isoformat()
                        })
            print(f"تم استخراج {len(offers)} عرض من الموفر")
    except Exception as e:
        print(f"خطأ الموفر: {e}")
    return offers


def scrape_noon_deals():
    """سحب عروض نون السعودية مع الصور"""
    offers = []
    try:
        print("جاري السحب من نون...")
        url = "https://www.noon.com/saudi-ar/offers/"
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            products = soup.select('[class*="product"], [class*="item"], article')[:15]
            
            for prod in products:
                title_el = prod.select_one('[class*="title"], [class*="name"], h3, h4')
                price_el = prod.select_one('[class*="price"], [class*="now"]')
                old_price = prod.select_one('[class*="was"], [class*="old"], del, s')
                link_el = prod.select_one('a[href]')
                image_el = prod.select_one('img[src]')
                
                if title_el and old_price:
                    title = clean_title(title_el.get_text(strip=True))
                    price = price_el.get_text(strip=True) if price_el else ""
                    link = link_el.get('href', '') if link_el else ""
                    image_url = ""
                    if image_el:
                         image_url = image_el.get('src', '')
                    
                    if title and len(title) > 5:
                        offers.append({
                            'title': f"عرض نون: {title[:60]}",
                            'link': link if link.startswith('http') else f"https://noon.com{link}",
                            'price': price,
                            'category': 'تخفيضات',
                            'source': 'نون',
                            'image_url': image_url,
                            'description': f"احصل على {title} بسعر {price} فقط! (السعر السابق: {old_price.get_text(strip=True)})",
                            'date': datetime.now().isoformat()
                        })
            print(f"تم استخراج {len(offers)} من نون")
    except Exception as e:
        print(f"خطأ نون: {e}")
    return offers


def scrape_extra_deals():
    """سحب عروض اكسترا مع الصور"""
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
                image_el = prod.select_one('img[src]')
                
                if title_el:
                    title = title_el.get('title') or title_el.get_text(strip=True)
                    title = clean_title(title)
                    price = price_el.get_text(strip=True) if price_el else ""
                    link = link_el.get('href', '') if link_el else ""
                    image_url = ""
                    if image_el:
                        image_url = image_el.get('src', '')
                        if image_url and not image_url.startswith('http'):
                            image_url = f"https://www.extra.com{image_url}"

                    if title and len(title) > 5:
                        offers.append({
                            'title': f"عرض اكسترا: {title[:60]}",
                            'link': link if link.startswith('http') else f"https://extra.com{link}",
                            'price': price,
                            'category': 'إلكترونيات',
                            'source': 'اكسترا',
                            'image_url': image_url,
                            'description': f"عرض خاص من اكسترا على {title}. السعر الحالي: {price}",
                            'date': datetime.now().isoformat()
                        })
            print(f"تم استخراج {len(offers)} من اكسترا")
    except Exception as e:
        print(f"خطأ اكسترا: {e}")
    return offers

def scrape_cobone_deals():
    """سحب عروض المطاعم من كوبون"""
    offers = []
    try:
        print("جاري السحب من كوبون (مطاعم)...")
        # نسحب من الرياض وجدة
        urls = [
            "https://www.cobone.com/ar/deals/riyadh/food-dining",
            "https://www.cobone.com/ar/deals/jeddah/food-dining"
        ]
        
        for url in urls:
            response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                deals = soup.select('.deal-box, .deal_item')[:10]
                
                for deal in deals:
                    title_el = deal.select_one('.title, h3, h2')
                    price_el = deal.select_one('.price, .actual-price')
                    img_el = deal.select_one('img')
                    link_el = deal.select_one('a')
                    
                    if title_el and link_el:
                        title = clean_title(title_el.get_text(strip=True))
                        price = price_el.get_text(strip=True) if price_el else "خصم خاص"
                        link = link_el.get('href')
                        if link and not link.startswith('http'):
                            link = f"https://www.cobone.com{link}"
                            
                        image_url = img_el.get('data-original') or img_el.get('src') if img_el else ""
                        
                        offers.append({
                            'title': title,
                            'link': link,
                            'price': price,
                            'category': 'مطاعم',
                            'source': 'كوبون',
                            'image_url': image_url,
                            'description': f"عرض مطاعم مميز: {title} بسعر {price}",
                            'date': datetime.now().isoformat()
                        })
        print(f"تم استخراج {len(offers)} عرض مطاعم")
    except Exception as e:
        print(f"خطأ كوبون: {e}")
    return offers


def scrape_ilofo_deals():
    """سحب عروض المطاعم والقهوة (والبنوك) من موقع عروض (ilofo)"""
    offers = []
    try:
        print("جاري السحب من عروض (ilofo)...")
        # صفحة المطاعم والمقاهي (غالباً تحتوي على 1+1 وعروض القهوة)
        url = "https://www.ilofo.com/saudi/offers/restaurants"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Select offer blocks
            offer_blocks = soup.select('.col-md-3, .offer-box, .card')[:15]
            
            for block in offer_blocks:
                title_el = block.select_one('.card-title, h5, h4, a[title]')
                img_el = block.select_one('img')
                link_el = block.select_one('a')
                
                if title_el and img_el:
                    title = clean_title(title_el.get_text(strip=True))
                    image_url = img_el.get('src') or img_el.get('data-src')
                    if image_url and not image_url.startswith('http'):
                        image_url = f"https://www.ilofo.com{image_url}"
                        
                    # Filter for keywords: Bank, Free, 1+1, Coffee
                    keywords = ['مجانا', '1+1', 'بنك', 'الراجحي', 'قهوة', 'riyal', 'ريال']
                    # We take mostly everything from here as it's targeted flyers, but checking keywords helps prioritization
                    # For now, take all restaurant offers found
                    
                    details_link = link_el.get('href') if link_el else ""
                    if details_link and not details_link.startswith('http'):
                        details_link = f"https://www.ilofo.com{details_link}"
                        
                    offers.append({
                        'title': title,
                        'link': details_link or url,
                        'price': "عرض نشرة", # Flyers often have multiple prices
                        'category': 'مطاعم/بنوك',
                        'source': 'ilofo',
                        'image_url': image_url,
                        'description': f"شاهد تفاصيل العرض: {title}. قد يحتوي على عروض 1+1 أو خصومات بنكية.",
                        'date': datetime.now().isoformat()
                    })
                    
        print(f"تم استخراج {len(offers)} عرض من ilofo")
    except Exception as e:
        print(f"خطأ ilofo: {e}")
    return offers


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
    print("🔍 بدء سحب العروض (مع الصور)...")
    print("=" * 40)
    
    try:
        all_offers.extend(scrape_almowafir_deals())
    except: pass
    
    try:
        all_offers.extend(scrape_noon_deals())
    except: pass
    
    try:
        all_offers.extend(scrape_extra_deals())
    except: pass

    try:
        all_offers.extend(scrape_cobone_deals())
    except: pass

    try:
        all_offers.extend(scrape_delivery_apps())
    except: pass

    try:
        all_offers.extend(scrape_ilofo_deals())
    except: pass
    
    # إضافة العروض التجريبية إذا كان العدد قليل (للتأكد من ظهور شيء للمستخدم)
    # إذا لم توجد عروض، لا نرسل عروض تجريبية (الصدق أهم)
    if not all_offers:
        print("⚠️ لم يتم العثور على عروض جديدة حالياً.")
    
    print("=" * 40)
    print(f"✅ إجمالي العروض: {len(all_offers)}")
    print("=" * 40)
    
    return all_offers


def fetch_webpage_offers(url: str, selectors: dict):
    return []
