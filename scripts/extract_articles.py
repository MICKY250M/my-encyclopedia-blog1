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

def is_title(paragraph_text):
    # القاعدة الأكثر تساهلاً: يعتبر عنوانًا إذا كان أقل من 20 كلمة وليس سطرًا فارغًا.
    word_count = len(paragraph_text.split())
    # إذا كان السطر بين 1 و 20 كلمة، سنعتبره عنوانًا محتملاً. 
    # هذا يقلل من فرصة اعتبار الفقرات الطويلة كعناوين.
    return 1 < word_count <= 20 and len(paragraph_text) < 150
    
    # يجب أن يكون السطر موجودًا (أكثر من كلمتين) وأقل من 10 كلمات وأقل من 100 حرف
    return 3 <= word_count <= 10 and char_count <= 100

def save_post(title, body, idx):
    # استخدام slugify لتنظيف العنوان لاسم ملف
    slug = slugify.slugify(title)[:80]
    filename = f"{idx:04d}-{slug}.md"
    path = os.path.join(OUTPUT_DIR, filename)
    
    # الحل الجذري: استخدام ثلاث علامات اقتباس لتفادي مشاكل الهروب (\)
    # نقوم بتنظيف العنوان من أي علامات اقتباس داخليًا قبل وضعه في القالب
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
        print(f"Error: Input file {INPUT} not found. Please ensure encyclopedia.docx is in the repository root.")
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
            
        if is_title(text):
            # إذا كان لدينا مقال سابق نحفظه قبل بدء مقال جديد
            if current_title and current_body:
                save_post(current_title, current_body, idx)
                idx += 1
            current_title = text
            current_body = ""
        else:
            # إضافة المحتوى إلى جسم المقال الحالي
            current_body += text + "\n\n"

    # حفظ آخر مقال بعد الانتهاء من الوثيقة
    if current_title and current_body:
        save_post(current_title, current_body, idx)

if __name__ == "__main__":
    main()
