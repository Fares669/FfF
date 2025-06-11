import json
import os
from facebook_scraper import get_posts
from telegram import Bot

FB_PAGE = os.getenv("FB_PAGE")
TG_TOKEN = os.getenv("TG_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")
COOKIE_STRING = os.getenv("FB_COOKIES")

SEEN_FILE = "seen_posts.json"
bot = Bot(token=TG_TOKEN)

# تحميل المنشورات المرسلة سابقًا
def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

# حفظ معرفات المنشورات
def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

# تنسيق وإرسال المنشور
def send_post(post):
    date = post.get("time").strftime("%Y-%m-%d %H:%M")
    text = post.get("post_text") or post.get("text", "")
    link = post.get("post_url")
    media = post.get("image") or post.get("video")
    message = f"📅 {date}\n\n{text}\n\n🔗 {link}"

    try:
        if media:
            bot.send_photo(chat_id=CHAT_ID, photo=media, caption=message[:1024])
        else:
            bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"Telegram Error: {e}")
        if media:
            bot.send_message(chat_id=CHAT_ID, text=message + f"\n📎 {media}")
        else:
            bot.send_message(chat_id=CHAT_ID, text=message)

def main():
    seen = load_seen()
    for post in get_posts(FB_PAGE, pages=1, cookies={"cookie": COOKIE_STRING}):
        pid = post.get("post_id")
        if pid and pid not in seen:
            send_post(post)
            seen.add(pid)
            break  # فقط منشور جديد واحد
    save_seen(seen)

if __name__ == "__main__":
    main()
