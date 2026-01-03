import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# Font
FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansArabic/NotoSansArabic-Bold.ttf"
FONT_FILE = "NotoSansArabic-Bold.ttf"


def load_arabic_font(size):
    """تحميل خط عربي"""
    if not os.path.exists(FONT_FILE):
        try:
            print("⬇️ تحميل الخط...")
            resp = requests.get(FONT_URL, timeout=30)
            with open(FONT_FILE, "wb") as f:
                f.write(resp.content)
            print("✅ تم تحميل الخط")
        except Exception as e:
            print(f"❌ خطأ تحميل الخط: {e}")
            return ImageFont.load_default()
    try:
        return ImageFont.truetype(FONT_FILE, size)
    except:
        return ImageFont.load_default()


def process_text(text):
    """معالجة النص العربي"""
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except:
        return text


def create_offer_image(image_url, title, price, store_name, category=""):
    """تصميم صورة العرض"""
    try:
        # أبعاد الصورة
        width, height = 800, 600
        
        # ألوان حسب المصدر
        colors = {
            'نون': ('#FFEC00', '#000000'),      # أصفر نون
            'أمازون': ('#FF9900', '#232F3E'),   # برتقالي أمازون
            'هنقرستيشن': ('#FF5A5F', '#FFFFFF'), # أحمر
            'جاهز': ('#00C853', '#FFFFFF'),      # أخضر
            'الراجحي': ('#004D40', '#FFFFFF'),   # أخضر داكن
            'ستاربكس': ('#00704A', '#FFFFFF'),   # أخضر ستاربكس
            'STC Pay': ('#4A148C', '#FFFFFF'),   # بنفسجي
        }
        
        # اختيار اللون
        bg_color = '#1a1a2e'  # خلفية داكنة افتراضية
        text_color = '#FFFFFF'
        accent_color = '#e94560'  # أحمر وردي
        
        for key, (accent, txt) in colors.items():
            if store_name and key in store_name:
                accent_color = accent
                break
        
        # إنشاء الصورة
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # شريط علوي ملون
        draw.rectangle((0, 0, width, 100), fill=accent_color)
        
        # اسم المتجر في الأعلى
        font_store = load_arabic_font(45)
        store_text = process_text(store_name or "عرض خاص")
        draw.text((width//2, 50), store_text, font=font_store, fill='#FFFFFF', anchor="mm")
        
        # العنوان الرئيسي
        font_title = load_arabic_font(38)
        title_text = process_text(title[:60] if title else "عرض مميز")
        
        # تقسيم العنوان إذا كان طويل
        if len(title) > 30:
            words = title.split()
            mid = len(words) // 2
            line1 = ' '.join(words[:mid])
            line2 = ' '.join(words[mid:])
            draw.text((width//2, 200), process_text(line1), font=font_title, fill='#FFFFFF', anchor="mm")
            draw.text((width//2, 260), process_text(line2), font=font_title, fill='#FFFFFF', anchor="mm")
        else:
            draw.text((width//2, 230), title_text, font=font_title, fill='#FFFFFF', anchor="mm")
        
        # السعر/الخصم في دائرة
        if price:
            font_price = load_arabic_font(55)
            price_text = process_text(price)
            
            # دائرة خلف السعر
            circle_x, circle_y = width//2, 380
            circle_r = 80
            draw.ellipse((circle_x-circle_r, circle_y-circle_r, 
                         circle_x+circle_r, circle_y+circle_r), 
                        fill=accent_color)
            draw.text((circle_x, circle_y), price_text, font=font_price, fill='#FFFFFF', anchor="mm")
        
        # التصنيف في الأسفل
        font_cat = load_arabic_font(28)
        cat_text = process_text(category or "عروض")
        draw.text((width//2, 520), cat_text, font=font_cat, fill='#888888', anchor="mm")
        
        # خط فاصل
        draw.line((100, 550, width-100, 550), fill='#333333', width=2)
        
        # شعار صغير
        draw.text((width//2, 575), "🎁 عروض المواقع", font=font_cat, fill='#666666', anchor="mm")
        
        # حفظ الصورة
        output = BytesIO()
        img.save(output, format='PNG', quality=95)
        output.seek(0)
        return output
        
    except Exception as e:
        print(f"❌ خطأ تصميم الصورة: {e}")
        return None
