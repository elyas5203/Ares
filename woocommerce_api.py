# woocommerce_api.py

import requests
import os

# اطلاعات سایت ووکامرس شما
WC_API_URL = "https://tahrirchishop.com/wp-json/wc/v3/"
WC_CONSUMER_KEY = "ck_738bb0cc5f34a6493b51e6240ad999a764dc5f3e"
WC_CONSUMER_SECRET = "cs_aa44d5b29581d6ea928bac99cb6867b0aa85e009"


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
            json=product_data
        )
        response.raise_for_status()  # اگر خطای HTTP رخ داد، exception ایجاد می‌کند

        new_product = response.json()
        product_id = new_product.get('id')
        edit_link = f"https://tahrirchishop.com/wp-admin/post.php?post={product_id}&action=edit"

        return {
            "success": True,
            "message": f"پیش‌نویس محصول با موفقیت ایجاد شد.",
            "edit_link": edit_link
        }

    except requests.exceptions.RequestException as e:
        error_message = f"خطا در ارتباط با ووکامرس: {e}"
        if e.response is not None:
            error_message += f"\nپاسخ سرور: {e.response.text}"

        return {
            "success": False,
            "message": error_message,
            "edit_link": None
        }
