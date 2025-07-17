# competitor_analysis.py

from bs4 import BeautifulSoup
import requests
import logging

# تنظیمات لاگ‌گیری
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# لیست وب‌سایت‌ها و صفحات اینستاگرام رقبا
COMPETITOR_WEBSITES = [
    "https://padidehtahrir.com/",
    "https://www.tahrireashrafi.com/",
    "https://tahrirbazar.com/",
    "https://www.bazaresefid.com/"
]

COMPETITOR_INSTAGRAMS = [
    "padidehtahrir",
    "hiva_tahrir",
    "europen_iran",
    "daftardasrak_online",
    "babakpen",
    "fountainpen1358",
    "parkerbookstore"
]

def get_website_title(url):
    """دریافت عنوان یک وب‌سایت"""
    try:
        response = requests.get(url, timeout=15, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.title.string.strip() if soup.title else "بدون عنوان"
    except requests.RequestException as e:
        logging.error(f"خطا در دسترسی به {url}: {e}")
        return None

def get_instagram_profile_data(username):
    """دریافت اطلاعات یک پروفایل اینستاگرام با استفاده از Instagram Graph API"""
    if not INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_ACCESS_TOKEN == "YOUR_ACCESS_TOKEN":
        logging.error("توکن دسترسی اینستاگرام در فایل config.py تنظیم نشده است.")
        return None

    try:
        # دریافت ID عددی کاربر
        url = f"https://graph.facebook.com/v19.0/ig_user_id?username={username}&access_token={INSTAGRAM_ACCESS_TOKEN}"
        response = requests.get(url)
        response.raise_for_status()
        user_id = response.json()["id"]

        # دریافت اطلاعات پروفایل
        url = f"https://graph.facebook.com/{user_id}?fields=username,followers_count,follows_count,media_count&access_token={INSTAGRAM_ACCESS_TOKEN}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        return {
            "username": data["username"],
            "followers": data["followers_count"],
            "followees": data["follows_count"],
            "posts": data["media_count"]
        }
    except requests.RequestException as e:
        logging.error(f"خطا در دریافت اطلاعات پروفایل {username} از طریق API: {e}")
        return None
    except KeyError:
        logging.error(f"پاسخ API برای پروفایل {username} معتبر نیست.")
        return None


def run_analysis():
    """اجرای کامل فرآیند تحلیل رقبا."""

    # تحلیل وب‌سایت‌ها
    logging.info("شروع تحلیل وب‌سایت‌های رقبا...")
    website_data = []
    for url in COMPETITOR_WEBSITES:
        title = get_website_title(url)
        if title:
            website_data.append({"url": url, "title": title})

    # # تحلیل اینستاگرام
    # logging.info("شروع تحلیل پروفایل‌های اینستاگرام رقبا...")
    # instagram_data = []
    # for username in COMPETITOR_INSTAGRAMS:
    #     profile_data = get_instagram_profile_data(username)
    #     if profile_data:
    #         instagram_data.append(profile_data)

    return {
        "websites": website_data,
        "instagrams": []
    }
