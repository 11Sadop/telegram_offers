import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display

def get_font(size):
    """تحميل خط عربي افتراضي"""
    return ImageFont.load_default()

def process_arabic_text(text):
    """تهيئة النص العربي للعرض الصحيح"""
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def create_offer_image(image_url, title, price, store_name):
    """
    إنشاء صورة مصممة للعرض
    args:
        image_url: رابط صورة المنتج
        title: عنوان العرض
        price: السعر أو الخصم
        store_name: اسم المتجر
    """
    try:
        # 1. إعداد القماش (Canvas)
        width = 1080
        height = 1080
        # خلفية متدرجة بسيطة
        base_image = Image.new('RGB', (width, height), '#f8f9fa')
        draw = ImageDraw.Draw(base_image)

        # 2. تحميل صورة المنتج
        if image_url:
            try:
                response = requests.get(image_url, timeout=10)
                product_img = Image.open(BytesIO(response.content))
                
                # تغيير حجم صورة المنتج مع الحفاظ على الأبعاد
                product_img.thumbnail((900, 600))
                
                # وضع الصورة في المنتصف
                x_offset = (width - product_img.width) // 2
                base_image.paste(product_img, (x_offset, 150))
            except Exception as e:
                print(f"Error loading image: {e}")

        # 3. إضافة النصوص
        # ملاحظة: الخطوط العربية تحتاج ملف خط ttf، هنا نستخدم الافتراضي كمثال
        # في بيئة الإنتاج يفضل إضافة ملف خط عربي للمجلد
        
        # العنوان
        draw.text((width//2, 800), process_arabic_text(title), fill='black', anchor="mm")
        
        # السعر (مميز)
        if price:
            # دائرة حمراء للسعر
            draw.ellipse((850, 50, 1030, 230), fill='#dc3545')
            draw.text((940, 140), process_arabic_text(price), fill='white', anchor="mm")

        # اسم المتجر
        if store_name:
            draw.text((width//2, 900), process_arabic_text(f"من: {store_name}"), fill='gray', anchor="mm")

        # حفظ الصورة في الذاكرة
        output = BytesIO()
        base_image.save(output, format='JPEG', quality=85)
        output.seek(0)
        
        return output
    
    except Exception as e:
        print(f"Error creating image: {e}")
        return None
