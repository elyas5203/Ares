# product_manager.py

import os
import ollama
from woocommerce_api import upload_image_to_wordpress, create_product_draft, get_product_categories

def generate_product_description(product_name: str):
    """
    با استفاده از Llama 3، توضیحات محصول را تولید می‌کند.
    """
    print(f"شروع تولید توضیحات برای: {product_name}")
    prompt = f"""
    You are a creative copywriter for an online stationery shop called "Tahrirchi Shop".
    Your task is to write a compelling and friendly product description for a new item.

    Product Name: "{product_name}"

    Write a short, engaging description (around 2-3 sentences).
    Highlight its potential use or a key feature.
    Keep the tone friendly and appealing to students, artists, and office workers.
    Do not use placeholders like "[Product Name]". Instead, use the actual name.
    """
    try:
        response = ollama.chat(
            model='llama3:latest',
            messages=[{'role': 'user', 'content': prompt}]
        )
        description = response['message']['content'].strip()
        print(f"توضیحات تولید شده: {description}")
        return description
    except Exception as e:
        print(f"خطا در ارتباط با Ollama برای تولید توضیحات: {e}")
        return f"توضیحات محصول {product_name}"

def handle_new_product_submission(
    product_name: str,
    local_image_path: str = None,
    category_id: int = None,
    category_name: str = None,
    description: str = None,
    price: str = None
):
    """
    فرآیند کامل ثبت یک محصول جدید را مدیریت می‌کند.
    """
    image_id = None
    if local_image_path:
        print(f"آپلود تصویر: {local_image_path}")
        image_id, upload_message = upload_image_to_wordpress(local_image_path, product_name)
        if not image_id:
            return {"success": False, "message": f"آپلود عکس ناموفق بود. خطا: {upload_message}", "edit_link": None}
        print(f"آپلود موفقیت‌آمیز. شناسه عکس: {image_id}")

    final_description = description
    if not final_description:
        final_description = generate_product_description(product_name)

    final_category_id = category_id
    if category_name and not final_category_id:
        print(f"جستجو برای دسته‌بندی متنی: '{category_name}'")
        categories = get_product_categories()
        cat_found = next((cat for cat in categories if cat['name'].lower() == category_name.lower()), None)
        if cat_found:
            final_category_id = cat_found['id']
            print(f"دسته‌بندی متنی '{category_name}' با شناسه {final_category_id} یافت شد.")
        else:
            print(f"هشدار: دسته‌بندی متنی '{category_name}' یافت نشد.")

    print(f"ایجاد پیش‌نویس محصول با نام: {product_name}, دسته‌بندی ID: {final_category_id}")
    product_data = {
        'name': product_name,
        'type': 'simple',
        'status': 'draft',
        'description': final_description,
    }
    if price:
        product_data['regular_price'] = price
    if image_id:
        product_data['images'] = [{'id': image_id}]
    if final_category_id:
        product_data['categories'] = [{'id': final_category_id}]

    result = create_product_draft(product_data)

    if local_image_path:
        try:
            os.remove(local_image_path)
            print(f"فایل موقت '{local_image_path}' پاک شد.")
        except OSError as e:
            print(f"خطا در پاک کردن فایل موقت: {e}")

    return result
