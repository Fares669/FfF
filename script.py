import os
import json
from facebook_scraper import get_posts
import requests

FB_PAGE = os.environ["FB_PAGE"]
TG_TOKEN = os.environ["TG_TOKEN"]
TG_CHAT_ID = os.environ["TG_CHAT_ID"]
FB_COOKIES = os.environ["FB_COOKIES"]

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "HTML"}
    response = requests.post(url, data=payload)
    return response.ok

def main():
    cookie_dict = {}
    for part in FB_COOKIES.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            cookie_dict[k] = v

    seen_post_file = "seen-posts.json"
    if os.path.exists(seen_post_file):
        with open(seen_post_file, "r") as f:
            seen_posts = json.load(f)
    else:
        seen_posts = []

    posts_found = False

    for post in get_posts(FB_PAGE, pages=1, cookies=cookie_dict):
        text = post.get("text", "").strip()
        post_id = post.get("post_id")
        timestamp = post.get("time")
        print(f"Found post ID {post_id} with text snippet: {text[:80]} at {timestamp}")

        if post_id in seen_posts:
            print(f"Post {post_id} already seen, skipping.")
            continue

        posts_found = True

        # Compose message
        message = f"<b>تاريخ النشر:</b> {timestamp}\n\n"
        message += f"<b>الوصف:</b>\n{text}\n\n"

        link = post.get("post_url")
        if link:
            message += f"<b>رابط المنشور:</b> {link}\n\n"

        # Send photo or video if exists
        media_urls = post.get("images") or post.get("videos") or []
        if media_urls:
            message += f"<b>الوسائط المرفقة:</b>\n"
            for url in media_urls:
                message += f"{url}\n"

        # Send message to Telegram
        sent = send_telegram_message(message)
        if sent:
            print(f"Sent post {post_id} to Telegram.")
            seen_posts.append(post_id)
            with open(seen_post_file, "w") as f:
                json.dump(seen_posts, f)
        else:
            print(f"Failed to send post {post_id}.")

    if not posts_found:
        print("No new posts found.")

if __name__ == "__main__":
    main()