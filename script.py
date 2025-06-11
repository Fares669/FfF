import os
import json
from facebook_scraper import get_posts
import requests
from datetime import datetime

# إعدادات من متغيرات GitHub Actions
FB_PAGE = os.environ["FB_PAGE"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
COOKIE_STRING = os.environ["FB_COOKIES"]

# ملف التخزين المحلي للمنشورات المرسلة
seen_file = "seen-posts.json"

# محاولة تحميل المنشورات المرسلة مسبقًا (أو البدء بقائمة فارغة)
try:
    with open(seen_file, "r") as f:
        seen = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    seen = []

# تحويل الكوكيز من شكل "key1=val1; key2=val2" إلى dict بأمان
cookie_dict = {}
for item in COOKIE_STRING.split(";"):
    item = item.strip()
    if not item or "=" not in item:
        continue
    key, val = item.split("=", 1)
    cookie_dict[key] = val

def send_to_telegram(text, image_url=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()

def main():
    for post in get_posts(FB_PAGE, pages=1, cookies=cookie_dict):
        post_id = post["post_id"]
        if post_id in seen:
            print("🔁 تم إرسال هذا المنشور مسبقًا، يتم تخطيه.")
            return

        # تنسيق التاريخ والوصف والرابط
        timestamp = post["time"].strftime("%Y-%m-%d %H:%M") if post["time"] else "بدون تاريخ"
        text = post.get("text", "بدون وصف")
        url = post.get("post_url", "")
        media = post.get("image") or post.get("video") or ""

        message = f"<b>🕓 {timestamp}</b>\n\n{text.strip()}\n\n🔗 {url}"

        # إرسال إلى تيليجرام
        send_to_telegram(message)

        # حفظ المعرف لتفادي التكرار
        seen.append(post_id)
        with open(seen_file, "w") as f:
            json.dump(seen, f)
        print("✅ تم إرسال منشور جديد.")
        return  # نخرج بعد أول منشور جديد

if __name__ == "__main__":
    main()