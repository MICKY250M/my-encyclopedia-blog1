# scripts/extract_articles.py
# يعتمد على python-docx و python-slugify

from docx import Document
import os
import re
import pathlib
import slugify 

# تم تعديل هذا المسار: أصبح يشير مباشرة إلى جذر المستودع
# ***التعديل الجديد***: تم تغيير اسم الملف من "موسوعه 1.docx" إلى "encyclopedia.docx" بناءً على طلب المستخدم.
INPUT = "encyclopedia.docx" 
OUTPUT_DIR = "posts"

def is_title(paragraph):
    """
    تحدد ما إذا كانت الفقرة عنوانًا محتملاً بناءً على Style الوورد.
    نبحث عن Styles "Heading 1" أو "Heading 2" أو ما يعادلها باللغة العربية.
    """
    # أسماء الـStyles الشائعة للعناوين (الإنجليزية والعربية) بالإضافة إلى الأسماء الأساسية (بدون مسافة)
    title_styles = [
        'Heading 1', 'Heading 2', 'Title', 'عنوان 1', 'عنوان 2', 'العنوان', 
        'heading 1', 'heading 2', 
        # إضافة الأسماء الأساسية التي تستخدمها python-docx داخليًا
        'Heading1', 'Heading2', 'Title'
    ]
    
    # التحقق من أن الـStyle الخاص بالفقرة موجود ضمن قائمة العناوين
    style_name = paragraph.style.name.strip()
    return style_name in title_styles and paragraph.text.strip() != ""

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
    doc = Document(INPUT)
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
            # نتحقق فقط من وجود محتوى غير فارغ (تم إزالة شرط الـ 50 حرفاً)
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
        print("ERROR: No articles were successfully extracted. Check your encyclopedia.docx content format. The current rule relies on paragraph styles (Heading 1/2, Heading1/2).")

if __name__ == "__main__":
    main()
