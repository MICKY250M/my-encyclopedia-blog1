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
    """
    تحدد ما إذا كانت الفقرة عنوانًا محتملاً بناءً على طول الكلمات والأحرف.
    نستخدم قاعدة متساهلة هنا لأن أنماط الوورد قد تكون غير موحدة.
    (تعديل نهائي: نزيد الحد الأقصى لاستيعاب العناوين الطويلة)
    """
    word_count = len(paragraph_text.split())
    # يعتبر عنوانًا إذا كان بين 2 و 30 كلمة، وطوله أقل من 200 حرف.
    # هذا يضمن التقاط العناوين الطويلة جداً مع تجاهل الفقرات الكاملة.
    return 2 <= word_count <= 30 and len(paragraph_text) < 200

def save_post(title, body, idx):
    """
    يحفظ المقال كملف Markdown مع إضافة Front Matter.
    """
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
            # شرط الحفظ: يجب أن يكون لدينا عنوان وجسم مقال يتجاوز 50 حرفًا (للتأكد من أنه ليس عنوان مكرر أو فقرة قصيرة جدًا)
            if current_title and len(current_body.strip()) > 50:
                save_post(current_title, current_body, idx)
                idx += 1
            current_title = text
            current_body = ""
        else:
            # إضافة المحتوى إلى جسم المقال الحالي
            current_body += text + "\n\n"

    # حفظ آخر مقال بعد الانتهاء من الوثيقة
    # نستخدم شرط > 50 حرفًا مرة أخرى
    if current_title and len(current_body.strip()) > 50:
        save_post(current_title, current_body, idx)
    
    # رسالة للتحقق: إذا لم يتم حفظ أي ملف، اظهر رسالة خطأ واضحة
    if idx == 1:
        print("ERROR: No articles were successfully extracted. Check your encyclopedia.docx content format. The current rule is 2-30 words and less than 200 characters.")

if __name__ == "__main__":
    main()
