# scripts/extract_articles.py
# يعتمد على python-docx و python-slugify

from docx import Document
import os
import re
import pathlib
import slugify 

# تم تعديل هذا المسار: أصبح يشير مباشرة إلى جذر المستودع
# ***التعديل الجديد***: تم تغيير اسم الملف إلى "encyclopedia.docx" بناءً على طلب المستخدم.
INPUT = "encyclopedia.docx" 
OUTPUT_DIR = "posts"

def is_title(paragraph):
    """
    تحدد ما إذا كانت الفقرة عنوانًا محتملاً بناءً على Style الوورد.
    نبحث عن أي Style يبدأ بـ 'Heading' أو نتحقق من اسم الـStyle بشكل مباشر.
    """
    # أسماء الـStyles الشائعة للعناوين (الإنجليزية والعربية) بالإضافة إلى الأسماء الأساسية
    # ***تعديل القائمة لتشمل المزيد من الأسماء العربية***
    title_styles = [
        'Heading 1', 'Heading 2', 'Title', 
        'heading 1', 'heading 2', 
        'Heading1', 'Heading2', 'Title', 
        'Heading', 
        # الأسماء العربية الموسعة
        'عنوان 1', 'عنوان 2', 'العنوان', 
        'عنوان رئيسي', 'عنوان فرعي', 'عنوان المقال', 
        'عناوين',
        'عنوان1', 'عنوان2'
    ]
    
    style_name = paragraph.style.name.strip()
    
    # 1. التحقق من أن الـStyle يبدأ بـ 'Heading' (الطريقة الأكثر موثوقية)
    if style_name.startswith('Heading'):
        return paragraph.text.strip() != ""
        
    # 2. التحقق من المطابقة التامة للأسماء المعروفة (كخيار احتياطي)
    if style_name in title_styles:
        return paragraph.text.strip() != ""
        
    return False

def save_post(title, body, idx):
    """
    يحفظ المقال كملف Markdown مع إضافة Front Matter.
    """
    # استخدام slugify لتنظيف العنوان لاسم ملف
    slug = slugify.slugify(title)[:80]
    filename = f"{idx:04d}-{slug}.md"
    path = os.path.join(OUTPUT_DIR, filename)
    
    # الحل الجذري: استخدام ثلاث علامات اقتباس لتفادي مشاكل الهروب (\)
    clean_title = title.replace('"', "'") # نستبدل "" بـ ' لتفادي التعارض مع تنسيق YAML
    
    meta = f"""---
title: "{clean_title}"
tags: []
affiliate: "{{AFFILIATE_LINK}}"
---

"""
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(meta + body.strip() + "\n")
    print("Saved:", path)

def main():
    if not os.path.exists(INPUT):
        print(f"Error: Input file {INPUT} not found. Please ensure {INPUT} is in the repository root.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        doc = Document(INPUT)
    except Exception as e:
        print(f"ERROR: Failed to open document {INPUT}. Details: {e}")
        return
        
    current_title = None
    current_body = ""
    idx = 1

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
            
        # نمرر كائن الفقرة p للدالة is_title بدلاً من النص فقط
        if is_title(p):
            # إذا كان لدينا مقال سابق نحفظه قبل بدء مقال جديد
            if current_title and current_body.strip():
                save_post(current_title, current_body, idx)
                idx += 1
            current_title = text
            current_body = ""
        else:
            # إضافة المحتوى إلى جسم المقال الحالي
            current_body += text + "\n\n"

    # حفظ آخر مقال بعد الانتهاء من الوثيقة
    if current_title and current_body.strip():
        save_post(current_title, current_body, idx)
    
    # رسالة للتحقق: إذا لم يتم حفظ أي ملف، اظهر رسالة خطأ واضحة
    if idx == 1:
        print("ERROR: No articles were successfully extracted. Check your encyclopedia.docx content format. The current rule relies on paragraph styles starting with 'Heading' or one of the many Arabic/English standard styles.")

if __name__ == "__main__":
    main()
