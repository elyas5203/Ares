# competitor_analysis.py

import instaloader
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

def get_instagram_profile_data(username, L):
    """دریافت اطلاعات یک پروفایل اینستاگرام"""
    try:
        logging.info(f"در حال دریافت اطلاعات برای پروفایل: {username}")
        profile = instaloader.Profile.from_username(L.context, username)
        return {
            "username": username,
            "followers": profile.followers,
            "followees": profile.followees,
            "posts": profile.mediacount
        }
    except Exception as e:
        logging.error(f"خطا در دریافت اطلاعات پروفایل {username}: {e}")
        return None

from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD

def run_analysis():
    """اجرای کامل فرآیند تحلیل رقبا."""

    # تحلیل وب‌سایت‌ها
    logging.info("شروع تحلیل وب‌سایت‌های رقبا...")
    website_data = []
    for url in COMPETITOR_WEBSITES:
        title = get_website_title(url)
        if title:
            website_data.append({"url": url, "title": title})

    # تحلیل اینستاگرام با لاگین
    logging.info("شروع تحلیل پروفایل‌های اینستاگرام رقبا...")
    L = instaloader.Instaloader(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        compress_json=False
    )

    is_logged_in = False
    try:
        if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
            logging.info(f"در حال لاگین به اینستاگرام با حساب کاربری: {INSTAGRAM_USERNAME}")
            try:
                L.load_session_from_file(INSTAGRAM_USERNAME)
                logging.info("لاگین از طریق سشن موفقیت‌آمیز بود.")
                is_logged_in = True
            except FileNotFoundError:
                logging.warning("فایل سشن اینستاگرام یافت نشد. تلاش برای لاگین با رمز عبور...")
                L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                L.save_session_to_file(INSTAGRAM_USERNAME)
                logging.info("لاگین با رمز عبور موفقیت‌آمیز بود و سشن ذخیره شد.")
                is_logged_in = True
        else:
            logging.warning("نام کاربری یا رمز عبور اینستاگرام در فایل config.py ارائه نشده است.")
    except Exception as e:
        logging.error(f"خطا در لاگین به اینستاگرام: {e}")

    if not is_logged_in:
        logging.error("امکان لاگین به اینستاگرام وجود ندارد. تحلیل اینستاگرام ممکن است با خطا مواجه شود.")

    instagram_data = []
    for username in COMPETITOR_INSTAGRAMS:
        profile_data = get_instagram_profile_data(username, L)
        if profile_data:
            instagram_data.append(profile_data)

    return {
        "websites": website_data,
        "instagrams": instagram_data
    }
