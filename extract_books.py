"""
R00tLib Books Extractor
Extracts all books, metadata, and Telegram post links directly from @R00tLib community.
Generates an organized README.md catalog and BOOKS.json for the repository.
"""

import os
import re
import json
import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageEntityTextUrl

API_ID = 15551290
API_HASH = "52541a59f55c6f54678a4ec33e708e0f"
COMMUNITY_USERNAME = "R00tLib"
SESSION_NAME = "r00t_user_session"

TOPIC_MAP = {
    415: "DataBase",
    431: "Reverse Engineering",
    428: "AI & ML",
    426: "3D Modeling & Game Development",
    226: "UI / UX",
    8: "Networks",
    410: "Cybersecurity & Hack",
    4: "Python",
    9: "Web & Application Development",
    440: "Wordpress & SEO",
    196: "General & Miscellaneous",
}


def parse_book_message(msg) -> dict | None:
    text = getattr(msg, "message", None) or getattr(msg, "text", "") or ""
    if not text or ("📚" not in text and "Author:" not in text and "ISBN:" not in text):
        return None

    # Title
    title = None
    title_match = re.search(r"📚\s*[*_`]?([^\n*_`]+)[*_`]?", text)
    if title_match:
        title = title_match.group(1).strip()
    else:
        first_line = text.strip().splitlines()[0]
        title = re.sub(r"^[📚\s*_`]+", "", first_line).strip()

    if not title or len(title) < 2:
        return None

    # Author
    author = "Unknown"
    author_match = re.search(r"👤\s*[*_`]?Author:?[*_`]?\s*([^\n]+)", text, re.IGNORECASE)
    if author_match:
        author = author_match.group(1).strip().strip("*_`")

    # Year
    year = "N/A"
    year_match = re.search(r"📅\s*[*_`]?Year:?[*_`]?\s*([^\n]+)", text, re.IGNORECASE)
    if year_match:
        year = year_match.group(1).strip().strip("*_`")

    # Rating
    rating = "N/A"
    rating_match = re.search(r"⭐\s*[*_`]?Rating:?[*_`]?\s*([^\n]+)", text, re.IGNORECASE)
    if rating_match:
        rating = rating_match.group(1).strip().strip("*_`")

    # ISBN
    isbn = "N/A"
    isbn_match = re.search(r"🆔\s*[*_`]?ISBN:?[*_`]?\s*`?([^\n`]+)`?", text, re.IGNORECASE)
    if isbn_match:
        isbn = isbn_match.group(1).strip()

    # Price
    price = "N/A"
    price_match = re.search(r"💵\s*[*_`]?Price on Amazon:?[*_`]?\s*([^\n]+)", text, re.IGNORECASE)
    if price_match:
        price = price_match.group(1).strip().strip("*_`")

    # Amazon link
    amazon_url = None
    amazon_match = re.search(r"\[View on Amazon\]\((https?://[^\)]+)\)", text, re.IGNORECASE)
    if amazon_match:
        amazon_url = amazon_match.group(1)

    # Free Download link
    download_url = None
    download_match = re.search(r"\[Download File Free\]\((https?://[^\)]+)\)", text, re.IGNORECASE)
    if download_match:
        download_url = download_match.group(1)

    # Check entities if URLs are in text entities
    if getattr(msg, "entities", None):
        for ent in msg.entities:
            if isinstance(ent, MessageEntityTextUrl):
                offset = ent.offset
                length = ent.length
                anchor_text = text[offset : offset + length].lower()
                if "amazon" in anchor_text or "view" in anchor_text:
                    amazon_url = amazon_url or ent.url
                elif any(k in anchor_text for k in ["download", "free", "تحميل", "ملف"]):
                    download_url = download_url or ent.url

    # Check inline buttons
    if getattr(msg, "buttons", None):
        for row in msg.buttons:
            for btn in row:
                btn_url = getattr(btn, "url", None)
                btn_text = (getattr(btn, "text", "") or "").lower()
                if btn_url:
                    if "amazon" in btn_url.lower() or "amazon" in btn_text:
                        amazon_url = amazon_url or btn_url
                    elif any(k in btn_text for k in ["download", "free", "تحميل", "file"]):
                        download_url = download_url or btn_url

    # Topic ID & Category
    topic_id = 0
    reply_to = getattr(msg, "reply_to", None)
    if reply_to:
        topic_id = getattr(reply_to, "reply_to_top_id", None) or getattr(reply_to, "reply_to_msg_id", None) or 0

    category = TOPIC_MAP.get(topic_id, "General & Miscellaneous")
    post_link = f"https://t.me/{COMMUNITY_USERNAME}/{msg.id}"

    return {
        "id": msg.id,
        "title": title,
        "author": author,
        "year": year,
        "rating": rating,
        "isbn": isbn,
        "price": price,
        "category": category,
        "topic_id": topic_id,
        "post_link": post_link,
        "download_url": download_url,
        "amazon_url": amazon_url,
    }


def generate_markdown(books: list) -> str:
    categories = {}
    for b in books:
        cat = b.get("category", "General & Miscellaneous")
        categories.setdefault(cat, []).append(b)

    total_books = len(books)
    lines = [
        "# 📚 R00tLib Book Index & Catalog",
        "",
        f"> فهرس تفاعلي شامل لجميع كتب مجتمع **[@R00tLib](https://t.me/{COMMUNITY_USERNAME})** على تيليجرام.",
        f"> **إجمالي الكتب المفهرسة:** `{total_books}` كتاب",
        "",
        "## 📑 الفهرس السريع حسب التصنيف",
        "",
    ]

    for cat in sorted(categories.keys()):
        anchor = cat.lower().replace(" ", "-").replace("&", "").replace("/", "")
        lines.append(f"- [{cat}](#{anchor}) ({len(categories[cat])} كتاب)")

    lines.append("\n---\n")

    for cat in sorted(categories.keys()):
        cat_books = categories[cat]
        lines.append(f"## {cat}")
        lines.append(f"*عدد الكتب:* `{len(cat_books)}`\n")
        lines.append("| الكتاب | المؤلف | السنة | ISBN | رابط المنشور في تيليجرام |")
        lines.append("|---|---|---|---|:---:|")

        for b in sorted(cat_books, key=lambda x: x["title"].lower()):
            t = b["title"].replace("|", "/")
            a = b["author"].replace("|", "/")
            y = b["year"]
            isbn = b["isbn"]
            post = b["post_link"]
            download_col = f"[🔗 عرض المنشور]({post})"
            if b.get("download_url"):
                download_col += f"<br>[📥 تحميل مباشر]({b['download_url']})"
            lines.append(f"| **{t}** | {a} | {y} | `{isbn}` | {download_col} |")

        lines.append("\n---\n")

    lines.append("## 📌 نبذة وطريقة الاستخدام")
    lines.append(f"جميع الكتب متوفرة في مجتمع [@{COMMUNITY_USERNAME}](https://t.me/{COMMUNITY_USERNAME}).")
    lines.append("اضغط على أي رابط في الجدول للانتقال مباشرة إلى رسالة الكتاب وملف التحميل في تيليجرام.")
    lines.append("")

    return "\n".join(lines)


async def main():
    print("=" * 60)
    print(" 🚀 R00tLib Books Extractor")
    print("=" * 60)

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    print("\n[✓] تم تسجيل الدخول بنجاح إلى تيليجرام!")

    print(f"[*] جارٍ البحث عن المجتمع: @{COMMUNITY_USERNAME} ...")
    entity = await client.get_entity(COMMUNITY_USERNAME)
    print(f"[✓] تم الوصول للمجتمع: {getattr(entity, 'title', COMMUNITY_USERNAME)}")

    print("[*] جارٍ استخراج الرسائل وقراءة الكتب...")
    books = []
    seen_titles = set()

    count = 0
    async for msg in client.iter_messages(entity, limit=None):
        count += 1
        if count % 100 == 0:
            print(f"[*] تم فحص {count} رسالة... وجدنا {len(books)} كتاب حتى الآن.")

        book = parse_book_message(msg)
        if book:
            norm_title = book["title"].lower().strip()
            if norm_title not in seen_titles:
                seen_titles.add(norm_title)
                books.append(book)

    print("\n" + "=" * 60)
    print(f"[✓] اكتمل الفحص! إجمالي الرسائل المفحوصة: {count}")
    print(f"[✓] إجمالي الكتب المستخرجة: {len(books)} كتاب.")
    print("=" * 60)

    # Save to JSON
    json_path = "BOOKS.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    print(f"[✓] تم حفظ بيانات الكتب في: {json_path}")

    # Save to README.md
    readme_path = "README.md"
    markdown_content = generate_markdown(books)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"[✓] تم إنشاء وتحديث الفهرس في: {readme_path}")
    print("\n🎉 انتهت المهمة بنجاح!")


if __name__ == "__main__":
    asyncio.run(main())
