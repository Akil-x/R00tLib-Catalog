"""
R00tLib Books Extractor
Extracts all books, metadata, and Telegram post links directly from the @R00tLib community.
Generates an organized, professional README.md catalog and BOOKS.json for the repository.
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
    415: "Database Systems",
    431: "Reverse Engineering & Malware Analysis",
    428: "Artificial Intelligence & Machine Learning",
    426: "3D Modeling & Game Development",
    226: "UI & UX Design",
    8: "Computer Networks & Protocols",
    410: "Cybersecurity & Ethical Hacking",
    4: "Python Programming",
    9: "Web & Application Development",
    440: "WordPress & Search Engine Optimization",
    196: "General Computer Science & Miscellaneous",
}


def parse_book_message(msg) -> dict | None:
    text = getattr(msg, "message", None) or getattr(msg, "text", "") or ""
    if not text or ("📚" not in text and "Author:" not in text and "ISBN:" not in text):
        return None

    # Title extraction
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

    # Check entities if URLs are embedded in text entities
    if getattr(msg, "entities", None):
        for ent in msg.entities:
            if isinstance(ent, MessageEntityTextUrl):
                offset = ent.offset
                length = ent.length
                anchor_text = text[offset : offset + length].lower()
                if "amazon" in anchor_text or "view" in anchor_text:
                    amazon_url = amazon_url or ent.url
                elif any(k in anchor_text for k in ["download", "free", "file"]):
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
                    elif any(k in btn_text for k in ["download", "free", "file"]):
                        download_url = download_url or btn_url

    # Topic ID & Category
    topic_id = 0
    reply_to = getattr(msg, "reply_to", None)
    if reply_to:
        topic_id = getattr(reply_to, "reply_to_top_id", None) or getattr(reply_to, "reply_to_msg_id", None) or 0

    category = TOPIC_MAP.get(topic_id, "General Computer Science & Miscellaneous")
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
        cat = b.get("category", "General Computer Science & Miscellaneous")
        categories.setdefault(cat, []).append(b)

    total_books = len(books)
    lines = [
        '<div align="center">',
        "",
        "# 📚 R00tLib Knowledge Hub",
        "",
        "**The Curated Library & Technical Index for Computer Science, Cybersecurity & Software Engineering**",
        "",
        f"[![Telegram Community](https://img.shields.io/badge/Telegram-@R00tLib-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/{COMMUNITY_USERNAME})",
        f"[![Indexed Books](https://img.shields.io/badge/Indexed_Books-{total_books}-blue?style=for-the-badge&logo=gitbook&logoColor=white)](#-categories)",
        '[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen?style=for-the-badge&logo=github)](CONTRIBUTING.md)',
        '[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)',
        "",
        "</div>",
        "",
        "---",
        "",
        "## 📖 About",
        "",
        f"Welcome to the official repository index for the **[@{COMMUNITY_USERNAME}](https://t.me/{COMMUNITY_USERNAME})** Telegram community.",
        f"This repository indexes **{total_books} high-caliber technical books**, categorized by specialization, with direct links to discussions, verified metadata, and download files hosted in our Telegram hub.",
        "",
        "---",
        "",
        "## 📑 Categories",
        "",
    ]

    for cat in sorted(categories.keys()):
        anchor = cat.lower().replace(" ", "-").replace("&", "").replace("/", "")
        lines.append(f"- [{cat}](#{anchor}) (`{len(categories[cat])}` books)")

    lines.append("\n---\n")

    for cat in sorted(categories.keys()):
        cat_books = categories[cat]
        lines.append(f"## {cat}")
        lines.append(f"*{len(cat_books)} books indexed in this category*\n")
        lines.append("| Book Title | Author | Year | ISBN | Direct Links |")
        lines.append("|:---|:---|:---:|:---:|:---:|")

        for b in sorted(cat_books, key=lambda x: x["title"].lower()):
            t = b["title"].replace("|", "/")
            a = b["author"].replace("|", "/")
            y = b["year"]
            isbn = b["isbn"]
            post = b["post_link"]

            links_col = f"[💬 View Post]({post})"
            if b.get("download_url"):
                links_col += f" &middot; [📥 Download]({b['download_url']})"
            if b.get("amazon_url"):
                links_col += f" &middot; [🛒 Amazon]({b['amazon_url']})"

            lines.append(f"| **{t}** | {a} | {y} | `{isbn}` | {links_col} |")

        lines.append("\n---\n")

    lines.extend([
        "## 🤝 Contributing",
        "",
        "Contributions are welcome! You can help expand and maintain this collection in several ways:",
        "",
        "1. **Suggest a New Book**: Open an issue or submit a Pull Request adding details to `BOOKS.json`.",
        "2. **Correct Metadata**: If an author, edition year, or ISBN is incorrect, please submit a fix.",
        "3. **Improve Tooling**: Enhancements to the extraction script or documentation are always appreciated.",
        "",
        "Please review [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.",
        "",
        "---",
        "",
        "## ⚖️ Disclaimer",
        "",
        "This repository is maintained strictly for educational, indexation, and research purposes.",
        "All trademarks, copyrights, and intellectual property belong to their respective authors and publishers.",
        "",
        "---",
        "",
        f"<div align=\"center\">Maintained with ❤️ by the <b><a href=\"https://t.me/{COMMUNITY_USERNAME}\">@{COMMUNITY_USERNAME}</a></b> Community</div>",
        "",
    ])

    return "\n".join(lines)


async def main():
    print("=" * 60)
    print(" R00tLib Books Extractor")
    print("=" * 60)

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    print("[*] Successfully connected to Telegram.")

    print(f"[*] Resolving target entity: @{COMMUNITY_USERNAME} ...")
    entity = await client.get_entity(COMMUNITY_USERNAME)
    print(f"[*] Connected to: {getattr(entity, 'title', COMMUNITY_USERNAME)}")

    print("[*] Extracting community messages and cataloging books...")
    books = []
    seen_titles = set()

    count = 0
    async for msg in client.iter_messages(entity, limit=None):
        count += 1
        if count % 100 == 0:
            print(f"[*] Scanned {count} messages... {len(books)} books found so far.")

        book = parse_book_message(msg)
        if book:
            norm_title = book["title"].lower().strip()
            if norm_title not in seen_titles:
                seen_titles.add(norm_title)
                books.append(book)

    print("\n" + "=" * 60)
    print(f"[*] Scan completed! Total messages processed: {count}")
    print(f"[*] Total unique books cataloged: {len(books)}")
    print("=" * 60)

    # Save to JSON
    json_path = "BOOKS.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    print(f"[✓] Exported dataset to: {json_path}")

    # Save to README.md
    readme_path = "README.md"
    markdown_content = generate_markdown(books)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"[✓] Successfully generated professional catalog: {readme_path}")


if __name__ == "__main__":
    asyncio.run(main())
