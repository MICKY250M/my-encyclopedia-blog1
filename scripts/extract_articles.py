# scripts/extract_articles.py
# يعتمد على python-docx و python-slugify

from docx import Document
import os
import re
import pathlib
import slugify 

# تم تعديل هذا المسار: أصبح يشير مباشرة إلى جذر المستودع
INPUT = "encyclopedia.docx" 
OUTPUT_DIR = "posts"

def is_title(paragraph):
    """
    تحدد ما إذا كانت الفقرة عنوانًا محتملاً بناءً على طول الفقرة ووجود خط غامق (Bold).
    يُستخدم هذا المنطق عندما يكون الـStyle هو 'Normal' فقط.
    """
    text = paragraph.text.strip()
    if not text:
        return False
        
    word_count = len(text.split())
    
    # 1. العنوان يجب أن يكون قصيراً جداً (أقل من 10 كلمات)
    if word_count > 10:
        return False
        
    # 2. التحقق من وجود تنسيق Bold في الفقرة. 
    # غالباً ما يتم تمييز العناوين بالخط الغامق حتى لو كان الـStyle هو 'Normal'.
    is_bold = False
    for run in paragraph.runs:
        if run.bold:
            is_bold = True
            break
            
    # إذا كان النص قصيراً جداً وأي جزء منه غامق، نعتبره عنواناً.
    # أو إذا كان نصيراً جداً وينتهي بنقطتين (نمط الترقيم في الموسوعات).
    if is_bold or text.endswith(':') or text.endswith(':'):
        return True
        
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
    
    # المنطق البديل: الاعتماد على is_title (طول الفقرة + غامق/نقطتين) لتحديد بداية كل مقال 

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
            
        if is_title(p):
            # 1. إذا كان لدينا مقال سابق نحفظه قبل بدء مقال جديد
            if current_title and current_body.strip():
                save_post(current_title, current_body, idx)
                idx += 1
            # 2. نبدأ مقالاً جديداً بعنوان هذه الفقرة
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
        print("ERROR: No articles were successfully extracted. This suggests that the titles are not bolded or they contain more than 10 words.")

if __name__ == "__main__":
    main()
