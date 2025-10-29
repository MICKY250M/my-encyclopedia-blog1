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
    # قاعدة بسيطة: يعتبر الفقرة عنوانًا إن عدد كلماتها بين 3 و12 وهي الفقرة نفسها بدون مسافات إضافية
    return 3 <= len(paragraph_text.split()) <= 12 and paragraph_text.strip() == paragraph_text

def save_post(title, body, idx):
    # استخدام slugify لتنظيف العنوان لاسم ملف
    slug = slugify.slugify(title)[:80]
    filename = f"{idx:04d}-{slug}.md"
    path = os.path.join(OUTPUT_DIR, filename)
    
    # السطر 25 المُسبب للمشكلة - تم تنظيفه تمامًا
meta = f"---\ntitle: \"{title.replace('"', '\\"')}\"\ntags: []\naffiliate: \"{{AFFILIATE_LINK}}\"\n---\n\n"
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
