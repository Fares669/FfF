import os
import json
from facebook_scraper import get_posts
import requests
from datetime import datetime

FB_PAGE = os.environ["FB_PAGE"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
COOKIE_STRING = os.environ["FB_COOKIES"]

seen_file = "seen-posts.json"
log_file = "log.txt"

# نبدأ تسجيل السجل
log = []

def log_print(*args):
    msg = " ".join(str(a) for a in args)
    print(msg)
    log.append(msg)

try:
    with open(seen_file, "r") as f:
        seen = json.load(f)
except:
    seen = []

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
    log_print(f"📤 Telegram status: {response.status_code}")
    if response.status_code != 200:
        log_print("❌ Telegram error:", response.text)

def send_log_file():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(log_file, "rb") as f:
        files = {"document": f}
        data = {"chat_id": CHAT_ID, "caption": "📄 log.txt"}
        requests.post(url, data=data, files=files)

def main():
    log_print("🚀 بدء تشغيل السكربت...")
    log_print("📄 الصفحة:", FB_PAGE)

    send_to_telegram("✅ اختبار اتصال من GitHub Actions")

    for post in get_posts(FB_PAGE, pages=3, cookies=cookie_dict):
        log_print("📦 منشور جديد تم العثور عليه.")
        post_id = post["post_id"]
        if post_id in seen:
            log_print("🔁 تم إرسال هذا المنشور مسبقًا.")
            break

        timestamp = post["time"].strftime("%Y-%m-%d %H:%M") if post["time"] else "بدون تاريخ"
        text = post.get("text", "بدون وصف").strip()
        url = post.get("post_url", "")

        message = f"<b>🕓 {timestamp}</b>\n\n{text}\n\n🔗 {url}"
        send_to_telegram(message)

        seen.append(post_id)
        with open(seen_file, "w") as f:
            json.dump(seen, f)

        log_print("✅ تم إرسال المنشور.")
        break
    else:
        log_print("ℹ️ لم يتم العثور على منشورات جديدة.")

    # حفظ السجل
    with open(log_file, "w") as f:
        f.write("\n".join(log))

    # إرسال السجل
    send_log_file()

if __name__ == "__main__":
    main()