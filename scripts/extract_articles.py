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
    # المنطق يعتمد على وجود رمز # متبوعاً بمسافة (العنوان الرئيسي للمقال)
    text = paragraph.text.strip()
    if not text:
        return False
    
    # التحقق من أن الفقرة تبدأ بـ # متبوعاً بمسافة
    if text.startswith('# '):
        return True
    
    return False

def save_post(title, body, idx):
    # يحفظ المقال كملف Markdown مع إضافة Front Matter.
    
    # تنظيف العنوان من رمز # ومسافاته الزائدة
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
    final_body = body.strip()
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(meta + final_body + "\n")
    print("Saved:", path)

def main():
    if not os.path.exists(INPUT):
        print(f"Error: Input file {INPUT} not found. Please ensure {INPUT} is in the repository root.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # *** التعديل الجديد: إنشاء ملف .gitkeep لضمان إرسال المجلد ***
    # هذا يضمن أن يتم تضمين مجلد posts حتى لو لم يكن يحتوي على ملفات
    pathlib.Path(os.path.join(OUTPUT_DIR, '.gitkeep')).touch()
    
    try:
        doc = Document(INPUT)
    except Exception as e:
        print(f"ERROR: Failed to open document {INPUT}. Details: {e}")
        return
        
    current_title_paragraph = None
    current_body = ""
    idx = 1
    
    # المنطق المعتمد على رموز Markdown (#)

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
            
        if is_title(p):
            # 1. إذا كان لدينا مقال سابق نحفظه قبل بدء مقال جديد
            if current_title_paragraph and current_body.strip():
                save_post(current_title_paragraph, current_body, idx)
                idx += 1
                
            # 2. نبدأ مقالاً جديداً
            current_title_paragraph = text
            current_body = ""
        else:
            # إضافة النص إلى جسم المقال الحالي
            current_body += text + "\n\n"

    # حفظ آخر مقال
    if current_title_paragraph and current_body.strip():
        save_post(current_title_paragraph, current_body, idx)
    
    if idx == 1:
        print("ERROR: No articles were successfully extracted. Ensure that every article starts with a paragraph formatted as '# Article Title' and that the file is named 'encyclopedia.docx'.")

if __name__ == "__main__":
    main()
