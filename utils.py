import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps
import arabic_reshaper
from bidi.algorithm import get_display
import textwrap

# نستخدم خط Tajawal لأنه جميل جداً في العناوين
FONT_URL = "https://github.com/googlefonts/tajawal/raw/main/fonts/ttf/Tajawal-Bold.ttf"
FONT_PATH = "Tajawal-Bold.ttf"

def ensure_font_exists():
    """تحميل خط عربي متوافق"""
    if not os.path.exists(FONT_PATH):
        try:
            print(f"Downloading font from {FONT_URL}...")
            response = requests.get(FONT_URL, timeout=10)
            if response.status_code == 200:
                with open(FONT_PATH, "wb") as f:
                    f.write(response.content)
                print("Font downloaded successfully.")
            else:
                print(f"Failed to download font: {response.status_code}")
        except Exception as e:
            print(f"Error downloading font: {e}")

def get_font(size):
    """تحميل الخط بالحجم المطلوب مع Fallback"""
    ensure_font_exists()
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        print("Falling back to default font (Arabic might be broken)")
        return ImageFont.load_default()

def process_text(text):
    """معالجة النص العربي"""
    if not text: return ""
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except:
        return text

def wrap_text_arabic(text, width_chars):
    """تقسيم النص العربي"""
    wrapper = textwrap.TextWrapper(width=width_chars)
    # ملاحظة: التفاف النص العربي قد يتطلب مكتبة متخصصة، لكن هذا تقريب جيد
    return wrapper.wrap(text=text)

def create_offer_image(image_url, title, price, store_name):
    """
    تصميم كارت العرض (Banner Style)
    """
    try:
        # الأبعاد
        W, H = 1080, 1080
        
        # 1. الخلفية: لون موحد أنيق (Dark Blue-Grey)
        bg_color = (33, 37, 41) # #212529 nice dark color
        img = Image.new('RGB', (W, H), bg_color)
        draw = ImageDraw.Draw(img)
        
        # 2. صورة المنتج (تأخذ 65% من المساحة العلوية)
        if image_url:
            try:
                response = requests.get(image_url, timeout=10)
                product = Image.open(BytesIO(response.content)).convert("RGB")
                
                # تغيير الحجم لملء العرض والحفاظ على النسبة
                target_ratio = W / (H * 0.65)
                img_ratio = product.width / product.height
                
                if img_ratio > target_ratio:
                    # صورة عريضة
                    new_h = int(H * 0.65)
                    new_w = int(new_h * img_ratio)
                else:
                    # صورة طويلة
                    new_w = W
                    new_h = int(new_w / img_ratio)
                
                product = product.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                # القص (Center Crop)
                left = (new_w - W) // 2
                top = (new_h - int(H * 0.65)) // 2
                right = (new_w + W) // 2
                bottom = (new_h + int(H * 0.65)) // 2
                
                # إذا كانت الصورة أصغر من الخلفية، لا تقص، بل ضعها في الوسط بخلفية بيضاء
                if new_w < W or new_h < int(H * 0.65):
                    white_bg = Image.new('RGB', (W, int(H * 0.65)), (255, 255, 255))
                    # Paste centered
                    paste_x = (W - new_w) // 2
                    paste_y = (int(H * 0.65) - new_h) // 2
                    white_bg.paste(product, (paste_x, paste_y))
                    img.paste(white_bg, (0, 0))
                else:
                    # Crop logic for larger images
                    # For simplicity, let's just resize to fit width and paste top
                    product = product.resize((W, int(product.height * (W/product.width)))) 
                    img.paste(product, (0, 0))

                # Gradient Overlay at bottom of image for text readability
                # (Optional, skipped for simplicity)

            except Exception as e:
                print(f"Image load error: {e}")
                # Fallback pattern
                pass

        # 3. منطقة النص (الأسفل)
        # مربع أبيض بحواف دائرية من الأعلى
        text_area_h = int(H * 0.35)
        text_bg = Image.new('RGBA', (W, text_area_h), (255, 255, 255, 255))
        img.paste(text_bg, (0, H - text_area_h))
        
        # الخطوط
        font_title = get_font(55)
        font_meta = get_font(40)
        font_price = get_font(50)
        
        # 4. كتابة العنوان (Align Right for Arabic)
        title_ar = process_text(title)
        lines = wrap_text_arabic(title_ar, 35)
        
        # حساب مكان النص (يمين)
        start_y = H - text_area_h + 60
        padding_right = 60
        
        for line in lines[:2]: # Max 2 lines
            bbox = draw.textbbox((0, 0), line, font=font_title)
            text_w = bbox[2] - bbox[0]
            # Align Right: W - padding - text_w
            draw.text((W - padding_right - text_w, start_y), line, font=font_title, fill=(33, 37, 41))
            start_y += 80
            
        # 5. السعر والمصدر
        meta_y = H - 120
        
        # المصدر (يمين)
        if store_name:
            store_ar = process_text(f"🛍️ {store_name}")
            bbox = draw.textbbox((0, 0), store_ar, font=font_meta)
            text_w = bbox[2] - bbox[0]
            draw.text((W - padding_right - text_w, meta_y), store_ar, font=font_meta, fill=(108, 117, 125)) # Gray
            
        # السعر (يسار - مميز)
        if price:
            price_ar = process_text(price)
            # خلفية للسعر
            p_bbox = draw.textbbox((0, 0), price_ar, font=font_price)
            p_w = p_bbox[2] - p_bbox[0]
            p_h = p_bbox[3] - p_bbox[1]
            
            # Left padding
            start_x = 60
            
            # Draw tag background
            draw.rounded_rectangle(
                (start_x, meta_y - 10, start_x + p_w + 40, meta_y + p_h + 30),
                radius=15,
                fill=(220, 53, 69) # Red
            )
            
            draw.text((start_x + 20, meta_y), price_ar, font=font_price, fill=(255, 255, 255))

        # Output
        output = BytesIO()
        img.save(output, format='JPEG', quality=95)
        output.seek(0)
        return output

    except Exception as e:
        print(f"Design Error: {e}")
        return None
