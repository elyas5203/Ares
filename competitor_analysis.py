# competitor_analysis.py

import requests
from bs4 import BeautifulSoup
import instaloader
import logging

# تنظیمات اولیه
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# لیست رقبا
COMPETITOR_WEBSITES = [
    "https://noline.one/",
    "https://www.ketabane.org/"
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

def scrape_website_title(url: str):
    """
    عنوان یک صفحه وب را استخراج می‌کند.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.title.string.strip() if soup.title else "عنوان یافت نشد"
    except requests.exceptions.RequestException as e:
        logging.error(f"خطا در دسترسی به وب‌سایت {url}: {e}")
        return None

def get_instagram_profile_info(username: str):
    """
    اطلاعات اولیه یک پروفایل اینستاگرام را دریافت می‌کند.
    """
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        return {
            "username": profile.username,
            "followers": profile.followers,
            "followees": profile.followees,
            "posts_count": profile.mediacount,
            "biography": profile.biography
        }
    except Exception as e:
        logging.error(f"خطا در دریافت اطلاعات پروفایل {username}: {e}")
        return None

def run_analysis():
    """
    تحلیل رقبا را اجرا کرده و نتایج را برمی‌گرداند.
    """
    analysis_results = {"websites": [], "instagrams": []}

    logging.info("شروع تحلیل وب‌سایت‌های رقبا...")
    for site in COMPETITOR_WEBSITES:
        title = scrape_website_title(site)
        if title:
            analysis_results["websites"].append({"url": site, "title": title})

    logging.info("شروع تحلیل پروفایل‌های اینستاگرام رقبا...")
    for profile_user in COMPETITOR_INSTAGRAMS:
        info = get_instagram_profile_info(profile_user)
        if info:
            analysis_results["instagrams"].append(info)

    return analysis_results

if __name__ == '__main__':
    # برای تست مستقیم این ماژول
    results = run_analysis()
    print("--- نتایج تحلیل وب‌سایت‌ها ---")
    for res in results['websites']:
        print(f"آدرس: {res['url']}, عنوان: {res['title']}")

    print("\n--- نتایج تحلیل اینستاگرام ---")
    for res in results['instagrams']:
        print(f"نام کاربری: {res['username']}, دنبال‌کننده: {res['followers']}, بیوگرافی: {res['biography'][:50]}...")
