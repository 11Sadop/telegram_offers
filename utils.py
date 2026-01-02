import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display
import textwrap

FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Bold.ttf"
FONT_PATH = "arial_bold.ttf"  # We'll save it as this name to keep it simple or use Noto

def ensure_font_exists():
    """تحميل خط عربي متوافق اذا لم يكن موجوداً"""
    if not os.path.exists("NotoSansArabic-Bold.ttf"):
        try:
            print("Downloading font...")
            response = requests.get(FONT_URL)
            with open("NotoSansArabic-Bold.ttf", "wb") as f:
                f.write(response.content)
            print("Font downloaded.")
        except Exception as e:
            print(f"Error downloading font: {e}")

def get_font(size):
    """تحميل الخط بالحجم المطلوب"""
    ensure_font_exists()
    try:
        return ImageFont.truetype("NotoSansArabic-Bold.ttf", size)
    except:
        return ImageFont.load_default()

def process_arabic_text(text):
    """تهيئة النص العربي"""
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def wrap_text(text, width_chars):
    """تقسيم النص الطويل إلى أسطر"""
    wrapper = textwrap.TextWrapper(width=width_chars)
    word_list = wrapper.wrap(text=text)
    return word_list

def create_offer_image(image_url, title, price, store_name):
    """
    إنشاء صورة مصممة للعرض بشكل احترافي
    """
    try:
        # 1. إعداد القماش (Canvas)
        width = 1080
        height = 1080
        # خلفية بيضاء نقية
        base_image = Image.new('RGB', (width, height), '#FFFFFF')
        draw = ImageDraw.Draw(base_image)

        # 2. تحميل الخطوط
        title_font = get_font(50)
        price_font = get_font(60)
        meta_font = get_font(40)

        # 3. معالجة صورة المنتج
        if image_url:
            try:
                response = requests.get(image_url, timeout=10)
                product_img = Image.open(BytesIO(response.content))
                
                # تصغير الصورة لتناسب المساحة (60% من الارتفاع)
                target_h = 600
                ratio = target_h / product_img.height
                target_w = int(product_img.width * ratio)
                
                if target_w > 900: # Max width limit
                    target_w = 900
                    ratio = target_w / product_img.width
                    target_h = int(product_img.height * ratio)

                product_img = product_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                
                # وضع الصورة في المنتصف العلوي
                x_offset = (width - target_w) // 2
                y_offset = 100
                base_image.paste(product_img, (x_offset, y_offset))
                
            except Exception as e:
                print(f"Error loading image: {e}")

        # 4. رسم الخلفية للنص (تدرج أو لون ثابت)
        # مربع للنص في الأسفل
        draw.rectangle((0, 750, width, height), fill='#F8F9FA')
        draw.line((0, 750, width, 750), fill='#E9ECEF', width=2)

        # 5. كتابة العنوان (مع التفاف النص)
        # Reshape for Arabic logic
        title_wrapped = wrap_text(title, 40) # Character width approx
        current_h = 780
        
        for line in title_wrapped:
            line_ar = process_arabic_text(line)
            # Center text
            # bbox returns (left, top, right, bottom)
            text_bbox = draw.textbbox((0, 0), line_ar, font=title_font)
            text_w = text_bbox[2] - text_bbox[0]
            draw.text(((width - text_w) / 2, current_h), line_ar, font=title_font, fill='#212529')
            current_h += 70

        # 6. كتابة السعر في شارة مميزة
        if price:
            # دائرة/بيضاوي للسعر على الصورة
            price_text = process_arabic_text(price)
            # قياس النص
            p_bbox = draw.textbbox((0, 0), price_text, font=price_font)
            p_w = p_bbox[2] - p_bbox[0]
            
            # دائرة حمراء في الزاوية العلوية اليسرى
            circle_x = 80
            circle_y = 80
            radius = max(p_w, 100) // 2 + 20
            
            draw.ellipse((circle_x, circle_y, circle_x + radius*2, circle_y + radius*2), fill='#DC3545')
            draw.text((circle_x + radius - p_w/2, circle_y + radius - 30), price_text, font=price_font, fill='white')

        # 7. اسم المتجر
        if store_name:
            store_text = process_arabic_text(f"🛍️ {store_name}")
            s_bbox = draw.textbbox((0, 0), store_text, font=meta_font)
            s_w = s_bbox[2] - s_bbox[0]
            # أسفل الصورة
            draw.text(((width - s_w) / 2, 980), store_text, font=meta_font, fill='#6C757D')

        # حفظ
        output = BytesIO()
        base_image.save(output, format='JPEG', quality=90)
        output.seek(0)
        
        return output
    
    except Exception as e:
        print(f"Error creating image: {e}")
        return None
