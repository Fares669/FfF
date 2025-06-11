import os
import json
from facebook_scraper import get_posts
import requests
from datetime import datetime
import sys

# إعدادات من متغيرات GitHub Actions
FB_PAGE = os.environ["FB_PAGE"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
COOKIE_STRING = os.environ["FB_COOKIES"]

# ملفات
seen_file = "seen-posts.json"
log_file = "log.txt"

# تسجيل مخصص لكل شيء في log.txt
sys.stdout = open(log_file, "w", encoding="utf-8")
sys.stderr = sys.stdout

# تحميل المنشورات السابقة
try:
    with open(seen_file, "r") as f:
        seen = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    seen = []

# تحويل الكوكيز
cookie_dict = {}
for item in COOKIE_STRING.split(";"):
    if "=" in item:
        key, value = item.strip().split("=", 1)
        cookie_dict[key] = value

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    response = requests.post(url, data=payload)
    print(f"📤 Telegram status: {response.status_code}")
    if response.status_code != 200:
        print("❌ Telegram error:", response.text)
    response.raise_for_status()

def send_log_file():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(log_file, "rb") as f:
        files = {"document": f}
        data = {"chat_id": CHAT_ID, "caption": "📄 ملف السجل log.txt"}
        response = requests.post(url, data=data, files=files)
        print("📤 Log upload status:", response.status_code)
        if response.status_code != 200:
            print("❌ Log upload error:", response.text)

def main():
    print("🚀 بدء السكربت")
    print("📄 الصفحة:", FB_PAGE)

    send_to_telegram("✅ اختبار اتصال من GitHub Actions")

    for post in get_posts(FB_PAGE, pages=3, cookies=cookie_dict):
        print("📦 منشور تم العثور عليه")
        post_id = post["post_id"]
        if post_id in seen:
            print("🔁 تم إرسال هذا المنشور سابقًا، يتم تخطيه.")
            break

        timestamp = post["time"].strftime("%Y-%m-%d %H:%M") if post["time"] else "بدون تاريخ"
        text = post.get("text", "بدون وصف").strip()
        url = post.get("post_url", "")

        print("🕓 التاريخ:", timestamp)
        print("📄 المحتوى:", text)
        print("🔗 الرابط:", url)

        message = f"<b>🕓 {timestamp}</b>\n\n{text}\n\n🔗 {url}"
        send_to_telegram(message)

        seen.append(post_id)
        with open(seen_file, "w") as f:
            json.dump(seen, f)
        print("✅ تم إرسال منشور جديد.")
        break
    else:
        print("ℹ️ لا يوجد منشور جديد.")

    send_log_file()

if __name__ == "__main__":
    main()