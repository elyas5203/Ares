# woocommerce_api.py

import requests
import os

# --- اطلاعات جدید ووکامرس با دسترسی خواندن/نوشتن ---
WC_API_URL = "https://tahrirchishop.com/wp-json/wc/v3/"
WC_CONSUMER_KEY = "ck_fc708afdcf9e8794477b1866d60724891253836b"
WC_CONSUMER_SECRET = "cs_1b804cc5ff0931ae30f5c0c8c384555fb5e8696f"

# --- اطلاعات کاربری وردپرس برای آپلود رسانه ---
# این بخش بدون تغییر باقی می‌ماند
WP_USERNAME = "mtahrirchi"
WP_APPLICATION_PASSWORD = "yfC9 0w9t W5Yb wep2 sSV0 aiTh"
WP_API_URL = "https://tahrirchishop.com/wp-json/wp/v2/media"


def create_product_draft(product_data: dict):
    """
    یک محصول جدید به صورت پیش‌نویس در ووکامرس ایجاد می‌کند.
    """
    endpoint = "products"
    url = WC_API_URL + endpoint

    # همیشه محصول را به صورت پیش‌نویس (draft) ایجاد می‌کنیم
    product_data['status'] = 'draft'

    try:
        response = requests.post(
            url,
            auth=(WC_CONSUMER_KEY, WC_CONSUMER_SECRET),
            json=product_data,
            timeout=20 # افزایش زمان انتظار برای جلوگیری از تایم‌اوت
        )
        response.raise_for_status()

        new_product = response.json()
        product_id = new_product.get('id')
        edit_link = f"https://tahrirchishop.com/wp-admin/post.php?post={product_id}&action=edit"

        return {
            "success": True,
            "message": f"پیش‌نویس محصول با شناسه {product_id} با موفقیت ایجاد شد.",
            "edit_link": edit_link
        }

    except requests.exceptions.RequestException as e:
        error_message = f"خطا در ارتباط با ووکامرس: {e}"
        if e.response is not None:
            try:
                error_details = e.response.json()
                error_message += f"\nپاسخ سرور: {error_details.get('message', e.response.text)}"
            except ValueError:
                 error_message += f"\nپاسخ سرور: {e.response.text}"

        return {
            "success": False,
            "message": error_message,
            "edit_link": None
        }


def upload_image_to_wordpress(image_path: str, product_name: str):
    """
    یک عکس را در کتابخانه رسانه وردپرس آپلود می‌کند.
    """
    if not os.path.exists(image_path):
        return None, "فایل عکس یافت نشد."

    # استفاده از نام محصول برای عنوان و متن جایگزین تصویر
    file_name = os.path.basename(image_path)

    # برای جلوگیری از خطای انکدینگ با حروف فارسی در هدرها، آن‌ها را به صورت دستی UTF-8 انکد می‌کنیم.
    encoded_product_name = product_name.encode('utf-8')
    encoded_description = f'تصویر محصول {product_name}'.encode('utf-8')

    headers = {
        'Content-Disposition': f'attachment; filename={file_name}',
        'Content-Type': 'image/jpeg',
        'Title': encoded_product_name,
        'Caption': encoded_product_name,
        'Description': encoded_description
    }

    try:
        with open(image_path, 'rb') as img:
            response = requests.post(
                WP_API_URL,
                auth=(WP_USERNAME, WP_APPLICATION_PASSWORD),
                headers=headers,
                data=img,
                timeout=20
            )
        response.raise_for_status()

        media_data = response.json()
        return media_data.get('id'), "آپلود موفقیت‌آمیز بود."

    except requests.exceptions.RequestException as e:
        error_message = f"خطا در آپلود عکس: {e}"
        if e.response is not None:
            try:
                error_details = e.response.json()
                error_message += f"\nپاسخ سرور: {error_details.get('message', e.response.text)}"
            except ValueError:
                error_message += f"\nپاسخ سرور: {e.response.text}"
        return None, error_message
