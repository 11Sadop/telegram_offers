import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display

# Use Noto Sans Arabic (Standard, reliable)
FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Bold.ttf"
FONT_FILE = "NotoSansArabic-Bold.ttf"

def load_arabic_font(size):
    """تحميل خط عربي بشكل آمن"""
    if not os.path.exists(FONT_FILE):
        try:
            print("Downloading Noto Sans Arabic...")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(FONT_URL, headers=headers, timeout=15)
            with open(FONT_FILE, "wb") as f:
                f.write(response.content)
            print("Font downloaded.")
        except Exception as e:
            print(f"Font download failed: {e}")
            return ImageFont.load_default()
    
    try:
        return ImageFont.truetype(FONT_FILE, size)
    except:
        return ImageFont.load_default()

def process_text(text):
    """
    معالجة النص العربي:
    1. Reshape (تشبيك الحروف)
    2. Bidi (اتجاه النص)
    """
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        return bidi_text
    except Exception as e:
        print(f"Text processing error: {e}")
        return text

def create_offer_image(image_url, title, price, store_name):
    """تصميم صورة العرض"""
    try:
        width, height = 1080, 1080
        
        # 1. الخلفية البيضاء
        img = Image.new('RGB', (width, height), '#FFFFFF')
        draw = ImageDraw.Draw(img)
        
        # 2. صورة المنتج
        if image_url:
            try:
                if not image_url.startswith('http'):
                     # Handle relative URLs just in case
                     pass
                else:
                    response = requests.get(image_url, timeout=10)
                    product_img = Image.open(BytesIO(response.content)).convert("RGBA")
                    
                    # White background for product in case it has transparency
                    bg_w, bg_h = product_img.size
                    background = Image.new('RGBA', (bg_w, bg_h), (255, 255, 255, 255))
                    product_img = Image.alpha_composite(background, product_img).convert("RGB")
                    
                    # Resize logic
                    max_h = 600
                    ratio = max_h / product_img.height
                    new_w = int(product_img.width * ratio)
                    new_h = int(product_img.height * ratio)
                    
                    if new_w > 900:
                        new_w = 900
                        ratio = new_w / product_img.width
                        new_h = int(product_img.height * ratio)
                        
                    product_img = product_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    
                    # Center paste
                    x = (width - new_w) // 2
                    y = 150 # Top margin
                    img.paste(product_img, (x, y))
            except Exception as e:
                print(f"Image error: {e}")

        # 3. النصوص
        font_title = load_arabic_font(50)
        font_price = load_arabic_font(60)
        font_store = load_arabic_font(40)
        
        # حاوية النص في الأسفل
        draw.rectangle((0, 780, width, height), fill='#F8F9FA')
        draw.line((0, 780, width, 780), fill='#DEE2E6', width=2)
        
        # العنوان
        full_title = process_text(title)
        # تقسيم بسيط اذا كان طويل جدا (يدوي لأنه textwrap لا يدعم العربي المشبك جيداً)
        # هنا سنعتمد على سطر واحد أو سطرين ونقص الزائد
        bbox = draw.textbbox((0, 0), full_title, font=font_title)
        text_w = bbox[2] - bbox[0]
        
        if text_w > 900:
            # تقريب بسيط للسطرين (يمكن تحسينه لاحقاً)
            split_idx = len(full_title) // 2
            # محاولة الايجاد مسافة
            space_idx = full_title.rfind(' ', 0, split_idx + 10)
            if space_idx > 0:
                 line1 = full_title[space_idx+1:] # Bidi reverses order usually, careful here
                 # With Bidi, the string is reversed visually. 
                 # Let's keep it simple: Just draw it centered. If it overflows, it overflows.
                 # For robustness, let's just use the full title and let it scale or center.
                 pass

        # لضمان عدم وجود مشاكل تعقيد: نكتب العنوان في المنتصف
        # Bidi text is rendered LTR logically but visually RTL.
        # draw.text expects the bidi-processed string.
        draw.text((width//2, 850), full_title, font=font_title, fill='black', anchor="mm")
        
        # السعر (يسار)
        if price:
            p_text = process_text(price)
            draw.ellipse((80, 80, 250, 250), fill='#DC3545')
            draw.text((165, 165), p_text, font=font_price, fill='white', anchor="mm")
            
        # المتجر (تحت العنوان)
        if store_name:
            store_text = process_text(f"🛍️ {store_name}")
            draw.text((width//2, 950), store_text, font=font_store, fill='#6C757D', anchor="mm")
            
        output = BytesIO()
        img.save(output, format='JPEG', quality=90)
        output.seek(0)
        return output

    except Exception as e:
        print(f"Generator Loop Error: {e}")
        return None
