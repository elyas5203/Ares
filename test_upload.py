# test_upload.py
import os
from woocommerce_api import upload_image_to_wordpress

# --- تنظیمات ---
# 1. یک عکس تستی در پروژه قرار دهید.
#    برای مثال، یک پوشه به نام `temp_images` بسازید و عکسی به نام `my_test_photo.jpg` در آن قرار دهید.
IMAGE_PATH = "temp_images/my_test_photo.jpg"
PRODUCT_NAME = "خودکار آبی تست" # نام محصول برای استفاده در عنوان و متن جایگزین عکس

# --- اجرای تابع ---
if __name__ == "__main__":
    # قبل از اجرا، مطمئن شوید که فایل عکس در مسیر مشخص شده وجود دارد.
    if not os.path.exists(IMAGE_PATH):
        print(f"خطا: فایل عکس در مسیر '{IMAGE_PATH}' یافت نشد.")
        print("لطفاً یک فایل عکس در این مسیر قرار دهید و دوباره امتحان کنید.")
    else:
        print(f"در حال آپلود عکس '{IMAGE_PATH}' به وردپرس...")

        image_id, message = upload_image_to_wordpress(IMAGE_PATH, PRODUCT_NAME)

        if image_id:
            print("--- موفقیت! ---")
            print(f"پیام: {message}")
            print(f"شناسه (ID) عکس آپلود شده: {image_id}")
            print(f"می‌توانید عکس را در کتابخانه رسانه وردپرس خود مشاهده کنید.")
        else:
            print("--- خطا در آپلود ---")
            print(f"پیام خطا: {message}")
