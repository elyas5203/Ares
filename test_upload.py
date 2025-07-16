# test_upload.py
import os
import shutil
from product_manager import handle_new_product_submission

# --- تنظیمات ---
# نام فایل عکسی که می‌خواهید برای تست استفاده کنید.
# این فایل باید در ریشه پروژه شما (کنار این اسکریپت) قرار داشته باشد.
TEST_IMAGE_FILENAME = "my_test_photo.jpg"
PRODUCT_NAME = f"محصول تستی جدید - {TEST_IMAGE_FILENAME}"

# مسیر پوشه موقت
TEMP_IMAGE_DIR = "temp_images"
# مسیر کامل فایل در پوشه موقت
DEST_IMAGE_PATH = os.path.join(TEMP_IMAGE_DIR, TEST_IMAGE_FILENAME)

# --- اجرای تابع ---
if __name__ == "__main__":
    # 1. بررسی وجود فایل عکس اصلی
    if not os.path.exists(TEST_IMAGE_FILENAME):
        print(f"خطا: لطفاً یک فایل عکس به نام '{TEST_IMAGE_FILENAME}' در پوشه اصلی پروژه قرار دهید.")

    else:
        # 2. اطمینان از وجود پوشه temp_images
        if not os.path.exists(TEMP_IMAGE_DIR):
            os.makedirs(TEMP_IMAGE_DIR)

        # 3. کپی کردن فایل عکس به پوشه temp_images برای شبیه‌سازی فرآیند ربات
        # این کار باعث می‌شود فایل اصلی شما دست‌نخورده باقی بماند.
        shutil.copy(TEST_IMAGE_FILENAME, DEST_IMAGE_PATH)
        print(f"فایل '{TEST_IMAGE_FILENAME}' برای تست به '{DEST_IMAGE_PATH}' کپی شد.")

        print("-" * 20)
        print(f"در حال اجرای فرآیند کامل برای محصول: '{PRODUCT_NAME}'")

        # 4. فراخوانی تابع اصلی
        result = handle_new_product_submission(DEST_IMAGE_PATH, PRODUCT_NAME)

        print("-" * 20)
        # 5. نمایش نتیجه
        if result and result.get("success"):
            print("--- فرآیند با موفقیت انجام شد! ---")
            print(f"پیام: {result.get('message')}")
            print(f"لینک ویرایش پیش‌نویس محصول: {result.get('edit_link')}")
        else:
            print("--- فرآیند ناموفق بود ---")
            error_message = result.get('message') if result else "نتیجه‌ای بازگردانده نشد."
            print(f"پیام خطا: {error_message}")

        # 6. بررسی اینکه آیا فایل موقت پاک شده است یا نه
        if not os.path.exists(DEST_IMAGE_PATH):
            print(f"بررسی نهایی: فایل موقت در '{DEST_IMAGE_PATH}' با موفقیت پاک شده است.")
        else:
            # اگر فرآیند به دلیل خطا متوقف شده باشد، ممکن است فایل پاک نشده باشد.
            print(f"بررسی نهایی: فایل موقت در '{DEST_IMAGE_PATH}' هنوز وجود دارد (احتمالاً به دلیل خطا).")
