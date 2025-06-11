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

# تحويل الكوكيز إلى dict وتجاهل الفراغات
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
    print(f"📤 Telegram response status: {response.status_code}")
    if response.status_code != 200:
        print("❌ Telegram Error:", response.text)
    response.raise_for_status()

def main():
    print("🚀 بدء تشغيل السكربت...")
    print("📄 الصفحة:", FB_PAGE)

    # 🧪 اختبار إرسال بسيط للتأكد من صلاحية البوت
    send_to_telegram("✅ اختبار اتصال من GitHub Actions")

    for post in get_posts(FB_PAGE, pages=3, cookies=cookie_dict):
        print("📦 تم العثور على منشور.")
        post_id = post["post_id"]
        if post_id in seen:
            print("🔁 تم إرسال هذا المنشور مسبقًا، يتم تخطيه.")
            return

        timestamp = post["time"].strftime("%Y-%m-%d %H:%M") if post["time"] else "بدون تاريخ"
        text = post.get("text", "بدون وصف").strip()
        url = post.get("post_url", "")

        print("📄 النص:", text)
        print("🕓 التاريخ:", timestamp)
        print("🔗 الرابط:", url)

        message = f"<b>🕓 {timestamp}</b>\n\n{text}\n\n🔗 {url}"

        send_to_telegram(message)

        # حفظ معرف المنشور لتفادي الإرسال المكرر
        seen.append(post_id)
        with open(seen_file, "w") as f:
            json.dump(seen, f)

        print("✅ تم إرسال منشور جديد.")
        return  # نخرج بعد أول منشور جديد

if __name__ == "__main__":
    main()