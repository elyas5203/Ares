import instaloader
from bs4 import BeautifulSoup
import requests
import logging
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD

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
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.title.string if soup.title else "بدون عنوان"
    except requests.RequestException as e:
        logging.error(f"خطا در دسترسی به {url}: {e}")
        return None

def get_instagram_profile_data(username, L):
    """دریافت اطلاعات یک پروفایل اینستاگرام"""
    try:
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

def run_analysis():
    """اجرای کامل فرآیند تحلیل رقبا"""

    # تحلیل وب‌سایت‌ها
    logging.info("شروع تحلیل وب‌سایت‌های رقبا...")
    website_data = []
    for url in COMPETITOR_WEBSITES:
        title = get_website_title(url)
        if title:
            website_data.append({"url": url, "title": title})

    # تحلیل اینستاگرام با لاگین
    logging.info("شروع تحلیل پروفایل‌های اینستاگرام رقبا...")
    L = instaloader.Instaloader()
    try:
        if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD and INSTAGRAM_USERNAME != "YOUR_INSTAGRAM_USERNAME":
            logging.info(f"در حال لاگین به اینستاگرام با حساب کاربری: {INSTAGRAM_USERNAME}")
            L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            logging.info("لاگین موفقیت‌آمیز بود.")
        else:
            logging.warning("نام کاربری یا رمز عبور اینستاگرام در config.py تنظیم نشده است. تحلیل بدون لاگین انجام می‌شود.")
    except Exception as e:
        logging.error(f"خطا در لاگین به اینستاگرام: {e}. تحلیل بدون لاگین ادامه می‌یابد.")

    instagram_data = []
    for username in COMPETITOR_INSTAGRAMS:
        profile_data = get_instagram_profile_data(username, L)
        if profile_data:
            instagram_data.append(profile_data)

    return {
        "websites": website_data,
        "instagrams": instagram_data
    }
