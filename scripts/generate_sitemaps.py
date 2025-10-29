# scripts/generate_sitemaps.py
import os
import glob
from datetime import datetime

# تم تعديل هذا المسار ليتناسب مع اسم المستخدم MICKY250M والمستودع
BASE_URL = "https://MICKY250M.github.io/my-encyclopedia-blog" 
POSTS_DIR = "posts"
MAX_URLS_PER_SITEMAP = 50000 # العدد الأقصى المسموح به لروابط في ملف سايت ماب واحد

def generate_sitemap_xml(urls, sitemap_number):
    """ينشئ ملف sitemap_N.xml لـ الروابط المحددة."""
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in urls:
        # يمكن إضافة lastmod و changefreq
        xml_content += f'<url>\n<loc>{url}</loc>\n</url>\n'
        
    xml_content += '</urlset>'
    
    filename = f"sitemap_{sitemap_number}.xml"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(xml_content)
    return filename

def generate_sitemap_index_xml(sitemap_files):
    """ينشئ ملف sitemap_index.xml يجمع كل الملفات الفرعية."""
    # استخدام التاريخ الحالي كتاريخ تحديث
    now = datetime.now().isoformat()
    index_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    index_content += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for filename in sitemap_files:
        # بناء الرابط الكامل لملف السايت ماب الفرعي
        sitemap_url = f"{BASE_URL}/{filename}"
        index_content += f'<sitemap>\n<loc>{sitemap_url}</loc>\n<lastmod>{now}</lastmod>\n</sitemap>\n'
        
    index_content += '</sitemapindex>'

    with open("sitemap_index.xml", "w", encoding="utf-8") as f:
        f.write(index_content)
    print("Generated sitemap_index.xml.")


def main():
    # التأكد من وجود مجلد المقالات (الذي ينتجه السكربت الأول)
    if not os.path.exists(POSTS_DIR):
        print(f"Error: The directory {POSTS_DIR} was not found. Run extract_articles.py first.")
        return

    markdown_files = glob.glob(os.path.join(POSTS_DIR, "*.md"))
    all_urls = []
    
    for file_path in markdown_files:
        # تحويل اسم الملف posts/0001-article-title.md إلى URL
        filename_only = os.path.basename(file_path)
        base_name = os.path.splitext(filename_only)[0]
        # نفترض أن النشر سيكون على /posts/NAME.html
        url = f"{BASE_URL}/posts/{base_name}.html" 
        all_urls.append(url)

    # تقسيم الروابط لمجموعات (للتوافق مع قيود حجم السايت ماب)
    sitemap_files = []
    num_urls = len(all_urls)
    # حساب عدد ملفات السايت ماب المطلوبة
    num_sitemaps = (num_urls + MAX_URLS_PER_SITEMAP - 1) // MAX_URLS_PER_SITEMAP
    
    for i in range(num_sitemaps):
        start = i * MAX_URLS_PER_SITEMAP
        end = start + MAX_URLS_PER_SITEMAP
        sitemap_urls = all_urls[start:end]
        
        filename = generate_sitemap_xml(sitemap_urls, i + 1)
        sitemap_files.append(filename)
        print(f"Generated {filename} with {len(sitemap_urls)} URLs.")
    
    # إنشاء ملف الفهرس الذي يشير لجميع ملفات السايت ماب الفرعية
    generate_sitemap_index_xml(sitemap_files)
    

if __name__ == "__main__":
    main()
