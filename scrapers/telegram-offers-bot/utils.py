import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display

# Fonts
FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Bold.ttf"
FONT_FILE = "NotoSansArabic-Bold.ttf"

# --- LOGO DATABASE ---
# روابط شعارات المتاجر المشهورة بدقة عالية (PNG شفاف)
STORE_LOGOS = {
    'noon': 'https://f.nooncdn.com/s/app/com/noon/images/logos/noon-black-on-yellow.svg', # Noon is tricky (SVG), let's use a PNG alternative for safety or convert
    # SVGs are hard for PIL. Let's use reliable PNG/JPG sources.
    'نون': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Noon_e-commerce_logo.svg/512px-Noon_e-commerce_logo.svg.png',
    'noon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Noon_e-commerce_logo.svg/512px-Noon_e-commerce_logo.svg.png',
    'extra': 'https://upload.wikimedia.org/wikipedia/commons/e/ec/Extra_Stores_Logo.jpg', # Solid background, will need masking or circular crop
    'اكسترا': 'https://upload.wikimedia.org/wikipedia/commons/e/ec/Extra_Stores_Logo.jpg',
    'jarir': 'https://upload.wikimedia.org/wikipedia/en/thumb/6/6f/Jarir_Bookstore_logo.svg/1200px-Jarir_Bookstore_logo.svg.png',
    'جرير': 'https://upload.wikimedia.org/wikipedia/en/thumb/6/6f/Jarir_Bookstore_logo.svg/1200px-Jarir_Bookstore_logo.svg.png',
    'amazon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Amazon_logo.svg/1024px-Amazon_logo.svg.png',
    'امازون': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Amazon_logo.svg/1024px-Amazon_logo.svg.png',
    'أمازون': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Amazon_logo.svg/1024px-Amazon_logo.svg.png',
    'starbucks': 'https://upload.wikimedia.org/wikipedia/en/thumb/d/d3/Starbucks_Corporation_Logo_2011.svg/1024px-Starbucks_Corporation_Logo_2011.svg.png',
    'ستاربكس': 'https://upload.wikimedia.org/wikipedia/en/thumb/d/d3/Starbucks_Corporation_Logo_2011.svg/1024px-Starbucks_Corporation_Logo_2011.svg.png',
    'alrajhi': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Al_Rajhi_Bank_Logo.svg/1200px-Al_Rajhi_Bank_Logo.svg.png',
    'الراجحي': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Al_Rajhi_Bank_Logo.svg/1200px-Al_Rajhi_Bank_Logo.svg.png',
    'hungerstation': 'https://play-lh.googleusercontent.com/1-f-1-f-1-f', # Placeholder logic needed? No, let's use a generic url
    'هنقرستيشن': 'https://pbs.twimg.com/profile_images/1612401938596007937/au7yL6rB_400x400.jpg',
    'almowafir': 'https://almowafir.com/wp-content/uploads/2019/11/Start-saving-money-today.png', # Generic placeholder
    'الموفر': 'https://pbs.twimg.com/profile_images/1389898950888361985/B1j27jV__400x400.jpg',
}

CATEGORY_ICONS = {
    'مطاعم': 'https://cdn-icons-png.flaticon.com/512/737/737967.png', # Burger
    'أزياء': 'https://cdn-icons-png.flaticon.com/512/3050/3050253.png', # Shirt
    'إلكترونيات': 'https://cdn-icons-png.flaticon.com/512/2983/2983799.png', # Phone
    'بنوك': 'https://cdn-icons-png.flaticon.com/512/2830/2830284.png', # Card
    'كوبونات': 'https://cdn-icons-png.flaticon.com/512/608/608933.png', # Tag
}

DEFAULT_LOGO = "https://cdn-icons-png.flaticon.com/512/1170/1170678.png" # Shopping bag

def load_arabic_font(size):
    """تحميل خط عربي"""
    if not os.path.exists(FONT_FILE):
        try:
            print("Downloading font...")
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(FONT_URL, headers=headers, timeout=15)
            with open(FONT_FILE, "wb") as f: f.write(resp.content)
        except: return ImageFont.load_default()
    try: return ImageFont.truetype(FONT_FILE, size)
    except: return ImageFont.load_default()

def process_text(text):
    if not text: return ""
    try: return get_display(arabic_reshaper.reshape(text))
    except: return text

def get_smart_logo(source, category):
    """تحديد الشعار المناسب للمصدر أو التصنيف"""
    # 1. البحث بالاسم
    if source:
        for key, url in STORE_LOGOS.items():
            if key in source.lower():
                return url
    
    # 2. البحث بالتصنيف
    if category:
        for key, url in CATEGORY_ICONS.items():
            if key in category:
                return url
                
    # 3. الافتراضي
    return DEFAULT_LOGO

def create_offer_image(image_url, title, price, store_name, category=""):
    """تصميم الصورة مع الشعار الذكي"""
    try:
        width, height = 1080, 1080
        img = Image.new('RGB', (width, height), '#FFFFFF')
        draw = ImageDraw.Draw(img)
        
        # --- الشعار الذكي (Smart Logo) ---
        logo_url = get_smart_logo(store_name, category)
        try:
            resp = requests.get(logo_url, timeout=5)
            logo = Image.open(BytesIO(resp.content)).convert("RGBA")
            
            # تحجيم الشعار
            base_w = 150
            ratio = base_w / logo.width
            h_size = int(logo.height * ratio)
            logo = logo.resize((base_w, h_size), Image.Resampling.LANCZOS)
            
            # قص دائري للشعار (اختياري، يعطي شكل أجمل)
            # mask = Image.new('L', (base_w, h_size), 0)
            # mask_draw = ImageDraw.Draw(mask)
            # mask_draw.ellipse((0, 0, base_w, h_size), fill=255)
            # logo.putalpha(mask)

            # وضعه في المنتصف بالأعلى
            logo_x = (width - base_w) // 2
            logo_y = 60
            img.paste(logo, (logo_x, logo_y), logo)
            
            content_top_margin = logo_y + h_size + 40
        except Exception as e:
            print(f"Logo fetch error: {e}")
            content_top_margin = 150

        # --- صورة المنتج ---
        if image_url:
            try:
                if image_url.startswith('http'):
                    resp = requests.get(image_url, timeout=10)
                    product_img = Image.open(BytesIO(resp.content)).convert("RGBA")
                    
                    bg_w, bg_h = product_img.size
                    background = Image.new('RGBA', (bg_w, bg_h), (255, 255, 255, 255))
                    product_img = Image.alpha_composite(background, product_img).convert("RGB")
                    
                    # Resize fit
                    available_h = 750 - content_top_margin
                    ratio = available_h / product_img.height
                    new_w = int(product_img.width * ratio)
                    new_h = int(product_img.height * ratio)
                    
                    if new_w > 900:
                        new_w = 900
                        ratio = new_w / product_img.width
                        new_h = int(product_img.height * ratio)
                    
                    product_img = product_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    
                    x = (width - new_w) // 2
                    y = content_top_margin
                    img.paste(product_img, (x, y))
            except: pass

        # --- النصوص ---
        draw.rectangle((0, 780, width, height), fill='#F8F9FA') # Gray footer
        draw.line((0, 780, width, 780), fill='#E9ECEF', width=3)
        
        font_title = load_arabic_font(50)
        font_price = load_arabic_font(55)
        font_meta = load_arabic_font(40)
        
        # العنوان (في الوسط)
        full_title = process_text(title)
        draw.text((width//2, 850), full_title, font=font_title, fill='#212529', anchor="mm")
        
        # مصدر العرض + التصنيف (أسفل العنوان)
        meta_text = process_text(f"{category} | {store_name}")
        draw.text((width//2, 920), meta_text, font=font_meta, fill='#6C757D', anchor="mm")
        
        # السعر (Tag)
        if price:
            p_text = process_text(price)
            # Tag shape
            draw.rounded_rectangle((80, 80, 280, 180), radius=20, fill='#DC3545')
            draw.text((180, 130), p_text, font=font_price, fill='white', anchor="mm")

        output = BytesIO()
        img.save(output, format='JPEG', quality=95)
        output.seek(0)
        return output

    except Exception as e:
        print(f"Gen Error: {e}")
        return None
