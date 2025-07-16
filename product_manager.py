# product_manager.py

from woocommerce_api import upload_image_to_wordpress, create_product_draft
import os

def handle_new_product_submission(local_image_path: str, product_name: str):
    """
    فرآیند کامل ثبت یک محصول جدید را مدیریت می‌کند:
    1. آپلود عکس به وردپرس.
    2. ایجاد پیش‌نویس محصول در ووکامرس با استفاده از عکس آپلود شده.
    """
    # مرحله ۱: آپلود عکس به وردپرس
    print("مرحله ۱: در حال آپلود تصویر به وردپرس...")
    image_id, upload_message = upload_image_to_wordpress(local_image_path, product_name)

    if not image_id:
        return {
            "success": False,
            "message": f"آپلود عکس ناموفق بود. خطا: {upload_message}",
            "edit_link": None
        }

    print(f"آپلود عکس موفقیت‌آمیز بود. شناسه عکس: {image_id}")

    # مرحله ۲: ایجاد پیش‌نویس محصول در ووکامرس
    print("مرحله ۲: در حال ایجاد پیش‌نویس محصول در ووکامرس...")
    product_data = {
        'name': product_name,
        'type': 'simple',
        'status': 'draft',  # ایجاد به صورت پیش‌نویس
        'images': [
            {'id': image_id}
        ]
    }

    result = create_product_draft(product_data)

    # در نهایت، فایل عکس موقت را پاک می‌کنیم
    try:
        os.remove(local_image_path)
        print(f"فایل موقت '{local_image_path}' با موفقیت پاک شد.")
    except OSError as e:
        print(f"خطا در پاک کردن فایل موقت: {e}")

    return result
