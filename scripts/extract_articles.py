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
    تحدد ما إذا كانت الفقرة عنوانًا محتملاً بالاعتماد على رموز Markdown (# و ##).
    نبحث عن الفقرات التي تبدأ برمز '#' أو '##' لتحديد بداية كل مقال.
    """
    text = paragraph.text.strip()
    if not text:
        return False
    
    # التحقق من أن الفقرة تبدأ برمز # متبوعاً بمسافة (العنوان الرئيسي)
    if text.startswith('# '):
        return True
    
    return False

def save_post(title, body, idx):
    """
    يحفظ المقال كملف Markdown مع إضافة Front Matter.
    """
    # العنوان سيكون هو السطر الأول بعد إزالة رمز #
    # نقوم بتنظيف العنوان من # ومسافاته الزائدة
    clean_title = title.lstrip('#').strip().replace('"', "'")
    
    # استخدام slugify لتنظيف العنوان لاسم ملف
    slug = slugify.slugify(clean_title)[:80]
    filename = f"{idx:04d}-{slug}.md"
    path = os.path.join(OUTPUT_DIR, filename)
    
    meta = f"""---
title: "{clean_title}"
tags: []
affiliate: "{{AFFILIATE_LINK}}"
---

"""
    # النص الأساسي (body) يجب أن يبدأ بعد العنوان ويحافظ على تنسيق Markdown بداخله
    # (مثل ## للترويسات الفرعية)
    
    # تأكد من أننا لا نكرر العنوان في النص الأساسي
    final_body = body.strip()
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(meta + final_body + "\n")
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
        
    current_title_paragraph = None
    current_body = ""
    idx = 1
    
    # *** المنطق المعتمد على رموز Markdown (#) ***

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
            
        if is_title(p):
            # 1. إذا كان لدينا مقال سابق نحفظه قبل بدء مقال جديد
            if current_title_paragraph and current_body.strip():
                # حفظ المقال السابق باستخدام نص العنوان السابق
                save_post(current_title_paragraph, current_body, idx)
                idx += 1
                
            # 2. نبدأ مقالاً جديداً: الفقرة الحالية هي العنوان
            current_title_paragraph = text
            current_body = ""
        else:
            # إذا لم يكن عنواناً، نضيفه إلى جسم المقال الحالي
            # مع الحفاظ على تنسيق Markdown (مثل ##)
            current_body += text + "\n\n"

    # حفظ آخر مقال بعد الانتهاء من الوثيقة
    if current_title_paragraph and current_body.strip():
        save_post(current_title_paragraph, current_body, idx)
    
    # رسالة للتحقق: إذا لم يتم حفظ أي ملف، اظهر رسالة خطأ واضحة
    if idx == 1:
        print("ERROR: No articles were successfully extracted. Ensure that every article starts with a paragraph formatted as '# Article Title' and that the file is named 'encyclopedia.docx'.")

if __name__ == "__main__":
    main()
